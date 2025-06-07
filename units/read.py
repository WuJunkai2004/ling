from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout, QApplication # Added imports
import requests # Added for API calls
import json # Added for JSON handling
import dataset
from . import utils

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
        self.send_button.clicked.connect(self.start_send)
        self.chat_layout.addWidget(self.send_button)
        
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(10)
        self.setFixedSize(200, 600)

    def start_send(self):
        utils.page(self, "read").widget.page().runJavaScript(
            "window.getSelection().toString();", 
            self.send_message
        )

    def send_message(self, selected_text):
        print(f"选中的文本: {selected_text}")
        user_text = self.chat_input.toPlainText().strip()
        self.chat_input.clear()
        if not user_text:
            return
        user_html = user_text.replace("\n", "<br>") 
        self.chat_display.appendHtml(f"<b>用户:</b> {user_html}<br>")

        payload = {
            "msg": user_text,
            "selection": selected_text,
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


class TransBar(FlyoutViewBase):
    def __init__(self, parent, token):
        super().__init__(parent)
        self.trans_layout = QVBoxLayout(self)

        self.trans_display = PlainTextEdit(self)
        self.trans_display.setReadOnly(True)
        self.trans_layout.addWidget(self.trans_display)

        self.trans_layout.setContentsMargins(10, 10, 10, 10)
        self.trans_layout.setSpacing(10)
        self.setFixedSize(200, 600)


    def add_translation(self, original_text, translated_text):
        self.trans_display.appendHtml(f"<b>原文:</b> {original_text}<br>")
        self.trans_display.appendHtml(f"<b>翻译:</b> {translated_text}<br><br>")
    


class reader(FramelessWebEngineView): # Changed base class to QWidget
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat = None
        self.tran = None
        self.token = None
        self.file_name = None
        self.resizeEvent = self.onResizeEvent

    def set_file_name(self, file_name):
        print("set_file_name in read.reader")
        self.file_name = file_name

    @pyqtSlot(str)
    def read(self, token:str):
        utils.page(self, "open").switch_show.setCurrentIndex(0)
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
        db = dataset.connect('sqlite:///./data/marks.db')
        history = db['history']
        if not history.find_one(token=token):
            history.insert({'token': token, 'filename': self.file_name})
            db.commit()

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
            self.chat.chat_input.setFixedHeight(max(int(self.height()*0.2 - 20), 50))
        if self.tran:
            self.tran.setFixedSize(int(self.width()*0.25), int(self.height() - 20) )
        super().resizeEvent(event)

    def start_chat(self):
        print("start_chat")
        if self.token is None:
            self.token = "chat_test"
        if self.chat is None:
            self.chat = ChatBar(self, self.token)
        self.onResizeEvent(None)  # Trigger resize to set initial size
        if utils.cfg("helper", "display") == 0:
            Flyout.make(self.chat, self.parent().ui.right_edge, self, FlyoutAnimationType.SLIDE_LEFT, False)
            return
        # 侧边栏
        if self.parent().ui.right_edge.width() > 0:
            self.parent().ui.right_edge.setFixedWidth(0)
            return
        self.parent().ui.right_edge.setLayout(self.chat.chat_layout)
        self.parent().ui.right_edge.setFixedWidth(200)

    def mark_favorite(self):
        print("mark_favorite")
        if self.file_name is None or self.token is None or self.token == "chat_test":
            utils.alert("提示", "请先打开一篇文章。", utils.root(self))
            return
        db = dataset.connect('sqlite:///./data/marks.db')
        marks = db['marks']
        if marks.find_one(token=self.token, file_name=self.file_name):
            utils.alert("提示", "该文章已被标记为收藏。", utils.root(self))
            return
        marks.insert({'token': self.token, 'filename': self.file_name})
        db.commit()

    def start_trans(self):
        if self.token is None:
            return
        if self.tran is None:
            self.tran = TransBar(self, self.token)
        # 获取WebEngineView中的选中文本
        Flyout.make(self.tran, self.parent().ui.right_edge, self, FlyoutAnimationType.SLIDE_LEFT, False)
        self.page().runJavaScript("window.getSelection().toString();", self.translate)

    def translate(self, text):
        print(f"用户选择的文字: //{text}//")
        if not text:
            utils.alert("提示", "请先选择要翻译的文本。", utils.root(self))
            return
        url = "http://47.121.28.18:8000/api/trans"
        payload = {
            "text": text,
            "token": self.token,
        }
        try:
            res = requests.post(url, json=payload).json()
        except:
            utils.alert("请求失败", "请检查网络连接或API服务。", utils.root(self))
            return
        if res['success'] == False:
            utils.alert("云端错误", "请联系管理员。", utils.root(self))
            return
        print(f"翻译结果 {res['text']}")
        self.tran.add_translation(text, res['text'])


from qfluentwidgets import ToolButton, FluentIconBase
class chatIcon(ToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.CHAT)
        self.setToolTip("开启AI对话")
        print("chatIcon")


class starIcon(ToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.TAG)
        self.setToolTip("标记为收藏")
        self.is_marked = False
        print("starIcon")

    def toggle(self):
        if self.is_marked:
            # 切换成未标记状态，图标颜色变深
            self.setIcon(FluentIconBase.icon(FIF.TAG, color="black"))
        else:
            # 切换成标记状态，图标颜色变浅
            self.setIcon(FluentIconBase.icon(FIF.TAG, color="red"))
        self.is_marked = not self.is_marked


class transIcon(ToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.LANGUAGE)
        self.setToolTip("翻译")
        print("transIcon")