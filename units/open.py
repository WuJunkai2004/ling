# import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFileDialog, QHBoxLayout
from PyQt5.QtGui import QFont

from . import utils

import os.path as path


from qfluentwidgets import PushButton
class open_select_button(PushButton):
    """open 页面的 select button"""
    def change_text(self):
        """该函数在地址栏输入时被调用，需要将按钮文字改成'打开文件'"""
        self.setText('打开文件')

    def be_click(self):
        """该函数在点击按钮时被调用，当按钮文字为'选择文件'时，弹出文件选择对话框"""
        if self.text() == '选择文件':
            file_name, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "Paper Files (*.pdf;*.caj);; All Files (*)")
            if file_name:
                utils.root(self).openFile(file_name)
            return
        print("No file selected")


from PyQt5.QtWidgets import QLabel
from qfluentwidgets import IndeterminateProgressRing
class file_get_label(QWidget):
    """open 页面的 file get label, 用于获取拖拽的文件路径"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Microsoft YaHei', 24))
        self.label.setText("请将文件拖拽至此")
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        print("dragEnterEvent in open.file_get_label")
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """拖拽放下事件"""
        print("dropEvent in open.file_get_label")
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if not path.exists(file_path):
                utils.alert("文件不存在", "文件不存在，请检查文件路径", self, only=True)
                event.ignore()
                return
            if not file_path.endswith(('.pdf', '.caj')):
                utils.alert("文件格式错误", "仅支持pdf或caj文件", self, only=True)
                event.ignore()
                return
            event.accept()
            self.loader()
            utils.root(self).openFile(file_path)
        else:
            event.ignore()

    def loader(self):
        print("loader in open.file_get_label")
        utils.page(self, 'open').switch_show.setCurrentIndex(1)

    def stop_loader(self):
        """停止加载动画"""
        print("stop_loader in open.file_get_label")
        utils.page(self, 'open').switch_show.setCurrentIndex(0)


class file_loading_ring(QWidget):
    """open 页面的 file loading ring, 用于加载动画"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.ring = IndeterminateProgressRing(parent=self)
        self.ring.setFixedSize(80, 80)
        self.hBoxLayout.addWidget(self.ring, 1, Qt.AlignCenter)
        self.setObjectName("file_loading_ring")
