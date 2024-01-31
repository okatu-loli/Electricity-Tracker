package chromium

import (
	"encoding/json"
	"errors"
	"github.com/gorilla/websocket"
	"log"
)

func (chromium *Chromium) Receive() ([]byte, error) {
	_, response, err := chromium.webSocketconnect.ReadMessage()
	if err != nil {
		log.Println("CDP响应接收失败", err)
		return nil, err
	}

	//if len(response) <= 64 {
	//	log.Println("接收CDP响应", len(response), string(response))
	//} else {
	//	log.Println("接收CDP响应", len(response), string(response[0:63]), "...")
	//}
	return response, nil
}

func (chromium *Chromium) Send(request []byte) error {
	//if len(request) <= 128 {
	//	log.Println("发送CDP请求", len(request), string(request))
	//} else {
	//	log.Println("发送CDP请求", len(request), string(request[0:127]), "...")
	//}

	err := chromium.webSocketconnect.WriteMessage(websocket.TextMessage, request)
	if err != nil {
		log.Println("CDP请求发送失败", err)
		return err
	}
	return nil
}

func (chromium *Chromium) SendMethod(method string, params any) (int, error) {
	request := struct {
		ID     int    `json:"id"`
		Method string `json:"method"`
		Params any    `json:"params"`
	}{ID: chromium.cdpMessageID, Method: method, Params: params}

	jsonStr, _ := json.Marshal(request)
	err := chromium.Send(jsonStr)
	if err != nil {
		return 0, err
	}
	chromium.cdpMessageID++
	return chromium.cdpMessageID - 1, nil
}

func (chromium *Chromium) SendMethodResponse(result any) (int, error) {
	response := struct {
		ID    int `json:"id"`
		Error struct {
			Code    int    `json:"code"`
			Message string `json:"message"`
			Data    string `json:"data"`
		} `json:"error"`
		Result any `json:"result"`
	}{ID: 0, Result: result}
	response.Error.Code = 0

	jsonData, err := chromium.Receive()
	if err != nil {
		return 0, err
	}

	err = json.Unmarshal(jsonData, &response)
	if err != nil {
		log.Println("解析响应数据失败", err)
		return 0, err
	}

	if response.Error.Code != 0 {
		log.Printf("非正常响应\nCode: %d\nMessage: %s\nData: %s\n",
			response.Error.Code,
			response.Error.Message,
			response.Error.Data)
		return response.ID, errors.New("非正常响应")
	}
	return response.ID, nil
}

func (chromium *Chromium) ReceiveMethod(params any) (string, error) {
	response := struct {
		Method string `json:"method"`
		Params any    `json:"params"`
	}{}
	if params == nil {
		response.Params = struct{}{}
	} else {
		response.Params = params
	}

	jsonData, err := chromium.Receive()
	if err != nil {
		return "", err
	}

	err = json.Unmarshal(jsonData, &response)
	if err != nil {
		log.Println("解析响应数据失败", err)
		return "", err
	}
	return response.Method, nil
}

func (chromium *Chromium) ExecuteMethod(method string, params any, result any) error {
	messageID, err := chromium.SendMethod(method, params)
	if err != nil {
		return err
	}

	for {
		checkID, err := chromium.SendMethodResponse(&result)
		if err != nil {
			return err
		}
		if checkID == messageID {
			break
		}
	}
	return nil
}
