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
