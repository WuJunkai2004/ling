import dblite
import os

# new folder name "var"
os.mkdir("./var")
os.mkdir("./var/files")
os.mkdir("./var/html")
os.mkdir("./var/cover")
os.mkdir("./var/vector_db")


db = dblite.SQL('./var/datas.db')
db['files'].create('name', 'filename', 'md5')
db.commit()