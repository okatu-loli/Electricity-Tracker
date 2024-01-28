<img src="https://github.com/okatu-loli/Baoding-Electricity-Tracker/assets/53247097/77e06c3d-d2c2-4ade-b386-5acd15b034af" width=512px/ alt="logo">

# Electricity-Tracker

Electricity-Tracker是一个基于Python编写的自动化程序，能够帮助用户查询每日电费，理论支持查询全国的电费，同时支持通过飞书和ServerChan等平台发送电费通知。

**因为一些积重难返的问题，项目主线暂停开发，并正在使用go语言重构，开发进度可以查看[go](https://github.com/okatu-loli/Electricity-Tracker/tree/go)分支**
**欢迎加入QQ群交流：361997678**
## 功能介绍

- **自动化查询**：自动定时登录网页，获取电费数据，无需人工干预。
- **数据API**：通过Flask Web服务器，提供API接口，可以随时查询当前电费。
- **阈值通知**：当电费低于用户设定的阈值时，程序会自动发送通知。
- **执行通知**：可以设定在每次查询执行后发送通知，无论电费是否达到阈值。
- **多平台支持**：目前支持飞书和ServerChan两种通知方式，未来可能会支持更多平台。

## 使用方法
本项目有两种部署方式，选择其一部署即可：
### 本地部署
1. 克隆本项目到本地
2. 重命名 `config.ini.example` 改为  `config.ini` ，根据注释修改配置文件。
3. 运行 `app.py` 文件，启动Web服务器。
4. 也可以单独执行`main.py`文件，这将不会有定时任务和API的功能。

### Docker部署
1. 拉取Docker镜像
    ```bash
    docker pull okatuloli/electricity-tracker
    ```
2. 运行Docker容器，并将本地的配置文件挂载到容器内
    ```bash
    docker run -v /path/to/config.ini:/usr/src/app/config.ini -p 5000:5000 okatuloli/electricity-tracker 
    ```
    **请注意，你需要将 /path/to/config.ini 这部分改为你实际的 config.ini 文件路径。**

## 使用方法

发起 HTTP 请求到以下URL来使用该服务:
- `GET http://localhost:5000/electricity`: 获取最新的电费数据。
- `POST http://localhost:5000/getelectricity`: 强制检查电费并更新到数据库。

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

## 开源许可证

本项目采用MIT许可证，欢迎自由使用、分发和修改。

## 联系我们

如有使用问题或者建议，欢迎联系我。
