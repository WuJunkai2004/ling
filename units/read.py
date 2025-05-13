from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout, QApplication # Added imports
import requests # Added for API calls
import json # Added for JSON handling

from qframelesswindow.webengine import FramelessWebEngineView
from qfluentwidgets import FluentIcon as FIF


from qfluentwidgets import FlyoutViewBase, Flyout, FlyoutAnimationType, PlainTextEdit, TextEdit, PushButton
class ChatBar(FlyoutViewBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat_history = []
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
        if not user_text:
            return
        user_text = user_text.replace("\n", "<br>") 
        self.chat_display.appendHtml(f"<b>用户:</b> {user_text}<br>")
        self.chat_input.clear()

        MY_API_KEY = "sk-b278fb2336e74e5e99069e6c5845d877"
        # TODO: 请替换为您的通义千问API密钥和实际的API端点
        api_key = MY_API_KEY # 替换为您的API Key
        api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions" # 通义千问API端点示例

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Add user message to history
        self.chat_history.append({"role": "user", "content": user_text})

        # 构建请求体，使其符合OpenAI兼容模式
        # Include previous messages from chat_history, ensuring not to exceed token limits if necessary (not implemented here for brevity)
        messages_to_send = [
            {"role": "system", "content": "You are a helpful assistant."}
        ] + self.chat_history

        payload = {
            "model": "qwen-turbo",  # 或者其他您选用的模型
            "messages": messages_to_send
            # "parameters": {} # 根据通义千问兼容模式文档，此字段可能不需要或有特定支持的参数
        }

        try:
            self.chat_display.appendHtml("LLM: 正在思考中...")
            QApplication.processEvents() # Process UI events to show "正在思考中..."

            response = requests.post(api_url, headers=headers, json=payload, timeout=30) # Added timeout
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            
            response_data = response.json()
            
            # 解析API响应，提取模型回复，适配OpenAI兼容模式
            # 结构通常是 response_data['choices'][0]['message']['content']
            if response_data.get("choices") and len(response_data["choices"]) > 0:
                message = response_data["choices"][0].get("message", {})
                llm_reply = message.get("content", "无法获取回复或回复格式不正确。")
            else:
                llm_reply = "API响应中未找到有效的choices。"

            # Remove the "正在思考中..." message if it was the last one
            cursor = self.chat_display.textCursor()
            cursor.movePosition(cursor.End)
            cursor.select(cursor.BlockUnderCursor)
            if cursor.selectedText().startswith("LLM: 正在思考中..."):
                cursor.removeSelectedText()
                cursor.deletePreviousChar() # Remove the newline if any

            self.chat_display.append(f"LLM: {llm_reply}")
            # Add LLM reply to history
            self.chat_history.append({"role": "assistant", "content": llm_reply})

        except requests.exceptions.RequestException as e:
            # Remove the "正在思考中..." message if it was the last one
            cursor = self.chat_display.textCursor()
            cursor.movePosition(cursor.End)
            cursor.select(cursor.BlockUnderCursor)
            if cursor.selectedText().startswith("LLM: 正在思考中..."):
                cursor.removeSelectedText()
                cursor.deletePreviousChar() # Remove the newline if any
            self.chat_display.append(f"LLM Error: 请求失败 - {e}")
        except json.JSONDecodeError:
            # Remove the "正在思考中..." message if it was the last one
            cursor = self.chat_display.textCursor()
            cursor.movePosition(cursor.End)
            cursor.select(cursor.BlockUnderCursor)
            if cursor.selectedText().startswith("LLM: 正在思考中..."):
                cursor.removeSelectedText()
                cursor.deletePreviousChar() # Remove the newline if any
            self.chat_display.appendHtml("LLM Error: 无法解析API响应")
        except Exception as e:
            # Remove the "正在思考中..." message if it was the last one
            cursor = self.chat_display.textCursor()
            cursor.movePosition(cursor.End)
            cursor.select(cursor.BlockUnderCursor)
            if cursor.selectedText().startswith("LLM: 正在思考中..."):
                cursor.removeSelectedText()
                cursor.deletePreviousChar() # Remove the newline if any
            self.chat_display.appendHtml(f"LLM Error: 未知错误 - {e}")


class reader(FramelessWebEngineView): # Changed base class to QWidget
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat = None
        self.resizeEvent = self.onResizeEvent

    @pyqtSlot(str)
    def read(self, token:str):
        print("openUrl in read.reader")
        print(f"http://47.121.28.18:8000/var/html/{token}.html")
        url = QUrl(f"http://47.121.28.18:8000/var/html/{token}.html")
        print(f"openUrl in read.reader url: {url}")
        self.setUrl(url)
        print(f"setUrl: {url}\nloading...")
        self.load(url)
        self.show()
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
        if self.chat is None:
            self.chat = ChatBar(self)
        Flyout.make(self.chat, self.parent().ui.right_edge, self, FlyoutAnimationType.SLIDE_LEFT, False)


from qfluentwidgets import ToolButton
class chatIcon(ToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.CHAT)
        print("chatIcon")
