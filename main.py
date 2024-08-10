# This is a sample Python script.
import os.path
import sys

from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QGraphicsRectItem, QLabel
from PySide6.QtGui import QPixmap, QColor, QCursor
from PySide6.QtCore import Qt, QObject, QRectF, Signal, QPoint, QCoreApplication

from ui import ColorPickerWindow
import image_reader
from image_reader import load_texture_mappings, find_closest_color
from gradient import generate_image

from PySide6.QtCore import QSettings

import copy

from PIL.ImageQt import ImageQt

from importlib import reload

import random

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

class Mixin(QObject):
    clicked = Signal(str, object)


class BlockImage(QGraphicsRectItem, Mixin):
    def __init__(self,*args, pixmap, block_path,**kwargs ):
        rect = QRectF(*args)
        self.image = pixmap
        self.active = False
        self.removed = False
        super().__init__(rect)

        self._block_path = block_path
        self.setPen(Qt.NoPen)
        self.setAcceptHoverEvents(True)
        self.popupLabel = QLabel("Popup Label")
        self.popupLabel.setStyleSheet("background-color: grey; border: 1px solid black;")
        self.popupLabel.setMinimumWidth(200)
        self.popupLabel.hide()
        self.popupLabel.setWindowFlags(Qt.ToolTip)

        self.clicked.emit(self._block_path, self)

    def paint(self, painter, option, widget):
        # Draw the rectangle
        #super().paint(painter, option, widget)
        # Draw the image inside the rectangle
        painter.drawPixmap(self.rect().toRect(), self.image)


    def __copy__(self, x,y, removed=True):
        new_inst = BlockImage(x,y, 16,16, pixmap=self.image, block_path=self._block_path)
        new_inst.removed = removed
        return new_inst









    #def setBrush(self, *args, **kwargs) -> None:
    #    if not self._initial_brush:
    #        self._initial_brush = args[0]
    #    super().setBrush(*args, **kwargs)

    def set_active(self):
        #self.setBrush(QColor("yellow"))
        self.active = True



    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:

        if event.button() == Qt.MouseButton.LeftButton:
            event.accept()
            self.clicked.emit(self._block_path, self)
            #    self.callback(self)
            #else:
            #    self.callback(self)

            #print(self.rect())

    def hoverMoveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:

        point = QCursor.pos() + QPoint(10, -10)


        self.popupLabel.setText(f"block: {os.path.basename(self._block_path)}")

        self.popupLabel.move(point)
        # self.setBrush(QColor("yellow"))

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:





        #self.setBrush(QColor("red"))

        self.popupLabel.show()

        event.accept()




    def hoverLeaveEvent(self, event:QtWidgets.QGraphicsSceneHoverEvent) -> None:
        self.setBrush(QColor("blue"))

        if self.active:
            self.setBrush(QColor("yellow"))

        self.popupLabel.hide()

        event.accept()





class GradientMapper(ColorPickerWindow):
    def __init__(self):
        super().__init__()


        self._width = 1
        self._height = 8
        self._noise = 1
        self._use_colour = False

        self.filter_list = []

        self._restore_session()

        self.pick_color_button.clicked.connect(self.draw_image)
        self.pick_color_button2.clicked.connect(self.draw_image)


        self.width_spin_box.setValue(self._width)
        self.height_spin_box.setValue(self._height)
        self.noise_spin_box.setValue(self._noise)


        self.width_spin_box.valueChanged.connect(self._set_width)
        self.height_spin_box.valueChanged.connect(self._set_height)
        self.noise_spin_box.valueChanged.connect(self._set_noise)
        self.use_col.clicked.connect(self._set_use_colour)
        self.gradient_range.valueChanged.connect(self.draw_image)



        self.draw_image()

        self.colour_changed.connect(self.draw_image)







    def _set_width(self, x):
        self._width = x
        self.draw_image()
    def _set_height(self, x):
        self._height = x
        self.draw_image()
    def _set_noise(self, x):
        self._noise = x
        self.draw_image()

    def _set_use_colour(self, x):
        self._use_colour = x
        self.draw_image()


    def match_colour(self):

        reload(image_reader)
        self._mappings = load_texture_mappings()["mappings"]
        print(len(self._mappings.keys()))

        #val = random.randint(0,255)
        col = self.picked_colour.getRgb()[:3]
        closest_image_path, closest_color = find_closest_color(col, self._mappings)


        self.color_label.setText(f"Selected Color: {self.picked_colour.name()}")
        self.color_label.setStyleSheet(f"background-color: {self.picked_colour.name()}; color: #ffffff")
        print(f"background-color: rgb{col}; color: #ffffff")
        self.color_label.setStyleSheet(f"background-color: rgb{col}; color: #ffffff")

        pixmap = QPixmap(closest_image_path)
        print(closest_image_path)

        #self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio ))
        #self.image_label.setText("")
        #self.image_label.setScaledContents(False)
        #self.image_label.setFixedSize(pixmap.size())

    def draw_image(self):

        for item in self.scene.items():
            #if isinstance(item, QGraphicsLineItem) or isinstance(item, FixedSizeTextItem):
            self.scene.removeItem(item)

        img, img_map = generate_image(self._width,
                             self._height,
                             self.picked_colour.getRgb()[:3],
                             self.picked_colour2.getRgb()[:3],
                             pos1=self.gradient_picker.pos1,
                             pos2=self.gradient_picker.pos2,
                             noise=self._noise,
                             use_colour=self._use_colour,
                             filters=tuple(self.filter_list))


        for coord, pixmap in img_map.items():

            image = BlockImage(*coord, 16, 16, **pixmap)
            image.clicked.connect(self.add_to_filter)
            self.scene.addItem(image)

        self._settings.setValue("editor/dimensions", (self._width, self._height))
        self._settings.setValue("editor/colours", (self.picked_colour, self.picked_colour2))
        self._settings.setValue("editor/ranges", (self.gradient_picker.pos1 *100, self.gradient_picker.pos2*100))
        self._settings.setValue("editor/noise_level", self._noise)
        self._settings.setValue("editor/filtered", self.filter_list)
        self._settings.sync()


    def add_to_filter(self, path, pixel_image: BlockImage = None):

        if not path in self.filter_list:
            self.filter_list.append(path)

        pos = len(self.removed_scene.items()) * 16
        if pixel_image:
            image = pixel_image.__copy__(0,pos, removed=True)
        else:
            #print("adding ", path)
            pixmap = QPixmap(path)
            image = BlockImage(0, pos, 16, 16, pixmap=pixmap, block_path=path)
            image.removed = True

        image.clicked.connect(self.remove_from_filter)
        self.removed_scene.addItem(image)
        self.draw_image()

    def remove_from_filter(self, path, pixel_image: BlockImage):
        self.filter_list.remove(path)

        for i in self.removed_scene.items():
            if i == pixel_image:
                self.removed_scene.removeItem(i)

        self.draw_image()


    def _restore_session(self):

        print("restoring")
        print(self._settings.value("editor/dimensions"))
        self._width, self._height = self._settings.value("editor/dimensions")
        self._noise = self._settings.value("editor/noise_level")
        p1, p2 = self._settings.value("editor/ranges")

        self.picked_colour, self.picked_colour2 = self._settings.value("editor/colours")


        self.width_spin_box.setValue(self._width)
        self.height_spin_box.setValue(self._height)
        self.noise_spin_box.setValue(self._noise)

        self.pick_color_button.setStyleSheet(f"background-color: {self.picked_colour.name()}; color: #ffffff")
        self.pick_color_button2.setStyleSheet(f"background-color: {self.picked_colour2.name()}; color: #ffffff")

        self.filter_list = self._settings.value("editor/filtered", [])
        for i in self.filter_list:
            self.add_to_filter(i)



        self.gradient_picker.set_colours(self.picked_colour, self.picked_colour2)
        self.gradient_range.setValue((p1, p2))

        self.draw_image()









if __name__ == "__main__":
    QCoreApplication.setOrganizationName("PixelTools")
    QCoreApplication.setOrganizationDomain("https://github.com/JLHayde")
    QCoreApplication.setApplicationName("Pixel Gradient mapper")

    app = QApplication(sys.argv)



    window = GradientMapper()
    window.show()

    sys.exit(app.exec())