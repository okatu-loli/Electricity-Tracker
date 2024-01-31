package main

import (
	"Electricity-Tracker/Decrypt_95598"
	"Electricity-Tracker/chromium"
	"log"
	"math/rand"
	"os"
	"strconv"
	"sync"
	"time"
)

// 单页面浏览器对象
var page chromium.Chromium

var threadPool sync.WaitGroup

func main() {
	startTime := time.Now()

	page.Init(9222, "chromium.log", "https://www.95598.cn/osgweb/login")
	page.Start()
	page.ConnectCdp()
	defer page.Exit()

	var captchaData Decrypt_95598.CaptchaData
	for {
		page.WaitUrlLoadingFinish("https://osg-apm.sgcc.com.cn:18084/track")

		page.DoClick("div.user")
		page.DoInput(`input[placeholder="请输入用户名/手机号/邮箱"]`, os.Getenv("95588_USER"))
		page.DoInput(`input[placeholder="请输入密码"]`, os.Getenv("95588_PASS"))
		page.DoClick(`#login_box > div.account-login > div:nth-child(1) > form > div.el-form-item > div > button`)

		var err error
		var keyCode Decrypt_95598.KeyCodeHeader
		msg, _ := page.WaitUrlRequestResponse("https://www.95598.cn/api/osg-web0004/open/c44/f05", &keyCode, nil)
		captchaData, err = Decrypt_95598.DecryptCaptchaData(keyCode, msg)
		if err == nil {
			break
		}

		_, _ = page.SendMethod("Page.reload", nil)
		log.Println("刷新页面")
	}

	log.Println("执行滑块验证")
	_ = doSlider(captchaData)
	log.Println("滑块验证结束")

	var keyCode Decrypt_95598.KeyCodeHeader
	var plainText []byte
	// 户号
	msg, _ := page.WaitUrlRequestResponse("https://www.95598.cn/api/osg-open-uc0001/member/c9/f02", &keyCode, nil)
	_ = Decrypt_95598.DecryptData(keyCode, msg, nil)
	plainText, _ = Decrypt_95598.ParseDecryptData(msg, keyCode.KeyCode)
	log.Println(string(plainText))
	// 电费使用量
	msg, _ = page.WaitUrlRequestResponse("https://www.95598.cn/api/osg-open-bc0001/member/c05/f01", &keyCode, nil)
	plainText, _ = Decrypt_95598.ParseDecryptData(msg, keyCode.KeyCode)
	log.Println(string(plainText))
	// 历史每月用电量
	msg, _ = page.WaitUrlRequestResponse("https://www.95598.cn/api/osg-open-bc0001/member/c01/f02", &keyCode, nil)
	plainText, _ = Decrypt_95598.ParseDecryptData(msg, keyCode.KeyCode)
	log.Println(string(plainText))

	endTime := time.Now()
	log.Printf("执行时间: %s\n", endTime.Sub(startTime))
}

func doSlider(captchaData Decrypt_95598.CaptchaData) error {
	BlockY, _ := strconv.Atoi(captchaData.BlockY)
	CanvasSrc, _ := Decrypt_95598.ParseBase64Img(captchaData.CanvasSrc)
	distance := int(float32(Decrypt_95598.SolveCaptcha(CanvasSrc, BlockY)-9) / 350.946 * 371)
	tracks := Decrypt_95598.GenTracks(distance)

	page.DomSetInspectedNode(page.DomGetDocument()["BODY"])
	slider := page.DomSearch("#slideVerify > div.slide-verify-slider > div > div")[0]
	sliderX, sliderY := chromium.GetCenterLocation(page.DomGetBoxModel(slider))

	page.SimpleMouseEvent("mouseMoved", sliderX, sliderY)
	time.Sleep(300 * time.Millisecond)
	page.SimpleMouseEvent("mousePressed", sliderX, sliderY)
	for _, value := range tracks {
		time.Sleep(66 * time.Millisecond)
		page.SimpleMouseEvent("mouseMoved", sliderX+value, sliderY+rand.Intn(11)-5)
	}
	time.Sleep(200 * time.Millisecond)
	//page.CaptureScreenshot("Debug.png")

	_ = page.ExecuteMethod("Network.enable", nil, nil)
	page.SimpleMouseEvent("mouseReleased", sliderX+distance, sliderY)
	var keyCode Decrypt_95598.KeyCodeHeader
	msg, _ := page.WaitUrlRequestResponse("https://www.95598.cn/api/osg-web0004/open/c44/f06", &keyCode, nil)
	return Decrypt_95598.DecryptData(keyCode, msg, nil)
}
