from PyQt5.QtCore import Qt, QThread, pyqtSlot, pyqtSignal

def root(component):
    """获取组件的根组件, 用于回退到 winMain"""
    while component.parent() is not None:
        component = component.parent()
    return component


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
