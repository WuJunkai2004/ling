from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout, QApplication # Added imports
import requests # Added for API calls
import json # Added for JSON handling
import units.utils as utils # Added for utility functions

from qframelesswindow.webengine import FramelessWebEngineView
from qfluentwidgets import FluentIcon as FIF


from qfluentwidgets import FlyoutViewBase, Flyout, FlyoutAnimationType, PlainTextEdit, TextEdit, PushButton
class ChatBar(FlyoutViewBase):
    def __init__(self, parent, token):
        super().__init__(parent)
        self.token = token

        self.chat_layout = QVBoxLayout(self)
    
        self.chat_display = PlainTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_layout.addWidget(self.chat_display)

        self.chat_input = TextEdit(self)
        self.chat_input.setFixedHeight(50) # Set a fixed height for input
        self.chat_input.setPlaceholderText("请输入消息...")
        self.chat_layout.addWidget(self.chat_input)

        self.send_button = PushButton("发送", self)
        self.send_button.clicked.connect(self.send_message)
        self.chat_layout.addWidget(self.send_button)
        
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(10)
        self.setFixedSize(200, 600)

    def send_message(self):
        user_text = self.chat_input.toPlainText().strip()
        self.chat_input.clear()
        if not user_text:
            return
        user_html = user_text.replace("\n", "<br>") 
        self.chat_display.appendHtml(f"<b>用户:</b> {user_html}<br>")

        payload = {
            "msg": user_text,
            "selection": "",
            "token": self.token,
        }

        self.chat_display.appendHtml("<b>LLM:</b> 正在思考中...<br>")
        QApplication.processEvents()

        try:
            res = requests.post("http://47.121.28.18:8000/api/chat/chat", json=payload).json()
        except:
            utils.alert("请求失败", "请检查网络连接或API服务。", utils.root(self))
            return
        
        if res['success'] == False:
            utils.alert("云端错误", res['msg'], utils.root(self))
            return
        
        self.chat_display.appendHtml(f"<b>LLM:</b> {res['answer']}<br>")


class reader(FramelessWebEngineView): # Changed base class to QWidget
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat = None
        self.token = None
        self.resizeEvent = self.onResizeEvent

    @pyqtSlot(str)
    def read(self, token:str):
        print("openUrl in read.reader")
        print(f"http://47.121.28.18:8000/var/html/{token}.html")
        url = QUrl(f"http://47.121.28.18:8000/var/html/{token}.html")
        self.setUrl(url)
        self.load(url)
        self.show()
        if self.token != token and self.chat is not None:
            self.chat.chat_display.clear()
        self.token = token
        print("openUrl in read.reader end")

    def onLinkClicked(self, url):
        print(f"用户点击了链接: {url.toString()}")

    def getSelectedText(self):
        self.page().runJavaScript("window.getSelection().toString();", self.onTextSelected)

    def onTextSelected(self, text):
        print(f"用户选择的文字: {text}")

    def onResizeEvent(self, event):
        print("onResizeEvent")
        if self.chat:
            self.chat.setFixedSize(int(self.width()*0.25), int(self.height() - 20) )
        super().resizeEvent(event)

    def start_chat(self):
        print("start_chat")
        if self.token is None:
            self.token = "chat_test"
        if self.chat is None:
            self.chat = ChatBar(self, self.token)
        Flyout.make(self.chat, self.parent().ui.right_edge, self, FlyoutAnimationType.SLIDE_LEFT, False)


from qfluentwidgets import ToolButton
class chatIcon(ToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.CHAT)
        print("chatIcon")
