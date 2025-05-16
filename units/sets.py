from . import utils

from qfluentwidgets import TitleLabel
class settingTitle(TitleLabel):
    def changeChatbar(self, num):
        print("changeChatbar", num)
        utils.setting("helper", "display")(num)