FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai
RUN apt-get update && apt-get install -y tzdata && apt-get clean
RUN apt-get update && apt-get install -y python3 python3-pip && apt-get clean
RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /usr/src/app/

COPY requirements.txt ./
RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt
RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir --upgrade --no-deps --force-reinstall schedule==1.2.1

RUN playwright install && playwright install-deps

COPY . ./
RUN chmod a+x app.py main.py

EXPOSE 5000

CMD ["/usr/bin/python", "app.py"]
