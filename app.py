import configparser
import os
import sqlite3
import time
from datetime import datetime
from threading import Thread

import schedule
from flask import Flask, jsonify

from main import Main

app = Flask(__name__)


def get_db_connection():
    return sqlite3.connect('electricity.db')


def check_and_create_db():
    db_path = './electricity.db'
    if not os.path.isfile(db_path):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                create_table_string = "CREATE TABLE electricity (time REAL, expense REAL)"
                cursor.execute(create_table_string)
                print('数据库和表创建成功.')
        except Exception as e:
            print('创建数据库时遇到错误: ', str(e))


def run_main():
    # 获取当前时间
    current_time = time.time()
    current_date = datetime.utcfromtimestamp(current_time).date()

    # 尝试从数据库获取最新记录的日期和电费
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT time, expense FROM electricity ORDER BY time DESC LIMIT 1")
            last_record = cursor.fetchone()

            if last_record is not None:
                last_date = datetime.utcfromtimestamp(last_record[0]).date()

                # 如果最新记录的日期与当前日期相同，则返回当日的电费
                if last_date == current_date:
                    main = Main()
                    main.notify(float(last_record[1]))
                    return last_record[1]  # 返回当日电费
    except Exception as e:
        print("Error occurred:", e)
        return f"err: {e}"

    # 如果日期不同，则执行 main 函数
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    main = Main()
    amount = main.run()

    # 将新的记录插入数据库
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO electricity (time, expense) VALUES (?, ?)", (current_time, amount))
            conn.commit()
    except Exception as e:
        print("Error occurred:", e)

    return amount


@app.route('/')
def index():
    response = {
        "status": 200,
        "message": "欢迎访问!"
    }
    return jsonify(response), 200


@app.route('/electricity', methods=['GET'])
def get_electricity():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT time, expense FROM electricity ORDER BY time DESC LIMIT 1")
            record = cursor.fetchone()
            response = {
                "status": 200,
                "data": {"time": record[0], "expense": record[1]}
            }
            return jsonify(response), 200
    except Exception as e:
        response = {
            "status": 500,
            "message": "An error occurred: " + str(e)
        }
        return jsonify(response), 500


@app.route('/getelectricity', methods=['POST'])
def call_run_main():
    try:
        amount = run_main()
        response = {"status": "success", "message": f"成功获取电费：{amount}."}
        return jsonify(response), 200
    except Exception as e:
        response = {"status": "failure", "message": "发生了一个错误，请在重试时间结束后再尝试，具体错误: " + str(e)}
        return jsonify(response), 500


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    check_and_create_db()
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    _time = config.get('Notification', 'time')

    schedule.every().day.at(f"{_time}").do(run_main)

    t = Thread(target=run_schedule)
    t.start()

    app.run(host='0.0.0.0', port=5000)
