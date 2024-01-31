package chromium

import (
	"encoding/json"
	"github.com/gorilla/websocket"
	"io"
	"log"
	"net/http"
	"strings"
)

func (chromium *Chromium) getCdpUrl() {
	resp, err := http.Get(chromium.baseUrl + "/json")
	if err != nil {
		log.Fatal("无法连接到chromium内核", err)
	}
	defer func(Body io.ReadCloser) {
		err := Body.Close()
		if err != nil {
			log.Println("chromium内核链接断开失败", err)
		}
	}(resp.Body)

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Fatal("无法读取chromium内核响应", err)
	}

	jsonStr := strings.ReplaceAll(strings.ReplaceAll(string(body), "[", ""), "]", "")
	// 解析Json字符串
	var pageInfo = struct {
		WebSocketDebuggerUrl string `json:"webSocketDebuggerUrl"`
	}{}
	err = json.Unmarshal([]byte(jsonStr), &pageInfo)
	if err != nil {
		log.Fatal("无法获取CDP链接", err)
	}

	chromium.webSocketDebuggerUrl = pageInfo.WebSocketDebuggerUrl
	log.Println("获取到CDP链接", pageInfo.WebSocketDebuggerUrl)
}

func (chromium *Chromium) ConnectCdp() {
	chromium.getCdpUrl()

	conn, _, err := websocket.DefaultDialer.Dial(chromium.webSocketDebuggerUrl, nil)
	if err != nil {
		log.Fatal("无法连接到CDP", err)
	}
	log.Println("连接到CDP成功")
	chromium.webSocketconnect = conn
	chromium.cdpMessageID = 0
}
