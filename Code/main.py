from PyQt5.QtGui import QCloseEvent, QMouseEvent
from User_interface import *
import keyboard
import sys
import time
import win32gui

# 区域放大
class MagnifierWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__()
        self.parent_MagniferWidget = parent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setMouseTracking(True)
        
        self.label_defaut_stylesheet = "background-color: #FFFFFF"
        self.near_mouse_area_size = 50 # 设置截取鼠标附近的区域大小
        self.magnifier_faktor = 3   # 设置放大倍数
        self.label_mouse_position_height = 15   # 设置显示像素大小标签高度
        self.spaceritem_height = 5 # 垂直弹簧高度
        self.magnifier_size = self.near_mouse_area_size * self.magnifier_faktor # 放大镜大小为 区域大小*放大倍数
        self.resize(self.magnifier_size, self.magnifier_size)
        
        self.spacer_item = QSpacerItem(self.magnifier_size, self.spaceritem_height, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.label_magnifier = QLabel(self)
        self.label_mouse_position_start = QLabel(self)
        self.label_mouse_position_end = QLabel(self)
        self.label_area_size = QLabel(self)
        self.label_exit_method = QLabel(self)
        self.label_init(self.label_mouse_position_start)
        self.label_init(self.label_mouse_position_end)
        self.label_init(self.label_area_size)
        self.label_init(self.label_exit_method)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.label_magnifier)
        layout.addWidget(self.label_mouse_position_start)
        layout.addWidget(self.label_mouse_position_end)
        layout.addWidget(self.label_area_size)
        layout.addWidget(self.label_exit_method)
        layout.addItem(self.spacer_item)
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
    
    def label_init(self, label_element: QLabel, stylesheet:str = None) -> None:
        if not stylesheet:
            stylesheet = self.label_defaut_stylesheet
        label_element.setStyleSheet(stylesheet)
        label_element.setFixedWidth(self.magnifier_size)
        label_element.setFixedHeight(self.label_mouse_position_height)

    def updateMagnifier(self) -> None:
        if not self.parent_MagniferWidget:
            return
        # 获取鼠标附近的区域
        area_rect =  QRect(self.parent_MagniferWidget.mapFromGlobal(QCursor.pos()), QSize(self.near_mouse_area_size, self.near_mouse_area_size))
        mouse_rect = QRect(self.parent_MagniferWidget.mapFromGlobal(QCursor.pos()), QSize(self.magnifier_size, self.magnifier_size))
        # 确保放大镜窗口不会超出父窗口的边界
        mouse_rect.moveTo(max(0, min(mouse_rect.x(), self.parent_MagniferWidget.width() - self.magnifier_size)),
                        max(0, min(mouse_rect.y(), self.parent_MagniferWidget.height() - self.magnifier_size)))
        
        self.setGeometry(mouse_rect.x(), mouse_rect.y(), mouse_rect.width(),mouse_rect.height()+self.label_mouse_position_height)
        pixmap = self.parent_MagniferWidget.grab(area_rect)
        w = area_rect.width() * self.magnifier_faktor
        h = area_rect.height() * self.magnifier_faktor
        pixmap = pixmap.scaled(w, h, aspectRatioMode=Qt.KeepAspectRatioByExpanding)
        self.label_magnifier.setPixmap(pixmap)
        self.lefttop_rightbottom_points_display()
        if self.parent_MagniferWidget.screenshot_times > 1:
            self.label_exit_method.setText('单击鼠标右键 或 按Esc退出')
        else: self.label_exit_method.setText('单击鼠标')
        self.get_active_window_title()
        self.update()
    
    # 判断左上右下的顶点位置，并更新显示
    def lefttop_rightbottom_points_display(self) -> None:
        lt = [self.parent_MagniferWidget.start_point.x(), self.parent_MagniferWidget.start_point.y()]
        rb = [self.parent_MagniferWidget.end_point.x(), self.parent_MagniferWidget.end_point.y()]
        if lt[0] > rb[0]:
            temp = lt[0]
            lt[0] = rb[0]
            rb[0] = temp
        if lt[1] > rb[1]:
            temp = lt[1]
            lt[1] = rb[1]
            rb[1] = temp
        self.label_mouse_position_start.setText(f'左上 [x: {lt[0]}, y: {lt[1]}]')
        self.label_mouse_position_end.setText(f'右下 [x: {rb[0]}, y: {rb[1]}]')
        self.label_area_size.setText(f'区域 [宽: {rb[0]-lt[0]}, 高: {rb[1]-lt[1]}]')
    
    def get_active_window_title(self):
        hwnd = win32gui.GetForegroundWindow()  # 获取当前活动窗口的句柄
        title = win32gui.GetWindowText(hwnd)  # 获取窗口标题
        print(hwnd)
        print(title)
    
    # def showEvent(self, event):
    #     super().showEvent(event)
    #     widget_list = self.parent_MagniferWidget.parent_ScreenWindow.screenshot_list
    #     for i in widget_list:
    #         if i.activ():
    #             print('0000000')
        # screen = QApplication.desktop().screen(QCursor().pos())
        # if screen:
        #     screen_rect = screen.availableGeometry()
        #     self.move(screen_rect.left(), screen_rect.top())
        
class ScreenWindow(QWidget):
    closed_signal = pyqtSignal()
    def __init__(self, parent, view_image, win_geometry) -> None:
        super().__init__()
        self.view_image = view_image
        self.parent_ScreenWindow = parent
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(win_geometry)  # 设置窗口位置和大小
        self.view = QLabel(self)
        self.view.setPixmap(self.view_image)
        self.start_point = None
        self.end_point = None
        self.screenshot_times = 0
        self.temp_pixmap = QPixmap(view_image.size())
        self.magnifier = MagnifierWidget(self)
        
    
    def paintEvent(self, event) -> None:
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
    
    # 鼠标按下事件
    def mousePressEvent(self, event) -> None:
        # 开始截图/测量
        if event.button() == Qt.LeftButton:
            self.end_point = None
            self.start_point = event.pos() # 起始坐标
            self.screenshot_times += 1
            self.magnifier.label_magnifier.show()
        # 退出截图/测量
        elif event.button() == Qt.RightButton:
            self.closed_signal.emit()
            self.widget_close()
    
    # 鼠标移动事件
    def mouseMoveEvent(self, event) -> None:
        if event.buttons() == Qt.LeftButton:
            self.end_point = event.pos()
            self.view.setPixmap(self.view_image) # 覆盖之前的绘制的图形
            self.magnifier.show()
            self.magnifier.updateMagnifier()
            self.setCursor(Qt.CrossCursor)
            self.update()
    
    # 鼠标释放事件
    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            self.magnifier.label_magnifier.hide()
    
    # 键盘按下事件
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.widget_close()
            self.closed_signal.emit() 
    
    # 关闭窗口
    def widget_close(self) -> None:
        self.magnifier.close()
        self.close()
    
    def closeEvent(self, event: QCloseEvent):
        self.widget_close()
        return super().closeEvent(event)

# 主程序
class Main(Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.connection()
        self.windows = []
    
    def connection(self) -> None:
        self.screenshot_toolbar.triggered.connect(self.create_canvas)
    
    def create_canvas(self) -> None:
        self.hide()
        time.sleep(0.2)
        image = self.get_screenshot()
        self.show()
        
        # 遍历所有屏幕创建窗口
        for index in range(len(self.screen_size_all)):
            window = ScreenWindow(self, image[index], self.screen_size_all[index].geometry())
            window.closed_signal.connect(self.on_window_closed)
            window.show()
            self.windows.append(window)
        
    def get_screenshot(self) -> list:
        self.screenshot_list = []
        for screen in self.screen_size_all:
            # 截取窗口
            pixmap = screen.grabWindow(0)
            self.screenshot_list.append(pixmap)
        return self.screenshot_list
    
    def on_window_closed(self) -> None:
        # 关闭其他窗口
        for window in self.windows:
            window.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())