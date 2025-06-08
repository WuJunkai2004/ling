from . import utils
import os
import dataset


from qfluentwidgets import CardWidget, BodyLabel
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QPushButton
from PyQt5.QtCore import Qt, QEasingCurve
from PyQt5.QtGui import QPixmap
class AppCard(CardWidget):
    def __init__(self, token, filename, parent=None):
        super().__init__(parent)
        self.token = token
        self.filename = filename
        self.setFixedSize(150, 250)
        self.vLayout = QVBoxLayout(self)
        self.picture = utils.cover(self, token)
        self.vLayout.addWidget(self.picture)
        self.text = BodyLabel(os.path.basename(filename), self)
        self.text.setWordWrap(True)
        self.text.setAlignment(Qt.AlignCenter)
        self.vLayout.addWidget(self.text)
        self.clicked.connect(self.click)
    
    def click(self):
        # 点击卡片时，打开对应的文件
        print(f"Opening file: {self.filename}")
        print(f"Token: {self.token}")


from qfluentwidgets import TitleLabel
class historys(TitleLabel):
    def init_history(self, text):
        print("test_form", text)
        db = dataset.connect('sqlite:///./data/marks.db')
        history = db['history']
        for item in history:
            token = item['token']
            filename = item['filename']
            print(f"Adding card for token: {token}, filename: {filename}")
            self.parent().ui.waterflow.addCard(token, filename)
        self.setStyleSheet('background-color: white;')
        

from qfluentwidgets import FlowLayout
class history_flow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('history_flow')
        self.flow = FlowLayout(self, needAni=True)
        self.flow.setAnimation(250, QEasingCurve.OutQuad)
        self.flow.setContentsMargins(30, 30, 30, 30)
        self.flow.setVerticalSpacing(20)
        self.flow.setHorizontalSpacing(10)
        self.flow.setAlignment(Qt.AlignCenter)

    def addCard(self, token, filename):
        card = AppCard(token, filename, self)
        self.flow.addWidget(card)