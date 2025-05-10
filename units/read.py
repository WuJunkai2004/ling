# import QUrl
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView # Added QWebEngineView for type hint
from PyQt5.QtCore import pyqtSignal # Added pyqtSignal for custom signal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSplitter, QTextEdit, QPushButton, QVBoxLayout, QLabel, QApplication # Added imports
import requests # Added for API calls
import json # Added for JSON handling

from qframelesswindow.webengine import FramelessWebEngineView
from qframelesswindow import FramelessWindow # reader will be a QWidget now

class CustomWebEnginePage(QWebEnginePage):
    linkClicked = pyqtSignal(QUrl)

    def __init__(self, parent=None):
        super().__init__(parent)

    def acceptNavigationRequest(self, url, type, isMainFrame):
        if type == QWebEnginePage.NavigationTypeLinkClicked:
            self.linkClicked.emit(url)
            return False # Prevent default navigation for clicked links
        return super().acceptNavigationRequest(url, type, isMainFrame)

class reader(QWidget): # Changed base class to QWidget
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat_history = [] # Initialize chat history
        self.current_url = ""

        # Main layout
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)

        # Splitter for left (PDF) and right (Chat)
        self.splitter = QSplitter(self)
        self.layout.addWidget(self.splitter)

        # PDF阅读器
        # Left side: PDF Viewer
        self.pdf_viewer = FramelessWebEngineView(self)
        # Create and set the custom page
        self.custom_page = CustomWebEnginePage(self.pdf_viewer)
        self.pdf_viewer.setPage(self.custom_page)
        self.pdf_viewer.page().setDevToolsPage(self.pdf_viewer.page()) # Configure dev tools for pdf_viewer
        # self.pdf_viewer.resizeEvent = self.onResizeEvent # This might not be needed or handled differently
        self.splitter.addWidget(self.pdf_viewer)

        # LLM交流器
        # Right side: Chat Interface (Placeholder)
        self.chat_widget = QWidget(self)
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_widget.setLayout(self.chat_layout)

        self.chat_display = QTextEdit(self.chat_widget)
        self.chat_display.setReadOnly(True)
        self.chat_layout.addWidget(self.chat_display)

        self.chat_input = QTextEdit(self.chat_widget)
        self.chat_input.setFixedHeight(50) # Set a fixed height for input
        self.chat_layout.addWidget(self.chat_input)

        self.send_button = QPushButton("发送", self.chat_widget)
        self.chat_layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.send_message) # Connect send message logic

        self.splitter.addWidget(self.chat_widget)

        # Set initial sizes for splitter panes (optional)
        self.splitter.setSizes([self.width() // 2, self.width() // 2])

        # Connect signals for PDF viewer if needed
        self.custom_page.linkClicked.connect(self.onLinkClicked)
        # self.resizeEvent = self.onResizeEvent # Override resize event for the main reader widget if needed

    def read(self, token:str):
        print("openUrl in read.reader")
        print(f"http://47.121.28.18:8000/var/html/{token}.html")
        url = QUrl(f"http://47.121.28.18:8000/var/html/{token}.html")
        self.current_url = url.toString() # Store the current URL
        self.pdf_viewer.setUrl(url)
        self.pdf_viewer.load(url)
        self.pdf_viewer.show()
        self.show() # Show the main reader widget
        print("openUrl in read.reader end")

    def onLinkClicked(self, url):
        print(f"用户点击了链接: {url.toString()}")

    def getSelectedText(self):
        self.pdf_viewer.page().runJavaScript("window.getSelection().toString();", self.onTextSelected)

    def onTextSelected(self, text):
        print(f"用户选择的文字: {text}")

    # def onResizeEvent(self, event): # This might need to be re-evaluated or removed if layout handles it
    #     new_width = self.width()
    #     new_height = self.height()
    #     print(f"窗口大小已更改: 宽度={new_width}, 高度={new_height}")
    #     super().resizeEvent(event)

    # Placeholder for send message logic
    def send_message(self):
        user_text = self.chat_input.toPlainText().strip()
        if not user_text:
            return

        self.chat_display.append(f"用户: {user_text}")
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
            self.chat_display.append("LLM: 正在思考中...")
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
            self.chat_display.append("LLM Error: 无法解析API响应")
        except Exception as e:
            # Remove the "正在思考中..." message if it was the last one
            cursor = self.chat_display.textCursor()
            cursor.movePosition(cursor.End)
            cursor.select(cursor.BlockUnderCursor)
            if cursor.selectedText().startswith("LLM: 正在思考中..."):
                cursor.removeSelectedText()
                cursor.deletePreviousChar() # Remove the newline if any
            self.chat_display.append(f"LLM Error: 未知错误 - {e}")

    # def send_message(self):
    #     user_text = self.chat_input.toPlainText()
    #     if user_text.strip():
    #         self.chat_display.append(f"用户: {user_text}")
    #         # Add LLM interaction logic here
    #         self.chat_display.append(f"LLM: ... (响应) ...") 
    #         self.chat_input.clear()
