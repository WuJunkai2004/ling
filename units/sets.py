from . import utils

from qfluentwidgets import TitleLabel
class settingTitle(TitleLabel):
    def changeChatbar(self, num):
        print("changeChatbar", num)
        if(utils.cfg("helper", "display") == num):
            return
        utils.setting("helper", "display")(num)
        utils.alert("设置已保存", "设置已保存，请重启软件生效", utils.root(self), only=True)