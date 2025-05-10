# import QUrl
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEnginePage


from qframelesswindow.webengine import FramelessWebEngineView
class reader(FramelessWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page().setDevToolsPage(self.page())

    def openUrl(self):
        print("openUrl in read.reader")
        url = QUrl('https://www.baidu.com')  # 添加完整的 URL
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