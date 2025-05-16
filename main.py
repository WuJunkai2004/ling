import hashlib
import json
import os

import requests
import sys
import time

from PyQt5.QtCore    import Qt, QMetaObject, Q_ARG, pyqtSlot
from PyQt5.QtGui     import QIcon, QColor, QFont
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout

from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import NavigationItemPosition, FluentWindow, SubtitleLabel

from views.home import Ui_Form as Form_Home
from views.info import Ui_Form as Form_Info
from views.open import Ui_Form as Form_Open
from views.read import Ui_Form as Form_Read
from views.sets import Ui_Form as Form_Sets

import units.utils as utils


def md5(path: str) -> str:
    """ 计算文件的md5值 """
    m = hashlib.md5()
    f = open(path, 'rb')
    data = f.read(8 * 1024)
    m.update(data)
    f.close()
    return m.hexdigest()


class Widget(QFrame):
    def __init__(self, text: str, parent, Frame = None):
        super().__init__(parent=parent)
        if Frame is None:
            self.label = SubtitleLabel(text, self)
            self.hBoxLayout = QHBoxLayout(self)
            self.label.setFont(QFont('Microsoft YaHei', 24))
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

        self.setInterface('home', '首页',       form=Form_Home, icon=FIF.HOME)
        self.setInterface('open', '打开文件',   form=Form_Open, icon=FIF.VIEW)
        self.setInterface('hist', '阅读历史',   form=None, icon=FIF.HISTORY)
        self.set_________()
        self.setInterface('read', '正在阅读',   form=Form_Read, icon=FIF.EDIT)
        self.set_________()
        self.setInterface('mark', '收藏',       form=None,      icon=FIF.BOOK_SHELF)
        self.set_________(position=NavigationItemPosition.BOTTOM)
        self.setInterface('sets', '设置',       form=Form_Sets, icon=FIF.SETTING,
                          position=NavigationItemPosition.BOTTOM)
        self.setInterface('info', '关于',       form=Form_Info, icon=FIF.INFO,
                          position=NavigationItemPosition.BOTTOM)

        self.initWindow()
        self.initSetting()

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

    def switchReader(self, token: str):
        # 切换到阅读器界面
        if token == 'didnt upload':
            return 'continue'
        print('文件打开中...')
        # 切换到主线程
        QMetaObject.invokeMethod(self.interface["read"]['interface'].ui.widget, "read", Qt.QueuedConnection, 
                                  Q_ARG(str, token))
        time.sleep(3)
        # 切换到阅读器界面
        #QMetaObject.invokeMethod(self.interface["read"]['navigater'], "click", Qt.QueuedConnection)
        self.interface['read']['navigater'].click()
        print('文件打开成功')
        return 'stop'
    
    def failOpen(self, e):
        # 打开文件失败的回调函数
        print('文件打开失败', e)
        QMetaObject.invokeMethod(self, "alertOpen", Qt.QueuedConnection)
        
    @pyqtSlot()
    def alertOpen(self):
        # 弹出提示框
        utils.alert('文件打开失败', '文件打开失败，阅读器可能不支持该文件格式。', self, only=True)

    def openFile(self, file_path):
        # 打开文件的逻辑
        def file_check_md5():
            print('文件检查中...')
            md5_value = md5(file_path)
            req_md5 = requests.get(
                url = 'http://47.121.28.18:8000/api/quicheck',
                params = {'token': md5_value}
            )
            if req_md5.json()['status']:
                return md5_value
            return 'didnt upload'
        
        def file_upload(md5_value):
            if(md5_value == 'stop'):
                return 'stop'
            print('文件上传中...')
            with open(file_path, 'rb') as file:
                req_upload = requests.post(
                    url='http://47.121.28.18:8000/api/upload',
                    files={'file': file}
                )
            return req_upload.json().get('token')

        def file_convert(md5_value):
            if(md5_value == 'stop'):
                return 'didnt upload'
            print('文件转换中...')
            requests.post(
                url='http://47.121.28.18:8000/api/convert',
                json={'token': md5_value}
            )
            return md5_value

        utils.promise(self, file_check_md5) \
             .then(self.switchReader) \
             .then(file_upload) \
             .then(file_convert) \
             .then(self.switchReader) \
             .catch(self.failOpen) \
             .start()
    
    def initSetting(self):
        if os.path.exists('./config.json'):
            return
        default_setting = {
            'helper': {
                'enabled': True,
                'display': 'float', # 浮动: float, 固定: fixed
            }
        }
        with open('./config.json', 'w', encoding='utf-8') as f:
            json.dump(default_setting, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    win = MainWin()
    win.show()
    win.setCustomBackgroundColor(QColor(242, 242, 242), QColor(25, 33, 42))
    win.setMicaEffectEnabled(False)
    sys.exit(app.exec_())