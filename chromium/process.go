package chromium

import (
	"log"
	"os"
	"strconv"
)

func (chromium *Chromium) Init(port int, logPath string, url string) {
	chromium.baseUrl = "http://127.0.0.1:" + strconv.Itoa(port)
	chromium.executable = "chromium/chrome-headless-shell-win64/chrome-headless-shell.exe"
	chromium.args = []string{
		"--disable-gpu",
		"--window-size=1920,1080",
		"--remote-debugging-port=" + strconv.Itoa(port),
		url,
	}

	logFile, err := os.Create(logPath)
	if err != nil {
		log.Fatal("日志文件打开失败", err)
	}
	chromium.logFile = logFile
}

func (chromium *Chromium) Start() {
	cmd := chromium.executable
	for _, arg := range chromium.args {
		cmd += " " + arg
	}
	log.Println("启动chromium内核", cmd)

	proc, err := os.StartProcess(chromium.executable, chromium.args, &os.ProcAttr{
		Files: []*os.File{nil, nil, chromium.logFile},
	})
	if err != nil {
		log.Fatal("chromium内核启动失败", err)
	}

	for { // 等待chromium内核启动
		fileInfo, _ := chromium.logFile.Stat()
		fileSize := fileInfo.Size()
		if fileSize != 0 {
			break
		}
	}

	log.Println("chromium内核启动成功 PID:", proc.Pid)
}

func (chromium *Chromium) Exit() {
	var err error
	err = chromium.logFile.Close()
	if err != nil {
		log.Println("日志文件关闭出错", err)
	}
	err = chromium.webSocketconnect.Close()
	if err != nil {
		log.Println("CDP链接断开出错", err)
	}
}
