import configparser
import subprocess
import time
from threading import Thread

import schedule
from flask import Flask

app = Flask(__name__)


def run_main():
    subprocess.run(['python', 'main.py'])
    print("main.py 执行成功")


@app.route('/')
def index():
    return '欢迎访问!'


@app.route('/electricity')
def get_electricity():
    with open('electricity.txt', 'r') as file:
        amount = file.read()
    return amount


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    time = config.get('Notification', 'time')

    # 设定每天定时执行run_main函数
    schedule.every().day.at(f"{time}").do(run_main)

    # 创建并启动线程，用于运行schedule
    t = Thread(target=run_schedule)
    t.start()

    app.run(host='0.0.0.0', port=5000)
