from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget
from User_interface import *

import time
import win32gui
# from ctypes import windll
from ctypes import wintypes
import ctypes
from functools import partial
import math


'''
    多块屏幕必须符合短边完全贴合长边，不可出现交错
'''

# 区域放大
class MagnifierWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__()
        self.parent_MagniferWidget = parent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setMouseTracking(True)
        
        self.label_defaut_stylesheet = "background-color: #FFFFFF; font: 12px 'Arial'"
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
        self.label_area_diagonal = QLabel(self)
        self.label_area_diagonal_angle = QLabel(self)
        self.label_exit_method = QLabel(self)
        self.label_init(self.label_mouse_position_start)
        self.label_init(self.label_mouse_position_end)
        self.label_init(self.label_area_size)
        self.label_init(self.label_area_diagonal)
        self.label_init(self.label_area_diagonal_angle)
        self.label_init(self.label_exit_method)
        
        self.frame_label_info = QFrame(self)
        frame_layout = QVBoxLayout(self)
        frame_layout.addWidget(self.label_mouse_position_start)
        frame_layout.addWidget(self.label_mouse_position_end)
        frame_layout.addWidget(self.label_area_size)
        frame_layout.addWidget(self.label_area_diagonal)
        frame_layout.addWidget(self.label_area_diagonal_angle)
        frame_layout.addWidget(self.label_exit_method)
        self.frame_label_info.setLayout(frame_layout)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.label_magnifier)
        layout.addWidget(self.frame_label_info)
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
        # print(self.parent_MagniferWidget.mouse_position.x())
        area_rect =  QRect(self.parent_MagniferWidget.mapFromGlobal(QCursor.pos()), QSize(self.near_mouse_area_size, self.near_mouse_area_size))
        if not self.parent_MagniferWidget.mouse_position_relativ_windows:
            self.label_magnifier.hide()
            self.frame_label_info.hide()
        else:
            mouse_rect = QRect(self.parent_MagniferWidget.mouse_position_relativ_windows, QSize(self.magnifier_size, self.magnifier_size))
            self.label_magnifier.show()
            self.frame_label_info.show()
        
            # 确保放大镜窗口不会超出父窗口的边界
            # x基础范围：0 到 最大坐标减去放大镜窗口大小。 在此基础上加上原窗口相对屏幕的坐标，这就实现了在不同窗口中的约束。 y方向同理
            mouse_rect.moveTo(max(0 + self.parent_MagniferWidget.window_position_global.left, min(mouse_rect.x(), self.parent_MagniferWidget.width() - self.magnifier_size + self.parent_MagniferWidget.window_position_global.left)),
                        max(0 + self.parent_MagniferWidget.window_position_global.top, min(mouse_rect.y(), self.parent_MagniferWidget.height() - self.magnifier_size - self.frame_label_info.size().height() + self.parent_MagniferWidget.window_position_global.top)))
        
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
            self.update()
    
    # 判断左上右下的顶点位置，并更新显示
    def lefttop_rightbottom_points_display(self) -> None:
        # 默认从左上向右下移动
        # if 标签是否显示为相对坐标 == True:
            # lt = [self.parent_MagniferWidget.start_point.x(), self.parent_MagniferWidget.start_point.y()]
            # rb = [self.parent_MagniferWidget.end_point.x(), self.parent_MagniferWidget.end_point.y()]
        # else:
        lt = [self.parent_MagniferWidget.start_point_global.x(), self.parent_MagniferWidget.start_point_global.y()]
        rb = [self.parent_MagniferWidget.end_point_global.x(), self.parent_MagniferWidget.end_point_global.y()]
        self.left_move_flag = False
        self.top_move_flag = False
        if lt[0] > rb[0]:
            temp = lt[0]
            lt[0] = rb[0]
            rb[0] = temp
            self.left_move_flag = True
        if lt[1] > rb[1]:
            temp = lt[1]
            lt[1] = rb[1]
            rb[1] = temp
            self.top_move_flag = True
        diagonal = ((rb[0]-lt[0])**2 + (rb[1]-lt[1])**2)**0.5
        diagonal_str = '{:.4f}'.format(diagonal)
        angle = math.asin((rb[1]-lt[1])/diagonal)
        angle_str = '{:.4f}'.format(angle)
        angle_degree = math.degrees(angle)
        angle_degree_str = '{:.2f}'.format(angle_degree)
        self.label_mouse_position_start.setText(f'左上 [x: {lt[0]}, y: {lt[1]}]')
        self.label_mouse_position_end.setText(f'右下 [x: {rb[0]}, y: {rb[1]}]')
        self.label_area_size.setText(f'区域 [宽: {rb[0]-lt[0]}, 高: {rb[1]-lt[1]}]')
        self.label_area_diagonal.setText(f'对角线长度: {diagonal_str}')
        self.label_area_diagonal_angle.setText(f'对角线角度: {angle_str}, {angle_degree_str}°')
        self.lefttop_xy = lt
        self.rightbottom_xy = rb

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
        self.start_point_global = None
        self.end_point = None
        self.end_point_global = None
        self.mouse_position = None
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
    
    def get_active_window(self):
        rect = wintypes.RECT()
        self.window_position_global = rect
        hwnd = win32gui.GetForegroundWindow()  # 获取当前活动窗口的句柄
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        
        for screen_info in self.parent_ScreenWindow.screens_info_list:
            screen_left = screen_info['top_left_bottom_right_point'][0]
            screen_top = screen_info['top_left_bottom_right_point'][1]
            screen_right = screen_info['top_left_bottom_right_point'][2]
            screen_bottom = screen_info['top_left_bottom_right_point'][3]
            # 判断rect窗口位置，是否位于某个显示器中，故要左上大于，右下小于
            if rect.top >= screen_top and rect.left >= screen_left and rect.bottom <= screen_bottom and rect.right <= screen_right:
                # 若在某个屏幕内，则进行补偿移动
                x = rect.left + self.end_point.x()
                y = rect.top + self.end_point.y()
                self.mouse_position_relativ_windows = QPoint(x, y)
                self.magnifier.show()
                break
        else:
            # 如果当前活动窗口不在任何一个屏幕内
            self.magnifier.hide()
            self.mouse_position_relativ_windows = None

    
    # 鼠标按下事件
    def mousePressEvent(self, event) -> None:
        # 开始截图/测量
        if event.button() == Qt.LeftButton:
            self.mouse_position = event.pos()
            self.end_point = None
            self.end_point_global = None
            self.start_point = event.pos() # 起始坐标
            self.start_point_global = QCursor.pos()
            self.screenshot_times += 1
            self.magnifier.label_magnifier.show()
        # 退出截图/测量
        elif event.button() == Qt.RightButton:
            self.closed_signal.emit()
            self.widget_close()
    
    # 鼠标移动事件
    def mouseMoveEvent(self, event) -> None:
        if event.buttons() == Qt.LeftButton and self.parent_ScreenWindow.start_measure_flag:
            self.mouse_position = event.pos()
            self.end_point = event.pos()
            self.end_point_global = QCursor.pos()
            self.view.setPixmap(self.view_image) # 覆盖之前的绘制的图形
            self.get_active_window()
            self.magnifier.show()
            self.magnifier.updateMagnifier()
            self.setCursor(Qt.CrossCursor)
            self.update()
    
    # 鼠标释放事件
    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.mouse_position = event.pos()
            self.end_point = event.pos()
            self.magnifier.label_magnifier.hide()
    
    # 键盘按下事件
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.widget_close()
            self.closed_signal.emit() 
            
    
    # 关闭窗口
    def widget_close(self) -> None:
        self.parent_ScreenWindow.start_measure_flag = False
        # print(self.parent_ScreenWindow.start_measure_flag)
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
        self.ruler_in_rect_toolbar.triggered.connect(self.create_canvas)
        self.all_screen_select_menu.triggered.connect(self.action_select_screen_changed)
        for index, screen_item in enumerate(self.screens_info_list):
            action = screen_item['select_action']
            action.triggered.connect(partial(self.action_select_screen_changed)) # 这里一定要用partial
    
    def action_select_screen_changed(self):
        for index, item in enumerate(self.screen_select_menu_action_list):
            if item.isChecked():
                self.app_setting['screenshot_screen'] = index
                self.write_setting_file()
                self.screen_select_label.setText(f"当前截取：{self.screen_select_menu_action_list[self.app_setting['screenshot_screen']].text()}")
    
    def create_canvas(self) -> None:
        self.hide()
        time.sleep(0.25)
        image = self.get_screenshot()
        self.show()
        self.start_measure_flag = True
        
        # 遍历所有屏幕并创建窗口
        if self.all_screen_select_menu.isChecked():
            for index, screen in enumerate(self.all_screens):
                window = ScreenWindow(self, image[index], screen.geometry())
                window.closed_signal.connect(self.on_window_closed)
                window.show()
                self.windows.append(window)
        else:
            index = self.app_setting['screenshot_screen']
            # print(index-1)
            # print(self.all_screens)
            window = ScreenWindow(self, image[index-1], self.all_screens[index-1].geometry())
            window.closed_signal.connect(self.on_window_closed)
            window.show()
        
    def get_screenshot(self) -> list:
        self.screenshot_list = []
        for screen in self.all_screens:
            # 截取窗口
            pixmap = screen.grabWindow(0)
            self.screenshot_list.append(pixmap)
        return self.screenshot_list
    
    def on_window_closed(self) -> None:
        # 关闭其他窗口
        for window in self.windows:
            window.close()
        # self.windows = []

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
