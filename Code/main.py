from PyQt5.QtGui import QMouseEvent
from User_interface import *
import keyboard
import sys
import time

class MagnifierWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        
        self.area_size = 50
        self.magnifier_faktor = 3
        self.label_mouse_position_height = 15
        self.magnifier_size = self.area_size * self.magnifier_faktor
        self.resize(self.magnifier_size, self.magnifier_size)

        self.label = QLabel(self)
        self.label_mouse_position = QLabel(self)
        # self.label_mouse_position.setContentsMargins(10,0, 0, 0)
        self.label_mouse_position.setStyleSheet("background-color: #FFFFFF")
        self.label_mouse_position.setFixedWidth(self.magnifier_size)
        self.label_mouse_position.setFixedHeight(self.label_mouse_position_height)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.label_mouse_position)
        
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    # def showEvent(self, event):
    #     self.updateMagnifier()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))  # 绘制半透明背景
        super().paintEvent(event)

    def updateMagnifier(self):
        if not self.parent():
            return

        # 获取鼠标附近的区域
        area_rect =  QRect(self.parent().mapFromGlobal(QCursor.pos()), QSize(self.area_size, self.area_size))
        mouse_rect = QRect(self.parent().mapFromGlobal(QCursor.pos()), QSize(self.magnifier_size, self.magnifier_size))
        
        # 确保放大镜窗口不会超出父窗口的边界
        # mouse_rect.moveTo(max(0, min(mouse_rect.x(), self.parent().width() - self.magnifier_size)),
        #                 max(0, min(mouse_rect.y(), self.parent().height() - self.magnifier_size)))
        self.setGeometry(mouse_rect.x(), mouse_rect.y(), mouse_rect.width(),mouse_rect.height()+self.label_mouse_position_height)
        pixmap = self.parent().grab(area_rect)
        print(pixmap)
        w = area_rect.width() * self.magnifier_faktor
        h = area_rect.height() * self.magnifier_faktor
        pixmap = pixmap.scaled(w, h, aspectRatioMode=1)
        # pixmap = pixmap.scaled(self.magnifier_size, self.magnifier_size, Qt.IgnoreAspectRatio, Qt.FastTransformation)
        # self.label.setPixmap(pixmap)
        self.label_mouse_position.setText(f'(x: {QCursor.pos().x()}, y: {QCursor.pos().y()})')


class ViewWindow(QWidget):
    closed_signal = pyqtSignal()
    def __init__(self, view_image, win_geometry):
        super().__init__()
        self.view_image = view_image
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(win_geometry)  # 设置窗口位置和大小
        self.view = QLabel(self)
        self.view.setPixmap(self.view_image)
        self.start_point = None
        self.end_point = None
        self.temp_pixmap = QPixmap(view_image.size())
        self.magnifier = MagnifierWidget(self)
    
    def paintEvent(self, event):
        painter = QPainter(self.view.pixmap())
        painter.fillRect(self.view.pixmap().rect(), QColor(0, 0, 0, 0)) 
        if self.start_point and self.end_point:
            start_x = min(self.start_point.x(), self.end_point.x())
            start_y = min(self.start_point.y(), self.end_point.y())
            width = abs(self.end_point.x() - self.start_point.x())
            height = abs(self.end_point.y() - self.start_point.y())
            painter.setPen(QColor(255, 0, 0))  # 设置画笔颜色为红色
            painter.setBrush(QColor(0, 0, 0, 0))  # 设置填充颜色为透明
            painter.drawRect(start_x, start_y, width, height)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            print('左键按下')
        elif event.button() == Qt.RightButton:
            self.closed_signal.emit()  # 发射关闭信号
            self.close()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.end_point = event.pos()
            self.update()
            self.view.setPixmap(self.view_image) # 覆盖之前的绘制的图形
            self.magnifier.show()
            self.magnifier.updateMagnifier()
    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.RightButton:
            self.end_point = event.pos()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.closed_signal.emit()  # 发射关闭信号
            self.close()

class Main(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.connection()
        self.windows = []
    
    def connection(self):
        self.screenshot_toolbar.triggered.connect(self.create_canvas)
    
    def create_canvas(self):
        self.hide()
        time.sleep(0.2)
        image = self.get_screenshot()
        self.show()
        # 遍历所有屏幕创建窗口
        for index in range(len(self.screen_size_all)):
            window = ViewWindow(image[index], self.screen_size_all[index].geometry())
            window.closed_signal.connect(self.on_window_closed)
            window.show()
            self.windows.append(window)
        
    def get_screenshot(self):
        temp_screenshots_list = []
        for screen in self.screen_size_all:
            # 截取窗口
            pixmap = screen.grabWindow(0)
            temp_screenshots_list.append(pixmap)
        return temp_screenshots_list
    
    def on_window_closed(self):
        # 关闭其他窗口
        for window in self.windows:
            window.close()
    



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())