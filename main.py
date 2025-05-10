import sys
import requests
import os
import time

from qfluentwidgets import NavigationItemPosition, FluentWindow, SubtitleLabel, setFont
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QApplication

#import QFrame and QHBoxLayout from PyQt5.QtWidgets
from PyQt5.QtWidgets import QFrame, QHBoxLayout
#import AlignCenter from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt
#import QIcon from PyQt5.QtGui
from PyQt5.QtGui import QIcon, QColor

from views.info import Ui_Form as Form_Info
from views.open import Ui_Form as Form_Open
from views.home import Ui_Form as Form_Home
from views.read import Ui_Form as Form_Read

from qframelesswindow.webengine import FramelessWebEngineView

import units.utils as utils

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
            self.ui = Frame()
            self.ui.setupUi(self)
        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))


class MainWin(FluentWindow):
    """ 主界面 """
    def __init__(self):
        super().__init__()
        self.navigationInterface.setExpandWidth(250)

        self.interface = {}
        self.reading   = {}

        self.setInterface('home', '首页',       form=Form_Home, icon=FIF.HOME)
        self.setInterface('open', '打开文件',   form=Form_Open, icon=FIF.VIEW)
        self.setInterface('hist', '阅读历史',   form=None, icon=FIF.HISTORY)
        self.set_________()
        self.setInterface('read', '正在阅读',   form=Form_Read, icon=FIF.EDIT)
        self.set_________()
        self.setInterface('mark', '收藏',       form=None,      icon=FIF.BOOK_SHELF)
        self.set_________(position=NavigationItemPosition.BOTTOM)
        self.setInterface('sets', '设置',       form=None,      icon=FIF.SETTING,
                          position=NavigationItemPosition.BOTTOM)
        self.setInterface('info', '关于',       form=Form_Info, icon=FIF.INFO,
                          position=NavigationItemPosition.BOTTOM)

        self.initWindow()

    def initWindow(self):
        self.resize(1080, 700)
        self.setWindowIcon(QIcon('./assets/icon.ico'))
        self.setWindowTitle('灵犀摘')
        self.navigationInterface.setMinimumExpandWidth(900)
        self.navigationInterface.expand(useAni=False)

    def setInterface(self, name: str, text: str, /, *, form: Widget = None, 
                     icon: QIcon = QIcon(), parent=None, position=NavigationItemPosition.TOP):
        # 设置导航栏的按钮
        widget = Widget(name, self, form)
        self.interface[name] = {
            'interface': widget,   # 界面
            'navigater': self.addSubInterface(widget, icon, text, parent=parent, position=position) # 导航栏
        }

    def set_________(self, position: NavigationItemPosition = NavigationItemPosition.TOP):
        # 设置导航栏的分隔符
        self.navigationInterface.addSeparator(position=position)

    def openFile(self, file_path):
        # 打开文件的逻辑
        print('打开文件:', file_path)
        with open(file_path, 'rb') as file:
            try:
                req_upload = requests.post(
                    url='http://47.121.28.18:8000/api/upload',
                    files={'file': file}
                )
            except:
                utils.alert('文件打开失败', '文件打开失败，请检查文件路径或网络连接。', self, only=True)
                return
        token = req_upload.json().get('token')
        try:
            req_convert = requests.post(
                url='http://47.121.28.18:8000/api/convert',
                json={'token': token}
            )
        except:
            utils.alert('文件打开失败', '文件打开失败，阅读器可能不支持该文件格式。', self, only=True)
            return
        if token in self.reading.keys():
            # 如果文件已经在阅读中，则直接打开
            self.interface[token]['navigater'].click()
            return
        # 如果文件不在阅读中，则创建页面，开始阅读
        self.interface["read"]['interface'].ui.widget.read(token)
        time.sleep(3)
        self.interface["read"]['navigater'].click()


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    win = MainWin()
    win.show()
    win.setCustomBackgroundColor(QColor(242, 242, 242), QColor(25, 33, 42))
    win.setMicaEffectEnabled(False)
    sys.exit(app.exec_())