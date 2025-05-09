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