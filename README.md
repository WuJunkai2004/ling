# ling
A Modern Paper Reader By PyQt5

### Build
using pyvenv
```bash
pip install -r requirements.txt
start.bat
```

### Develop
```bash
pip install pyqt5-tools
```

### Folder Structure
```bash
ling
- assets: 资源文件夹，存放图片和图标等资源
- Lib: python虚拟环境的Lib文件夹，存放python的标准库和第三方库
- scripts: python虚拟环境的Scripts文件夹，存放python的可执行文件和脚本
- views: UI文件夹，存放所有的UI文件。需要pyuic5编译成python脚本后调用
- units: 组件文件夹，存放ui文件对应的组件。组件仅重写了对应信号槽函数，其他的功能都交给了原组件
- main.py: 主程序文件，程序的入口
- start.bat: 启动脚本，编译ui文件并运行主程序
- README.md: 项目说明文件
- requirements.txt: python依赖文件列表
- .gitignore: git忽略文件
```

# 关于信号和信号槽
我们决定继续使用信号和信号槽的机制来实现组件之间的通信。
所以有了slots.py这个文件。
该文件中继承了很多组件，并且添加了对应的信号槽函数。