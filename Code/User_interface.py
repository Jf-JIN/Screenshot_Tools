from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QToolBar, QStatusBar, QLabel, QAction, QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QFrame, QActionGroup
from PyQt5.QtGui import QPixmap, QIcon, QCursor, QFont,QPainter, QColor
from PyQt5.QtCore import Qt, QByteArray, QObject, QEvent, pyqtSignal, QRect, QSize, QPoint
from Icon_svg import *
# from os import path as opath
# from os import environ as oenviron
import os
import json


class WinEventFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Move or event.type() ==QEvent.Resize or event.type() ==QEvent.MouseMove:
            if isinstance(obj, QMainWindow):
                win_geometry = obj.geometry()
                global_pos = QCursor.pos()
                obj.statusbar_win_mouse.showMessage(f"窗口位置:({win_geometry.x()}, {win_geometry.y()}), 窗口宽高：({win_geometry.width()}, {win_geometry.height()}), 鼠标位置:({global_pos.x()},{global_pos.y()})")
        return super().eventFilter(obj, event)

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.parameter_init()
        self.ui_init()
        self.menubar_init()
        self.toolbar_init()
        self.statusbar_init()
        self.event_filter = WinEventFilter()
        self.installEventFilter(self.event_filter)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        # self.connections_Ui_MainWindow()
    
    def ui_init(self):
        self.setWindowTitle("截图小工具")
        self.setGeometry(600, 400, 800, 100)  # 设置窗口位置和大小
        self.label_init()
    
    def parameter_init(self):
        self.screens_info_list = []
        self.screens_info_in_label_text = ''
        self.app_setting = {
            "screenshot_screen": 0
        }
        self.read_setting_file()
        self.get_screens_info()
    
    # def connetions_Ui_MainWindow(self):
    #     for _, item in enumerate(self.all_screen_select_menu_action_list):
    #         item.triggel
    def read_setting_file(self):
        user_appdata_path = os.path.join(os.environ.get('USERPROFILE'), 'AppData', 'Local', 'Screen_Measure')
        if not os.path.exists(user_appdata_path):
            os.makedirs(user_appdata_path)
        setting_file_path = os.path.join(user_appdata_path, 'Screen_Measure_setting')
        if not os.path.exists(setting_file_path):
            with open(setting_file_path, 'w', encoding='utf-8') as setting_file:
                json.dump(self.app_setting, setting_file, ensure_ascii=False, indent=None)
        else:
            with open(setting_file_path, 'r',encoding = 'utf-8') as setting_file:
                    self.app_setting = json.load(setting_file)
    
    def get_screens_info(self):
        self.all_screens = QApplication.screens() # 获取所有屏幕
        for index, screen in enumerate(self.all_screens):
            left_top = screen.geometry().topLeft() - self.all_screens[0].geometry().topLeft()
            right_bottom = screen.geometry().bottomRight() - self.all_screens[0].geometry().topLeft() + QPoint(1,1)
            top_left_bottom_right_point = [left_top.x(), left_top.y(), right_bottom.x(), right_bottom.y()]
            temp_info_dict= {
                "select_action": None,
                "number": index,
                "top_left_bottom_right_point": top_left_bottom_right_point,
                "size": screen.size(),
                "geometry": screen.geometry(),
                "available_geometry": screen.availableGeometry(),
                "logical_dpi": screen.logicalDotsPerInch()
            }
            self.screens_info_list.append(temp_info_dict)
            self.screens_info_in_label_text += f' 第{index+1}屏幕尺寸：({screen.size().width()}, {screen.size().height()})'
    
    def menubar_init(self):
        self.menubar = QMenuBar()
        self.setMenuBar(self.menubar)
        self.file_menu = self.menubar.addMenu('文件')
        self.new_menubar_action = QAction('新建', self)
        self.file_menu.addAction(self.new_menubar_action)
        self.open_menubar_action = QAction('打开', self)
        self.file_menu.addAction(self.open_menubar_action)
        self.option_menu = self.menubar.addMenu('选项')
        screen_select_menu = self.option_menu.addMenu('屏幕选择')
        self.screen_select_menu_action_group = QActionGroup(self)
        self.all_screen_select_menu = QAction('所有屏幕', self)
        self.all_screen_select_menu.setCheckable(True)
        self.screen_select_menu_action_group.addAction(self.all_screen_select_menu)
        screen_select_menu.addAction(self.all_screen_select_menu)
        for i, screen_item in enumerate(self.screens_info_list):
            temp_action = QAction(f'第{i+1}屏幕', self)
            temp_action.setCheckable(True)
            self.screen_select_menu_action_group.addAction(temp_action)
            screen_select_menu.addAction(temp_action)
            screen_item['select_action'] = temp_action
        self.all_screen_select_menu_action_list = screen_select_menu.actions()
        self.all_screen_select_menu_action_list[self.app_setting['screenshot_screen']]
        
        # self.all_screen_select_menu = QAction('新建', self)
        # self.screen_select_menu.addAction(self.all_screen_select_menu)
    
    def toolbar_init(self):
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        self.ruler_in_rect_toolbar = QAction(self.icon_setup(RULER_IN_RECT), '截图',self)
        self.toolbar.addAction(self.ruler_in_rect_toolbar)
        self.ruler_toolbar = QAction(self.icon_setup(RULER), '截图',self)
        self.toolbar.addAction(self.ruler_toolbar)
        self.a_toolbar = QAction(self.icon_setup(RULER_IN_RECT), '截图',self)
        self.toolbar.addAction(self.a_toolbar)
        self.ruler_in_window_toolbar = QAction(self.icon_setup(RULER_IN_WINDOW), '截图',self)
        self.toolbar.addAction(self.ruler_in_window_toolbar)
    
    def statusbar_init(self):
        self.statusbar_win_mouse = QStatusBar()
        self.setStatusBar(self.statusbar_win_mouse)
        win_geometry = self.geometry()
        self.statusbar_win_mouse.showMessage(f"窗口位置:({win_geometry.x()}, {win_geometry.y()}), 宽高：({win_geometry.width()}, {win_geometry.height()})")  # 设置状态栏初始消息
        
    # 设置图标
    def icon_setup(self, icon_code):
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(icon_code.encode()))
        return QIcon(pixmap)
    
    def label_init(self):
        central_widget = QWidget()  # 创建一个中央部件
        self.setCentralWidget(central_widget)  # 将中央部件设置为窗口的中心部件
        self.screen_select_label = QLabel()
        self.screen_select_label.setGeometry(0, 0, 50, 9)
        self.screen_select_label.setStyleSheet("background-color: #00AAAA")
        self.screen_size_label = QLabel()
        self.screen_size_label.setGeometry(0,0,200, 9)
        self.screen_select_label.setFixedWidth(150)  # 设置标签宽度
        self.main_layout = QHBoxLayout()  # 修正布局创建方式
        central_widget.setLayout(self.main_layout)  # 将布局设置到中央部件
        self.main_layout.setContentsMargins(4, 0, 0, 0)
        self.main_layout.addWidget(self.screen_select_label)
        self.main_layout.addWidget(self.screen_size_label)
        font = QFont("微软雅黑")  # 创建 QFont 对象
        font.setPointSize(9)
        self.screen_select_label.setFont(font)
        self.screen_size_label.setFont(font)  # 设置字体
        self.screen_select_label.setText("当前截取屏幕为：所有屏幕")
        self.screen_size_label.setText(self.screens_info_in_label_text)
    
    def mouseMoveEvent(self, event):
        win_geometry = self.geometry()
        self.statusbar_win_mouse.showMessage(f"窗口位置:({win_geometry.x()}, {win_geometry.y()}), 鼠标位置:({event.x()}, {event.y()})")
