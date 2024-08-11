import sys

import PySide6
from PySide6 import QtCore
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QColorDialog, QFileDialog, QVBoxLayout,
                               QWidget, QSpinBox, QCheckBox, QGraphicsScene, QGraphicsView, QGraphicsRectItem,
                               QHBoxLayout, QSizePolicy, QFormLayout, QGridLayout, QSpacerItem)
from PySide6.QtGui import QPixmap, QColor, QMouseEvent, QWheelEvent, QPainter
from PySide6.QtCore import Qt, QTimer, QObject, Signal, QRectF, QRect, QSettings
from widgets import GradientWidget, GradientRange
from superqt.sliders import QRangeSlider


class PixelGraph(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        # self.setRenderHint(QPainter.RenderHint.)
        self.setRenderHint(QPainter.TextAntialiasing)
        # self.setRenderHint(QPainter.SmoothPixmapTransform)
        # scene = QGraphicsScene(self)
        # self.setScene(scene)

        self.setSceneRect(QRect(1000, 1000, 0, 0))

        self._pan = False
        self._pan_start_x, self._pan_start_y = 0, 0

    def grab_position(self, event: QMouseEvent):
        self._pan_start_x = event.position().x()
        self._pan_start_y = event.position().y()

    def wheelEvent(self, event: QWheelEvent) -> None:
        #
        modifiers = QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.KeyboardModifier.ControlModifier:
            super().wheelEvent(event)

        else:
            zoomInFactor = 1.25
            zoomOutFactor = 1 / zoomInFactor

            # Save the scene pos
            oldPos = self.mapToScene(event.position().toPoint())

            # Zoom
            if event.angleDelta().y() > 0:
                zoomFactor = zoomInFactor
            else:
                zoomFactor = zoomOutFactor
            self.scale(zoomFactor, zoomFactor)

            # Get the new position
            newPos = self.mapToScene(event.position().toPoint())

            # Move scene to old position
            delta = newPos - oldPos
            self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        #
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan = True
            self.grab_position(event)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self._last_pan_point = event.pos()
            event.accept()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        #
        super().mouseReleaseEvent(event)

    #
    def mouseMoveEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:

        if event.buttons() == QtCore.Qt.MouseButton.MiddleButton:
            delta = event.pos() - self._last_pan_point

            print(delta)
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self._last_pan_point = event.pos()
            event.accept()

        super().mouseMoveEvent(event)


class ColorPickerWindow(QMainWindow):
    colour_changed = Signal()

    def __init__(self):
        super().__init__()

        self.picked_colour: QColor = QColor(255, 255, 255)
        self.timer = QTimer()

        self.picked_colour2: QColor = QColor(0, 0, 0)

        self._settings = QSettings()

        self._color_picker_1 = QColorDialog(self)
        # self._color_picker_1.currentColorChanged()

        self.setWindowTitle("Gradient Mapper")
        self.setGeometry(100, 100, 800, 600)

        # self.color_label = QLabel("Selected Color: None", self)
        # self.color_label.setAlignment(Qt.AlignCenter)

        # self.image_label = QLabel(self)
        # self.image_label.setAlignment(Qt.AlignCenter)
        # self.image_label.setText("No image loaded")

        self.pick_color_button = QPushButton("Pick Color", self)
        self.pick_color_button.clicked.connect(self.open_color_picker)

        self.pick_color_button2 = QPushButton("Pick Color2", self)
        self.pick_color_button2.clicked.connect(self.open_color_picker2)

        self.width_spin_box = QSpinBox(self)
        self.width_spin_box.setMinimum(0)
        self.width_spin_box.setMaximum(500)
        self.height_spin_box = QSpinBox(self)
        self.height_spin_box.setMinimum(0)
        self.height_spin_box.setMaximum(500)
        self.noise_spin_box = QSpinBox(self)
        self.use_col = QCheckBox(self)

        self.scene = QGraphicsScene()
        # self.view = PixelGraph(self.scene)
        self.image_view = PixelGraph(self.scene)

        self.removed_scene = QGraphicsScene()
        # self.view = PixelGraph(self.scene)
        self.removed_view = PixelGraph(self.removed_scene)
        self.removed_view.setSceneRect(QRect(200, 500, 0, 0))

        colour_picker_layout = QVBoxLayout()

        gradient_range_layout = QHBoxLayout()

        self.gradient_picker = GradientWidget(self.picked_colour, self.picked_colour2)
        self.gradient_range = GradientRange(Qt.Orientation.Vertical)
        self.gradient_range.setValue((0, 100))
        gradient_range_layout.addWidget(self.gradient_range)
        gradient_range_layout.addWidget(self.gradient_picker)

        self.gradient_range.valueChanged.connect(self.update_gradient)

        colour_picker_layout.addWidget(self.pick_color_button)

        colour_picker_layout.addLayout(gradient_range_layout)
        colour_picker_layout.addWidget(self.pick_color_button2)

        dimension_layout = QGridLayout()
        width_label = QLabel("X: ")
        height_label = QLabel("Y: ")
        noise_label = QLabel("Noise: ")
        show_col_label = QLabel("Show Colours: ")

        # self.width_spin_box.setMaximumWidth(100)
        # self.height_spin_box.setMaximumWidth(100)
        # self.noise_spin_box.setMaximumWidth(100)
        self.width_spin_box.setMinimumWidth(100)
        self.height_spin_box.setMinimumWidth(100)
        self.noise_spin_box.setMinimumWidth(100)

        # self.width_spin_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # self.height_spin_box.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum)
        # self.noise_spin_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # self.use_col.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        dimension_layout.addWidget(width_label, 0, 0)
        dimension_layout.addWidget(self.width_spin_box, 0, 1)
        dimension_layout.addWidget(height_label, 1, 0)
        dimension_layout.addWidget(self.height_spin_box, 1, 1)
        dimension_layout.addWidget(noise_label, 2, 0)
        dimension_layout.addWidget(self.noise_spin_box, 2, 1)
        dimension_layout.addWidget(show_col_label, 3, 0)
        dimension_layout.addWidget(self.use_col, 3, 1)

        removed_items_layout = QVBoxLayout()
        removed_items_layout.addWidget(self.removed_view)

        # self.pick_color_button.clicked.connect(self.open_color_picker)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # dimension_layout.addItem(spacer, 4,0)

        config_layout = QVBoxLayout()
        config_layout.addLayout(dimension_layout)
        config_layout.addLayout(removed_items_layout)
        # config_layout.addItem(spacer)

        # ontainer = QWidget()
        # ontainer.setLayout(main_layout)
        # elf.setCentralWidget(container)

        editor_layout = QHBoxLayout()

        editor_layout.addLayout(colour_picker_layout)

        editor_layout.addWidget(self.image_view)

        editor_layout.addLayout(config_layout)

        layout = QVBoxLayout()

        layout.addLayout(editor_layout)
        # layout.addWidget(self.color_label)
        # layout.addWidget(self.pick_color_button)
        # layout.addWidget(self.pick_color_button2)

        # layout.addWidget(self.image_label)
        # layout.addWidget(self.load_image_button)
        # layout.addWidget(self.width_spin_box)
        # layout.addWidget(self.height_spin_box)
        # layout.addWidget(self.noise_spin_box)
        # layout.addWidget(self.use_col)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def update_gradient(self, ranges):
        self.gradient_picker.set_pos1(ranges[1])
        self.gradient_picker.set_pos2(ranges[0])

    def colorChanged(self, color):
        self.pick_color_button.setStyleSheet(f"background-color: {color.name()}; color: #ffffff")
        self.picked_colour = color
        self.gradient_picker.set_colours(self.picked_colour, self.picked_colour2)
        self.colour_changed.emit()

    def colorChanged2(self, color):
        self.pick_color_button2.setStyleSheet(f"background-color: {color.name()}; color: #ffffff")
        self.picked_colour2 = color
        self.gradient_picker.set_colours(self.picked_colour, self.picked_colour2)
        self.colour_changed.emit()

    def open_color_picker(self, x):

        dialog = QColorDialog(self)
        initial_color = QColor(self.picked_colour)
        dialog.setCurrentColor(initial_color)
        dialog.currentColorChanged.connect(self.colorChanged)
        dialog.exec()



    def open_color_picker2(self, x):
        dialog = QColorDialog(self)
        initial_color = QColor(self.picked_colour2)
        dialog.setCurrentColor(initial_color)
        dialog.currentColorChanged.connect(self.colorChanged2)
        dialog.exec()
