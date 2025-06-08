from PyQt5.QtCore import QThread, pyqtSignal, Q_ARG, QMetaObject, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
import json
import os
import requests


def root(component):
    """获取组件的根组件, 用于回退到 winMain"""
    while hasattr(component, 'parent') and component.parent() is not None:
        component = component.parent()
    return component


def page(component, name: str):
    """获取组件的子组件, 用于获取页面"""
    main = root(component)
    try:
        return main.interface[name]['interface'].ui
    except Exception as e:
        print(f"Error getting page {name}: {e}")
        return None


from qfluentwidgets import MessageBox
def alert(title: str, message: str, parent, only = None):
    """弹出提示框"""
    msg = MessageBox(title, message, root(parent))
    if only == True:
        # 仅展示yes按钮
        msg.cancelButton.hide()
        msg.buttonLayout.insertStretch(1)
    if only == False:
        # 仅展示no按钮
        msg.yesButton.hide()
        msg.buttonLayout.insertStretch(0, 1)
    if(msg.exec()):
        return True
    return False


class promise(QThread):
    sign = pyqtSignal()  # 定义信号
    def __init__(self, parent, func, *args):
        super().__init__(parent = parent)
        self.func = func    # 任务函数
        self.args = args
        self.funs = []      # 后续的链式调用函数
        self.errf = None    # 错误处理函数
        self.sign.connect(self.run_next)
    
    def then(self, func):
        self.funs.append(func)
        return self
    
    def then_all(self, funs):
        self.funs = funs
        return self
    
    def catch(self, func):
        self.errf = func
        return self
    
    def run(self):
        try:
            print(f'promise call fun {self.func.__name__} with args {self.args}')
            self.result = self.func(*self.args)
        except Exception as e:
            if self.errf:
                self.errf(e)
            else:
                print(e)
            return
        self.sign.emit()
        
    def run_next(self):
        if not self.funs:
            return
        func = self.funs.pop(0)
        if not hasattr(self, 'result'):
            pro = promise(self.parent(), func)
        else:
            pro = promise(self.parent(), func, self.result)
        pro .then_all(self.funs)\
            .catch(self.errf)\
            .start()
        

def cfg(*key: str):
    with open('./data/config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    for k in key:
        try:
            config = config[k]
        except:
            return None
    return config


class setting:
    """setting("helper", "enabled")(True)"""
    def __init__(self, *keys):
        self.keys = keys
    
    def __call__(self, value):
        with open('./data/config.json', 'r', encoding='utf-8') as f:
            origin = json.load(f)
            config = origin
        for k in self.keys[:-1]:
            try:
                config = config[k]
            except:
                return None
        if config.get(self.keys[-1]) == value:
            return
        config[self.keys[-1]] = value
        print(config)
        with open('./data/config.json', 'w', encoding='utf-8') as f:
            json.dump(origin, f, ensure_ascii=False, indent=4)


def invokeMain(component, method, *args):
    # 将函数的调用转发到主线程
    def get_arg_type(arg):
        inner_type = (int, float, str, bool, list, dict)
        if isinstance(arg, inner_type):
            return type(arg)
        return object
    arg_types = [get_arg_type(arg) for arg in args]
    arg_alist = [Q_ARG(arg_type, arg) for arg_type, arg in zip(arg_types, args)]
    QMetaObject.invokeMethod(
        component, method, Qt.QueuedConnection, *arg_alist
    )


def __cover_load(token):
    url = f'http://47.121.28.18:8000/var/cover/{token}.png'
    local_path = f'./data/pics/{token}.png'
    if not os.path.exists('./data/pics'):
        os.makedirs('./data/pics')
    if os.path.exists(local_path):
        return
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            print(f'Cover image for {token} downloaded successfully.')
        else:
            print(f'Failed to download cover image for {token}. Status code: {response.status_code}')
    except Exception as e:
        print(f'Error downloading cover image for {token}: {e}')


def cover(parent, token):
    pic = QLabel(parent, objectName='picture')
    pic.setStyleSheet('background-color: #f0f0f0;')
    pic.setAlignment(Qt.AlignCenter)
    local_path = f'./data/pics/{token}.png'
    if not os.path.exists(local_path):
        __cover_load(token)
    if not os.path.exists(local_path):
        pic.setText('No Image')
    else:
        pic.setPixmap(QPixmap(local_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    return pic