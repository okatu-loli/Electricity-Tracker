<img src="https://github.com/okatu-loli/Baoding-Electricity-Tracker/assets/53247097/77e06c3d-d2c2-4ade-b386-5acd15b034af" width=512px/>

# Electricity-Tracker

Electricity-Tracker是一个基于Python编写的自动化程序，能够帮助用户查询每日电费，理论支持查询全国的电费，同时支持通过飞书和ServerChan等平台发送电费通知。

**项目已恢复，功能可正常使用**
**欢迎加入QQ群交流：361997678**
## 功能介绍

- **自动化查询**：自动定时登录网页，获取电费数据，无需人工干预。
- **数据API**：通过Flask Web服务器，提供API接口，可以随时查询当前电费。
- **阈值通知**：当电费低于用户设定的阈值时，程序会自动发送通知。
- **执行通知**：可以设定在每次查询执行后发送通知，无论电费是否达到阈值。
- **多平台支持**：目前支持飞书和ServerChan两种通知方式，未来可能会支持更多平台。

## 使用方法

1. 重命名 `config.ini.example` 改为  `config.ini` ，根据注释修改配置文件。
2. 运行 `app.py` 文件，启动Web服务器。
3. 访问 `http://localhost:5000/electricity` 接口，获取最新的电费数据。
4. 也可以单独执行`main.py`文件，这将不会有定时任务和API的功能。
5. 设定好通知时间、阈值等，程序将按照这些配置进行工作。

## 项目依赖
Python3.10  
依赖安装：
```bash
pip install -r requirements.txt
```

## 待办事项列表

- [ ] 适配 Bark
- [ ] 编写青龙脚本

## 更新日志：
2023.07.14:  
添加MQTT支持，实现多渠道消息推送，详见PR [#1](https://github.com/okatu-loli/Baoding-Electricity-Tracker/pull/1) 感谢[@sunshinenny](https://github.com/sunshinenny)

2023.08.19:  
增加Webhook支持，详见 [#2](https://github.com/okatu-loli/Baoding-Electricity-Tracker/pull/2) 感谢[@marvyn](https://github.com/marvyn)

## 相关链接：
- [ddddocr requirements](https://github.com/sml2h3/ddddocr/blob/master/ddddocr/requirements.txt)
- [Pillow deprecations](https://pillow.readthedocs.io/en/stable/deprecations.html#constants)
- [ddddocr Pull Request #126](https://github.com/sml2h3/ddddocr/pull/126)



## 开源许可证

本项目采用MIT许可证，欢迎自由使用、分发和修改。

## 联系我们

如有使用问题或者建议，欢迎联系我。
