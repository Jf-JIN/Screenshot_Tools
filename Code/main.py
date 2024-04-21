from User_interface import *
import sys

class ViewWindow(QWidget):
    def __init__(self, view_image, win_geometry):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(win_geometry)  # 设置窗口位置和大小
        self.view = QLabel(self)
        self.view.setPixmap(view_image)

class Main(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.connection()
        self.temp_png_path = "1.png"
        self.windows = []
    
    def connection(self):
        self.new_toolbar_action.triggered.connect(self.create_canvas)
    
    def create_canvas(self):
        image = self.get_screenshot()
        # 遍历所有屏幕创建窗口
        for index in range(len(self.screen_size_all)):
            window = ViewWindow(image[index], self.screen_size_all[index].geometry())
            window.show()
            self.windows.append(window)
        
    def get_screenshot(self):
        temp_screenshots_list = []
        for screen in self.screen_size_all:
            # 截取窗口
            pixmap = screen.grabWindow(0)
            temp_screenshots_list.append(pixmap)
        return temp_screenshots_list


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())