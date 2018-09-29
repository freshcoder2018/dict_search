'''
name: freshcoder2018
date: 2018/09/28
email: lindascut@qq.com
module: pymysql
This is a dict search project exercise
'''

from socket import *
import os
import sys
import time
import signal
import pymysql

# 定义需要的全局变量
# 单词本位置
DICT_TEXT = './dict.txt'
# 地址
HOST = '0.0.0.0'
PORT = 8000
ADDR = (HOST, PORT)

# 流程控制
def main():
    # 创建数据库链接
    db = pymysql.connect('localhost', 'root', '123456', 'dict')

    # 创建套接字
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(5)

    # 忽略子进程信号
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    while True:
        try:
            c, addr = s.accept()
            print('Connect from', addr)
        except KeyboardInterrupt:
            s.close()
            sys.close('服务器退出')
        except Exception as e:
            print(e)
            continue

        # 创建子进程
        pid = os.fork()
        if pid == 0:
            s.close()
            do_child(c, db)
        else:
            c.close()
            continue


def do_child(c, db):
    # 循环接收客户端请求
    while True:
        data = c.recv(128).decode()
        data = data.split(' ')
        if (not data) or data[0] == 'E':
            c.close()
            sys.exit(0)
        elif data[0] == 'R':
            do_register(c, data[1], data[2], db)
        elif data[0] == 'L':
            do_login(c, data[1], data[2], db)
        elif data[0] == 'Q':
            do_query(c, data[1], data[2], db)
        elif data[0] == 'H':
            do_hist(c, data[1], db)


def do_login(c, name, passwd, db):
    print('登录操作')
    cursor = db.cursor()
    sql = 'select * from user where name="%s" and passwd="%s"' % (name, passwd)
    cursor.execute(sql)
    r = cursor.fetchone()
    if r is None:
        c.send(b'FALL')
    else:
        print('%s登录成功' % name)
        c.send(b'OK')


def do_register(c, name, passwd, db):
    print('注册操作')
    cursor = db.cursor()
    sql = 'select * from user where name="%s"' % name
    cursor.execute(sql)
    r = cursor.fetchone()
    if r is not None:
        c.send(b'EXISTS')
        return

    # 用户不存在插入用户
    sql = 'insert into user(name, passwd) values("%s","%s")' % (name, passwd)
    try:
        cursor.execute(sql)
        db.commit()
        c.send(b'OK')
    except:
        db.rollback()
        c.send(b'FALL')
    else:
        print('%s注册成功' % name)


def do_query(c, name, word, db):
    print('查询操作', word)
    cursor = db.cursor()

    def insert_history():
        tm = time.ctime()
        sql = "insert into hist(name, word, time) values('%s','%s','%s')" % (
            name, word, tm)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

    # 文本查询
    try:
        f = open(DICT_TEXT)
    except:
        c.send(b'FALL')
        return

    for line in f:
        tmp = line.split(' ')[0]
        if tmp > word:
            c.send(b'FALL')
            f.close()
            return
        elif tmp == word:
            c.send(b'OK')
            time.sleep(0.1)
            c.send(line.encode())
            f.close()
            insert_history()
            return
    c.send(b'FALL')
    f.close()


def do_hist(c, name, db):
    print('历史记录')
    cursor = db.cursor()
    sql = 'select * from hist where name="%s"' % name  # 限制条数可用limit
    cursor.execute(sql)
    r = cursor.fetchall()
    if not r:
        c.send(b'FALL')
        return
    else:
        c.send(b'OK')
    for i in r:
        time.sleep(0.1)
        msg = '%s    %s    %s' % (i[1], i[2], i[3])
        c.send(msg.encode())
    time.sleep(0.1)
    c.send(b'##')















if __name__ == '__main__':
    main()




















