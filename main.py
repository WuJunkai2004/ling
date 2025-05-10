import sys

from qfluentwidgets import NavigationItemPosition, FluentWindow, SubtitleLabel, setFont
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QApplication

#import QFrame and QHBoxLayout from PyQt5.QtWidgets
from PyQt5.QtWidgets import QFrame, QHBoxLayout
#import AlignCenter from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt
#import QIcon from PyQt5.QtGui
from PyQt5.QtGui import QIcon

from views.info import Ui_Form as Form_Info
from views.open import Ui_Form as Form_Open
from views.home import Ui_Form as Form_Home

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

        self.interface = {}

        self.setInterface('home', '首页',       form=Form_Home, icon=FIF.HOME)
        self.setInterface('open', '打开文件',   form=Form_Open, icon=FIF.VIEW)
        self.setInterface('hist', '阅读历史',   form=None,      icon=FIF.HISTORY)
        self.setSeparator('read-separator')
        self.setInterface('read', '正在阅读',   form=None,      icon=FIF.EDIT)
        self.setSeparator('mark-separator')
        self.setInterface('mark', '收藏',       form=None,      icon=FIF.BOOK_SHELF)
        self.setSeparator('bottom-separator')
        self.setInterface('sets', '设置',       form=None,      icon=FIF.SETTING)
        self.setInterface('info', '关于',       form=Form_Info, icon=FIF.INFO)

        self.initWindow()

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon('./assets/icon.ico'))
        self.setWindowTitle('灵犀摘')
        self.navigationInterface.setMinimumExpandWidth(900)
        self.navigationInterface.expand(useAni=False)

    def setInterface(self, name: str, text: str, /, *, form: Widget = None, 
                     icon: QIcon = QIcon(), parent=None, position=NavigationItemPosition.TOP):
        widget = Widget(name, self, form)
        self.interface[name] = {
            'widget': widget,
            'interface': self.addSubInterface(widget, icon, text, parent=parent, position=position)
        }

    def setSeparator(self, name:str, position: NavigationItemPosition = NavigationItemPosition.TOP):
        self.interface[name] = {
            'widget': None,
            'interface': self.navigationInterface.addSeparator(position=position)
        }

    def openFile(self, file_path):
        # 打开文件的逻辑
        print("open file: ", file_path)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    #初始化
    win = MainWin()
    #将窗口控件显示在屏幕上
    win.show()
    #程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())