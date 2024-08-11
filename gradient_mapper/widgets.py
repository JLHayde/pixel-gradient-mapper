import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSlider, QLabel, QVBoxLayout, QWidget, QColorDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QMouseEvent
from superqt.sliders import QRangeSlider


class GradientRange(QRangeSlider):
    """
        Gradient slider with start and end points.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.color1 = (0, 0, 255)
        self.color2 = (255, 0, 0)

    def show_color_picker(self, pos):
        color_dialog = QColorDialog(self.color, self)
        if color_dialog.exec():
            self.color = color_dialog.selectedColor()


class GradientWidget(QWidget):
    def __init__(self, colour1=None, colour2=None):
        super().__init__()
        self.color1 = colour1 if colour1 else QColor(0, 0, 255)
        self.color2 = colour2 if colour2 else QColor(255, 0, 0)
        self.pos1 = 0.0
        self.pos2 = 1.0
        self.setMinimumWidth(100)

    def set_colours(self, colour1, colour2):
        self.color1 = colour1
        self.color2 = colour2
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(self.pos1, self.color1)
        gradient.setColorAt(self.pos2, self.color2)
        brush = QBrush(gradient)
        painter.fillRect(self.rect(), brush)

    def set_pos1(self, value):
        self.pos1 = 1 - value / 100.0
        self.update()

    def set_pos2(self, value):
        self.pos2 = 1 - value / 100.0
        self.update()
