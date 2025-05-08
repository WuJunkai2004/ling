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
- assets: for assets files
- Lib: for python libraries, ignore this folder
- scripts: for python venvironment scripts, ignore this folder
- units: for pyqt5 ui files, should be compiled to python scripts
- views: for python scripts, use pyqt5 components to build the ui
- main.py: the entry point of the program
- start.bat: the script to compile the pyqt5 ui files to python scripts, and run the program
- README.md: this file
- requirements.txt: the python dependencies of the project
- .gitignore: the git ignore file
```

# 关于信号和信号槽
我们决定继续使用信号和信号槽的机制来实现组件之间的通信。
所以有了slots.py这个文件。
该文件中继承了很多组件，并且添加了对应的信号槽函数。