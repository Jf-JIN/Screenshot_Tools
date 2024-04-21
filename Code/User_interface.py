from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QToolBar, QStatusBar, QPushButton, QLabel, QAction
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtCore import QByteArray, QObject, QEvent
from Icon_svg import *

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
        self.setWindowTitle("截图小工具")
        self.setGeometry(600, 400, 800, 80)  # 设置窗口位置和大小
        self.setMaximumHeight(80)
        self.menubar_init()
        self.toolbar_init()
        self.statusbar_init()
        self.event_filter = WinEventFilter()
        self.installEventFilter(self.event_filter)
    
    def menubar_init(self):
        self.menubar = QMenuBar()
        self.setMenuBar(self.menubar)
        self.file_menu = self.menubar.addMenu('文件')
        self.new_menubar_action = QAction('新建', self)
        self.file_menu.addAction(self.new_menubar_action)
        self.open_menubar_action = QAction('打开', self)
        self.file_menu.addAction(self.open_menubar_action)
    
    def toolbar_init(self):
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        self.new_toolbar_action = QAction(self.icon_setup(NEW_FILE), '新建',self)
        self.toolbar.addAction(self.new_toolbar_action)
    
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
    
    def mouseMoveEvent(self, event):
        win_geometry = self.geometry()
        self.statusbar_win_mouse.showMessage(f"窗口位置:({win_geometry.x()}, {win_geometry.y()}), 鼠标位置:({event.x()}, {event.y()})")