import sys

from qfluentwidgets import NavigationItemPosition, FluentWindow, SubtitleLabel, setFont
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QApplication, QMainWindow

#import QFrame and QHBoxLayout from PyQt5.QtWidgets
from PyQt5.QtWidgets import QFrame, QHBoxLayout
#import AlignCenter from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt
#import QIcon from PyQt5.QtGui
from PyQt5.QtGui import QIcon

#from units.home import Ui_Form as Frame_Home
from units.info import Ui_Form as Frame_Info
from units.open import Ui_Form as Frame_Open
from units.home import Ui_Form as Frame_Home


class Widget(QFrame):
    def __init__(self, text: str, parent, Frame = None):
        super().__init__(parent=parent)
        if Frame is None:
            self.label = SubtitleLabel(text, self)
            self.hBoxLayout = QHBoxLayout(self)
            setFont(self.label, 24)
            self.label.setAlignment(Qt.AlignCenter)
            self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        else:
            ui = Frame()
            ui.setupUi(self)

        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))


class MainWin(FluentWindow):
    """ 主界面 """
    def __init__(self):
        super().__init__()
        self.navigationInterface.setExpandWidth(250)
        # 创建子界面，实际使用时将 Widget 换成自己的子界面
        self.homeInterface = Widget('Home Interface', self, Frame_Home)
        self.openInterface = Widget('Open Interface', self, Frame_Open)
        self.albumInterface = Widget('Album Interface', self)
        self.albumInterface1 = Widget('Album Interface 1', self)
        self.settingInterface = Widget('Setting Interface', self)
        self.aboutInterface = Widget('About Interface', self, Frame_Info)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        self.addSubInterface(self.openInterface, FIF.VIEW, 'Open', NavigationItemPosition.SCROLL)
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.albumInterface,   FIF.HISTORY,    '阅读历史', NavigationItemPosition.SCROLL)
        self.addSubInterface(self.albumInterface1,  FIF.BOOK_SHELF, 'Album 1',  parent=self.albumInterface)
        self.addSubInterface(self.settingInterface, FIF.SETTING,    'Settings', NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.aboutInterface,   FIF.INFO,       'About', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('灵犀摘')
        self.navigationInterface.setMinimumExpandWidth(900)
        self.navigationInterface.expand(useAni=False)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    #初始化
    win = MainWin()
    #将窗口控件显示在屏幕上
    win.show()
    #程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())