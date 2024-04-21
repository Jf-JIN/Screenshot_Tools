from User_interface import *
import sys

class Main(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        pass
    



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    # 在应用程序级别安装事件过滤器
    # event_filter = WinEventFilter()
    # app.installEventFilter(event_filter)
    sys.exit(app.exec_())