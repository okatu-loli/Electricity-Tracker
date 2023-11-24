import configparser
import time
from threading import Thread

import schedule
from flask import Flask

from main import Main

app = Flask(__name__)


def run_main():
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    retry_times = int(config.get('Retry', 'retry_times'))
    retry_interval = int(config.get('Retry', 'retry_interval'))

    main = Main()
    amount = main.run(retry_times=retry_times, retry_interval=retry_interval)
    with open('electricity.txt', 'w') as file:
        file.write(str(amount))


@app.route('/')
def index():
    return '欢迎访问!'


@app.route('/electricity')
def get_electricity():
    try:
        with open('electricity.txt', 'r') as file:
            amount = file.read()
        return amount
    except Exception as e:
        return {"error": str(e)}, 500


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
