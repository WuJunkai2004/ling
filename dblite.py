# Author: WuJunkai2004
# Update: 2025-05-10
# Version: 1.1.2


import sqlite3
try:
    import pandas as pd
except:
    __can_be_visualized = False
else:
    __can_be_visualized = True

debug   = False
defined = [':memory:', 'debug.db'][debug]


class CONLUMN:
    def __init__(self, cursor, table, conlumn):
        self.cursor = cursor
        self.table  = table
        self.name   = conlumn

    def __setitem__(self, __id, __value):
        self.insert(__id, __value)

    def __getitem__(self, __id):
        if(__id < 1):
            raise RuntimeError("下标错误")
        self.cursor.execute("SELECT {} FROM {} WHERE oid={}".format( self.name, self.table, __id))
        return self.cursor.fetchone()[0]

    def update(self, __id, __value):
        self.insert(__id, __value)

    def insert(self, __id, __value):
        self.cursor.execute('UPDATE {} set "{}"="{}" WHERE oid={}'.format(self.table, self.name, __value, __id))

    def index(self, __value, __start = 0, __stop = 0x7fffffffffffffff):
        #return list.index(self, __value, __start, __stop) + 1
        self.cursor.execute("SELECT oid FROM {} WHERE {}='{}'".format(self.table, self.name, __value))
        if found := self.cursor.fetchone():
            return found[0]
        return -1
    
    def append(self, __iterable):
        for item in __iterable:
            self.cursor.execute("INSERT INTO {} ({}) VALUES ({})".format(self.table, self.name, '"{}"'.format(item) ) )
    
    def __iter__(self):
        self.cursor.execute("SELECT {} FROM {}".format(self.name, self.table))
        for item in self.cursor.fetchall().__iter__():
            yield item[0]

    def __len__(self):
        self.cursor.execute("SELECT COUNT({}) FROM {}".format(self.name, self.table))
        return self.cursor.fetchone()[0]


class TABLE:
    def __init__(self, cursor, table) -> None:
        self.cursor = cursor
        self.name   = table

    def __getitem__(self, __name):
        return CONLUMN(self.cursor, self.name, __name)

    def create(self, *__conlumns):
        self.cursor.execute( 'CREATE TABLE "{}"\n({});'.format(self.name, ',\n'.join(['"{}" TEXT'.format(item) for item in __conlumns]) ) )

    def insert(self, *__value) -> None:
        try:
            self.cursor.execute("INSERT INTO {} VALUES({})".format(self.name, ",".join(['"{}"'.format(item) for item in __value]) ) )
        except:
            return 'ERROR in ```{}```'.format(__value)

    def filder(self, __filder):
        pass

    def add_conlumn(self, __name):
        self.cursor.execute("ALTER TABLE {} ADD COLUMN {}".format(self.name, __name))

    def del_line(self, __id):
        self.cursor.execute("DELETE FROM {} WHERE oid={}".format(self.name, __id))

    def del_table(self):
        self.cursor.execute("DROP TABLE {}".format(self.name))

    def existed(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(self.name))
        return bool(self.cursor.fetchone())
    
    def __len__(self):
        self.cursor.execute('SELECT COUNT(*) FROM "{}"'.format(self.name))
        return self.cursor.fetchone()[0]



class SQL:
    def __init__(self, file = defined) -> None: 
        self.connect = sqlite3.connect(file)
        self.cursor  = self.connect.cursor()
        self.status  = 'open'

    def __getitem__(self, __name) -> TABLE:
        return TABLE(self.cursor, __name)
        
    def __del__(self) -> None:
        if(self.status == 'open'):
            self.close()

    def commit(self):
        self.connect.commit()

    def vacuum(self):
        self.connect.execute("VACUUM")

    def close(self):
        self.connect.commit()
        self.cursor .close()
        self.connect.close()
        self.status = 'close'


def _shell():
    print("欢迎使用 dblite shell")
    while(True):
        cmmd = ''
        line = input('>>>').rstrip()
        cmmd += line
        while(line and (line[0] == ' ' or line[-1] == ':')):
            line = input('...').rstrip()
            cmmd += '\n' + line
        try:
            result = eval(cmmd)
        except Exception as e1:
            try:
                exec(cmmd)
            except Exception as e2:
                print("ERROR ! : {}".format(e2))
        else:
            if(result != None):
                print(result)


if(__name__ == "__main__"):
    _shell()
