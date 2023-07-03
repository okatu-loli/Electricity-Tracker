# Baoding-Electricity-Tracker

Baoding-Electricity-Tracker是一个基于Python编写的自动化程序，能够帮助用户查询河北省保定市的每日电费，同时支持通过飞书和ServerChan等平台发送电费通知。

## 功能介绍

- **自动化查询**：自动定时登录网页，获取电费数据，无需人工干预。
- **数据API**：通过Flask Web服务器，提供API接口，可以随时查询当前电费。
- **阈值通知**：当电费低于用户设定的阈值时，程序会自动发送通知。
- **执行通知**：可以设定在每次查询执行后发送通知，无论电费是否达到阈值。
- **多平台支持**：目前支持飞书和ServerChan两种通知方式，未来可能会支持更多平台。

## 使用方法

1. 修改配置文件 `config.ini` ，填入自己的账号密码、通知配置、[飞书](https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot)和[ServerChan](https://sct.ftqq.com/sendkey)的密钥。
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
## 注意事项

由于 `ddddocr` 项目长时间未更新，且其未明确指定 `Pillow` 库的版本，项目和最新版本的 `Pillow` 出现了兼容性问题。因此，**强烈建议您使用Python 3.10版本**来运行本项目，以避免可能出现的兼容性问题。

目前这个问题已经被第三方开发者修复，我们正在等待原作者合并PR。

相关链接：
- [ddddocr requirements](https://github.com/sml2h3/ddddocr/blob/master/ddddocr/requirements.txt)
- [Pillow deprecations](https://pillow.readthedocs.io/en/stable/deprecations.html#constants)
- [ddddocr Pull Request #126](https://github.com/sml2h3/ddddocr/pull/126)



## 开源许可证

本项目采用MIT许可证，欢迎自由使用、分发和修改。

## 联系我们

如有使用问题或者建议，欢迎联系我。
