from PyQt5.QtWidgets import QApplication,  QMainWindow, QMenu, QMenuBar, QToolBar, QStatusBar, QLabel, QAction, QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QFrame, QActionGroup, QMessageBox, QDialog, QPushButton
from PyQt5.QtGui import QPixmap, QIcon, QCursor, QFont,QPainter, QColor
from PyQt5.QtCore import Qt, QByteArray, QObject, QEvent, pyqtSignal, QRect, QSize, QPoint, QCoreApplication
from Icon_svg import *
# from os import path as opath
# from os import environ as oenviron
import os
import json
import sys


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
        self.menubar_init()
        self.toolbar_init()
        self.statusbar_init()
        self.ui_init()
        self.event_filter = WinEventFilter()
        self.installEventFilter(self.event_filter)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        # self.connections_Ui_MainWindow()
    
    def ui_init(self):
        self.setWindowTitle("截图小工具")
        self.setGeometry(600, 400, 800, 100)  # 设置窗口位置和大小
        self.label_init()
    
    def parameter_init(self):
        self.start_measure_flag = False
        self.screens_info_list = []
        self.screens_info_in_label_text = ''
        self.standard_setting_info = {
            'screenshot_screen': 0,
            'measure_unit': ['px', 'pt', '%', 'ppi', 'dpi', 'dp', 'sp', 'rpx', 'rem', 'em', 'vw', 'vh', 'vm'],
            'magnifier_display': True,
            'magnifier_display_keep': False,
            'magnifier_extend': 3,
            'relativ_position': True
        }
        self.app_setting = dict(self.standard_setting_info)
        self.app_setting['measure_unit'] = self.app_setting['measure_unit'][0]
        self.check_dialog = None
        self.read_setting_file()
        self.get_screens_info()
    
    def read_setting_file(self):
        self.user_appdata_path = os.path.join(os.environ.get('USERPROFILE'), 'AppData', 'Local', 'Screen_Measure')
        if not os.path.exists(self.user_appdata_path):
            os.makedirs(self.user_appdata_path)
        self.setting_file_path = os.path.join(self.user_appdata_path, 'Screen_Measure_setting')
        if not os.path.exists(self.setting_file_path):
            self.write_setting_file()
        else:
            with open(self.setting_file_path, 'r',encoding = 'utf-8') as setting_file:
                try:
                    self.app_setting = json.load(setting_file)
                    # 检查app_setting
                    temp_dict = {}
                    repair_flag =False # 用于取消点击同意修复配置文件后，反复出现确认弹窗
                    for key, value in self.standard_setting_info.items():
                        if key in self.app_setting:
                            # 判断候选列表
                            if isinstance(value, list):
                                if isinstance(self.app_setting[key], str) and self.app_setting[key] in value:
                                    temp_dict[key] = self.app_setting[key]
                                else: 
                                    temp_dict[key] = self.repair_messagebox(value, repair_flag) #设置为默认值，即列表中的第0个元素
                                    repair_flag = True
                            # 判断整数型数据
                            elif isinstance(value, int) and isinstance(self.app_setting[key], int):
                                if self.app_setting[key] >= 0:
                                    temp_dict[key] = self.app_setting[key]
                                else:
                                    self.repair_messagebox(value, repair_flag) 
                                    repair_flag = True
                                if key == 'magnifier_extend' and self.app_setting[key] <= 1:
                                    temp_dict[key] = self.repair_messagebox(value, repair_flag)
                                    repair_flag = True
                            elif type(value) == type(self.app_setting[key]):
                                temp_dict[key] = self.app_setting[key]
                            else:
                                temp_dict[key] = self.repair_messagebox(value, repair_flag)
                                repair_flag = True
                        else:
                            temp_dict[key] = self.repair_messagebox(value, repair_flag)
                            repair_flag = True
                    self.app_setting = temp_dict
                    self.write_setting_file()
                except:
                    temp = self.repair_messagebox(self.app_setting)
                    self.write_setting_file(temp)
    
    def repair_messagebox(self, value, repair_flag=None):
        if repair_flag:
            if isinstance(value, list):
                return value[0]
            else:
                return value
        else:
            reply = QMessageBox.critical(None, '配置文件错误', '配置文件已被篡改、损坏或含有不正确的配置，程序无法正常运行。\n请选择“Yes”以修复配置文件。',
                                                        QMessageBox.Yes | QMessageBox.Cancel,
                                                        defaultButton=QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                if isinstance(value, list):
                    return value[0]
                else:
                    return value
            else:
                sys.exit()
    
    def write_setting_file(self, file=None):
        if not file:
            file = self.app_setting
        with open(self.setting_file_path, 'w', encoding='utf-8') as setting_file:
                json.dump(file, setting_file, ensure_ascii=False, indent=None)
    
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
        # ====================选项====================
        self.option_menu = self.menubar.addMenu('选项')
        # print(type(self.option_menu))
        # --------------------屏幕选择--------------------
        screen_select_menu = self.option_menu.addMenu('屏幕选择')
        self.screen_select_menu_action_group = QActionGroup(self)
        self.all_screen_select_menu = QAction('所有屏幕', self)
        self.all_screen_select_menu.setCheckable(True)
        self.screen_select_menu_action_group.addAction(self.all_screen_select_menu)
        screen_select_menu.addAction(self.all_screen_select_menu)
        for i, screen_item in enumerate(self.screens_info_list):
            temp_action = self.action_init(f'第{i+1}屏幕', screen_select_menu, self.screen_select_menu_action_group)
            screen_item['select_action'] = temp_action
        self.screen_select_menu_action_list = self.screen_select_menu_action_group.actions()
        # print(self.app_setting['screenshot_screen'], len(self.screen_select_menu_action_list))
        if self.app_setting['screenshot_screen'] > len(self.screen_select_menu_action_list)-1:
            self.app_setting['screenshot_screen'] = 0
            self.write_setting_file()
            # print(self.app_setting['screenshot_screen'])
        self.screen_select_menu_action_list[self.app_setting['screenshot_screen']].setChecked(True)
        # --------------------坐标设置--------------------
        position_select_menu = self.option_menu.addMenu('坐标设置')
        self.position_select_menu_action_group = QActionGroup(self)
        self.position_select_absolute_action = self.action_init('绝对坐标', position_select_menu, self.position_select_menu_action_group)
        self.position_select_relativ_action = self.action_init('相对坐标', position_select_menu, self.position_select_menu_action_group)
        self.position_select_menu_action_list = self.position_select_menu_action_group.actions()
        print(self.app_setting)
        # self.position_select_menu_action_list[self.app_setting['relativ_position']].setChecked(True)
        # --------------------测量单位设置--------------------
        
        measure_unit_menu = self.option_menu.addMenu('测量单位')
        self.measure_unit_menu_action_group = QActionGroup(self)
        self.measure_unit_px_action = self.action_init('像素(px)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_point_action = self.action_init('点(pt)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_percent_action = self.action_init('百分比(%)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_ppi_action =  self.action_init('像素密度(ppi)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_dpi_action =  self.action_init('每英寸点数(dpi)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_dp_action =  self.action_init('独立像素(dp)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_sp_action =  self.action_init('比例像素(sp)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_rpx_action =  self.action_init('响应式像素(rpx)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_rem_action =  self.action_init('根元素字体大小(rem)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_em_action =  self.action_init('文本字体尺寸(em)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_vw_action =  self.action_init('视口宽度百分比(vw)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_vh_action =  self.action_init('视口高度百分比(vh)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_vm_action =  self.action_init('视口单位(vm)', measure_unit_menu, self.measure_unit_menu_action_group)
        self.measure_unit_menu_action_list = self.measure_unit_menu_action_group.actions()
        for action in self.measure_unit_menu_action_list:
            if action.text().split('(')[1].split(')')[0] == self.app_setting['measure_unit']:
                action.setChecked(True)
                break
        
        
        
        # self.all_screen_select_menu = QAction('新建', self)
        # self.screen_select_menu.addAction(self.all_screen_select_menu)
    
    def action_init(self, display_text: str, parent_menu: QMenu, action_group:QActionGroup = None,  checkable_flag:bool = True):
        temp = QAction(display_text, self)
        if action_group:
            action_group.addAction(temp)
        if checkable_flag:
            temp.setCheckable(True)
        parent_menu.addAction(temp)
        return temp
    
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
        self.screen_select_label.setFixedWidth(120)  # 设置标签宽度
        self.main_layout = QHBoxLayout()  # 修正布局创建方式
        central_widget.setLayout(self.main_layout)  # 将布局设置到中央部件
        self.main_layout.setContentsMargins(4, 0, 0, 0)
        self.main_layout.addWidget(self.screen_select_label)
        self.main_layout.addWidget(self.screen_size_label)
        font = QFont("微软雅黑")  # 创建 QFont 对象
        font.setPointSize(9)
        self.screen_select_label.setFont(font)
        self.screen_size_label.setFont(font)  # 设置字体.
        self.screen_select_label.setText(f"当前截取：{self.screen_select_menu_action_list[self.app_setting['screenshot_screen']].text()}")
        self.screen_size_label.setText(self.screens_info_in_label_text)
    
    def mouseMoveEvent(self, event):
        win_geometry = self.geometry()
        self.statusbar_win_mouse.showMessage(f"窗口位置:({win_geometry.x()}, {win_geometry.y()}), 鼠标位置:({event.x()}, {event.y()})")
