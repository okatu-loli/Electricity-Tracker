package chromium

import (
	"encoding/base64"
	"log"
	"os"
)

func (chromium *Chromium) CaptureScreenshot(path string) bool {
	result := struct {
		Data string `json:"data"`
	}{}
	err := chromium.ExecuteMethod("Page.captureScreenshot", nil, &result)
	if err != nil {
		log.Println("捕获屏幕截图失败")
		return false
	}

	dist, _ := base64.StdEncoding.DecodeString(string(result.Data))
	f, err := os.OpenFile(path, os.O_RDWR|os.O_CREATE, os.ModePerm)
	if err != nil {
		log.Println("创建屏幕截图时出错", err)
		return false
	}
	_, err = f.Write(dist)
	if err != nil {
		log.Println("写入屏幕截图时出错", err)
		return false
	}
	err = f.Close()
	if err != nil {
		log.Println("结束写入屏幕截图时出错", err)
		return false
	}

	log.Println("保存屏幕截图", path)
	return true
}

func (chromium *Chromium) RunScript(script string) bool {
	//log.Println("执行JS脚本", script)
	_, _ = chromium.SendMethod("Runtime.enable", nil)

	paramsCompileScript := struct {
		Expression    string `json:"expression"`
		PersistScript bool   `json:"persistScript"`
		SourceURL     string `json:"sourceURL"`
	}{Expression: script, PersistScript: true, SourceURL: ""}
	resultCompileScript := struct {
		ScriptId string `json:"scriptId"`
	}{}
	err := chromium.ExecuteMethod("Runtime.compileScript", paramsCompileScript, &resultCompileScript)
	if err != nil {
		log.Println("JS脚本执行失败")
		return false
	}

	paramsRunScript := struct {
		ScriptId string `json:"scriptId"`
	}{ScriptId: resultCompileScript.ScriptId}
	err = chromium.ExecuteMethod("Runtime.runScript", paramsRunScript, nil)
	if err != nil {
		log.Println("JS脚本执行失败")
		return false
	}
	_, _ = chromium.SendMethod("Runtime.disable", nil)

	return true
}

func (chromium *Chromium) DoClick(selector string) {
	chromium.RunScript("document.querySelector(`" + selector + "`).click()")
}

func (chromium *Chromium) DoInput(selector string, text string) {
	chromium.RunScript(
		"var elem = document.querySelector(`" + selector + "`);" +
			"elem.value=`" + text + "`; " +
			"elem.dispatchEvent(new Event('input'));")
}

func (chromium *Chromium) WaitUrlLoadingFinish(url string) {
	_, _ = chromium.SendMethod("Network.enable", nil)

	paramRequestWillBeSent := struct {
		Request struct {
			Url string `json:"url"`
		} `json:"request"`
		RequestId string `json:"requestId"`
	}{}
	for {
		out, _ := chromium.ReceiveMethod(&paramRequestWillBeSent)
		if out == "Network.requestWillBeSent" {
			if paramRequestWillBeSent.Request.Url == url {
				break
			}
		}
	}

	paramLoadingFinished := struct {
		RequestId string `json:"requestId"`
	}{}
	for {
		out, _ := chromium.ReceiveMethod(&paramLoadingFinished)
		if out == "Network.loadingFinished" {
			if paramLoadingFinished.RequestId == paramRequestWillBeSent.RequestId {
				break
			}
		}
	}

	_, _ = chromium.SendMethod("Network.disable", nil)
	log.Println("页面加载完成")
}

func (chromium *Chromium) WaitUrlRequestResponse(url, requestHeader any, responseHeader any) (string, bool) {
	_, _ = chromium.SendMethod("Network.enable", nil)

	// 获取请求头
	paramRequestWillBeSent := struct {
		Request struct {
			Url     string `json:"url"`
			Headers any    `json:"headers"`
		} `json:"request"`
		RequestId string `json:"requestId"`
	}{}
	paramRequestWillBeSent.Request.Headers = requestHeader

	for {
		out, _ := chromium.ReceiveMethod(&paramRequestWillBeSent)
		if out == "Network.requestWillBeSent" {
			if paramRequestWillBeSent.Request.Url == url {
				break
			}
		}
	}

	// 获取响应头
	if responseHeader != nil {
		paramResponseReceived := struct {
			Response struct {
				Headers any `json:"headers"`
			} `json:"response"`
			RequestId string `json:"requestId"`
		}{}
		paramResponseReceived.Response.Headers = responseHeader

		for {
			out, _ := chromium.ReceiveMethod(&paramResponseReceived)
			if out == "Network.responseReceived" {
				if paramResponseReceived.RequestId == paramRequestWillBeSent.RequestId {
					break
				}
			}
		}
	}

	// 等待响应完成
	paramLoadingFinished := struct {
		RequestId string `json:"requestId"`
	}{}
	for {
		out, _ := chromium.ReceiveMethod(&paramLoadingFinished)
		if out == "Network.loadingFinished" {
			if paramLoadingFinished.RequestId == paramRequestWillBeSent.RequestId {
				break
			}
		}
	}

	// 获取响应体
	requestGetResponseBody := struct {
		RequestId string `json:"requestId"`
	}{RequestId: paramRequestWillBeSent.RequestId}
	responseGetResponseBody := struct {
		Body          string `json:"body"`
		Base64Encoded bool   `json:"base64Encoded"`
	}{}
	_ = chromium.ExecuteMethod("Network.getResponseBody", requestGetResponseBody, &responseGetResponseBody)

	_, _ = chromium.SendMethod("Network.disable", nil)
	return responseGetResponseBody.Body, responseGetResponseBody.Base64Encoded
}

func (chromium *Chromium) GetResponseBody(requestId string) string {
	param := struct {
		RequestId string `json:"requestId"`
	}{RequestId: requestId}
	result := struct {
		Body string `json:"body"`
	}{}
	err := chromium.ExecuteMethod("Network.getResponseBody", param, &result)
	if err != nil {
		return ""
	}

	return result.Body
}
