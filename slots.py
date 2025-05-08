# import QtWidgets
from PyQt5 import QtWidgets


from qfluentwidgets import PushButton
class open_select_button(PushButton):
    """open 页面的 select button"""
    def change_text(self):
        """该函数在地址栏输入时被调用，需要将按钮文字改成'打开文件'"""
        self.setText('打开文件')

    def be_click(self):
        """该函数在点击按钮时被调用，当按钮文字为'选择PDF文件'时，弹出文件选择对话框"""
        if self.text() != '选择PDF文件':
            return
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择PDF文件", "", "PDF Files (*.pdf);;All Files (*)")
        if file_name:
            print(file_name)
        else:
            print("No file selected")
