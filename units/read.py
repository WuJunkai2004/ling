# import QUrl
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEnginePage

from qframelesswindow.webengine import FramelessWebEngineView
class reader(FramelessWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page().setDevToolsPage(self.page())
        self.resizeEvent = self.onResizeEvent  # Override resize event

    def read(self, token:str):
        print("openUrl in read.reader")
        print(f"http://47.121.28.18:8000/var/html/{token}.html")
        url = QUrl(f"http://47.121.28.18:8000/var/html/{token}.html")
        self.setUrl(url)
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
        new_width = self.width()
        new_height = self.height()
        print(f"窗口大小已更改: 宽度={new_width}, 高度={new_height}")
        super().resizeEvent(event)
