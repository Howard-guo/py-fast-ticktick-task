#!/usr/bin/python
#! -*- coding: utf8 -*-
import json
import datetime
import tzlocal
import time
import requests
import os.path
import random
import re
import sys
import os
import pyperclip

BASE_URL = "https://www.dida365.com"
TASK_API_URL = BASE_URL + "/api/v2/task"
PROJECT_API_URL = BASE_URL + "/api/v2/projects"
LOGIN_URL = BASE_URL + "/api/v2/user/signon?wc=true&remember=true"
CFG = os.getcwd() + os.path.sep + ".ticktick"


def read_config():
    d = {}
    with open(CFG, 'r') as f:
        for line in f:
            [key, value] = line.strip().split("=", 1)
            d[key] = value
    return d

def write_config(cfg):
    with open(CFG, 'w+') as f:
        for k, v in cfg.items():
            f.write("{0}={1}\n".format(k, v))

def object_id(args=[]):
    if not args:
        args.extend([random.randint(0, 16777215), random.randint(0, 32766), random.randint(0, 16777215)])
    args[1] += 1
    if args[2] > 16777215:
        args[2] = 0
    return "{:08x}{:06x}{:04x}{:06x}".format(int(time.time()), args[0], args[1], args[2])


def generate_item(title, content, pid):
    tz = tzlocal.get_localzone()
    item = {}
    n = datetime.datetime.now().utcnow()
    item["modifiedTime"] = n.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0000"
    item["id"] = object_id()
    item["title"] = title
    item["priority"] = 1
    item["status"] = 0
    item["deleted"] = 0
    item["timeZone"] = tz.zone
    item["content"] = content
    item["sortOrder"] = 0
    item["projectId"] = pid

    d = datetime.datetime.now(tz)
    d = d.replace(hour=0, minute=0, second=0, microsecond=0)
    startDate = "{0}{1:%z}".format(d.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3], d)
    item["startDate"] = startDate
    item["dueDate"] = None
    item["items"] = []
    item["assignee"] = None
    item["progress"] = 0
    item["tags"] = []
    item["isAllDay"] = True
    item["reminder"] = None
    item["local"] = True
    item["isDirty"] = False
    return item

def generate_header(cookie=None):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:36.0) Gecko/20100101 Firefox/36.0",\
               "Accept-Language": "zh-CN,en-US;q=0.7,en;q=0.3",\
               "Referer": BASE_URL,
               "DNT": "1",
               "Accept": "application/json, text/javascript, */*; q=0.01",
               "Content-Type": "application/json; charset=UTF-8",
               "X-Requested-With": "XMLHttpRequest",
               "Accept-Encoding": "deflate"}
    if cookie:
        headers["Cookie"] = cookie
    return headers

def login(user, pwd):
    try:
        headers = generate_header()
        payload = json.dumps({"username": user, "password": pwd})
        r = requests.post(LOGIN_URL, headers=headers, data=payload)
        m = re.search("(t=\w+);", r.headers.get("Set-Cookie"))
        cfg = {"cookie": m.group(1)}
        write_config(cfg)
    except Exception as e:
        print("Login failed", e)
        return
    print("Login success")


def set_default_project(name):
    cfg = read_config()
    if not cfg.get("projectId") or not cfg.get("cookie"):
        print("please login first")
        return False

    try:
        headers = generate_header(cfg["cookie"])
        r = requests.get(PROJECT_API_URL, headers=headers)
        projects = json.loads(r.text)
        for item in projects:
            if item['name']==name:
                cfg = read_config()
                cfg['projectId'] = item['id']
                write_config(cfg)
                print("Set default project success")
                return
    except Exception as e:
        print("Set default project failed:", e)
        return
    print("Set default project failed")


def create_task(title, content=''):
    cfg = read_config()
    if not cfg.get("projectId") or not cfg.get("cookie"):
        print("please login first")
        return False

    if content == '#':
        content = pyperclip.paste()


    item = generate_item(title, content, cfg["projectId"])
    headers = generate_header(cfg["cookie"])
    payload = json.dumps(item)
    r = requests.post(TASK_API_URL, headers=headers, data=payload)
    return r.status_code == requests.codes.ok


if __name__=="__main__":
    argvLen = len(sys.argv)
    if argvLen < 2:
        print("param num error")
        sys.exit()


    if sys.argv[1] == "login":
        if argvLen == 4:
            login(sys.argv[2], sys.argv[3])  # .py login <mail> <pwd>
        else:
            print("login param num error")
    elif sys.argv[1] == "project":
        if argvLen == 3:
            set_default_project(sys.argv[2])  # .py project <projectName>
        else:
            print("set default project param num error")
    elif sys.argv[1] in ['/?', '-h', '--help', 'help']:
            print('''
        1.登录
          login <mail> <pwd>
        2.配置默认项目
          project <projectName>
        3.创建任务[只包含标题]
          <tasktitle>
        4.创建任务[标题+内容]
          <tasktitle> <taskcontent>
        5.创建任务[标题+剪切板内容]
          <tasktitle> #''')
    else:
        if argvLen == 2:
            create_task(sys.argv[1])  # .py <tasktitle>
        else:
            create_task(sys.argv[1], sys.argv[2])  # .py <tasktitle> <taskcontent>
        print("create task success")