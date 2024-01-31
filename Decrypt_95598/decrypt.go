package Decrypt_95598

import (
	"crypto/cipher"
	"encoding/base64"
	"encoding/json"
	"errors"
	"log"

	"github.com/tjfoc/gmsm/sm4"
)

type KeyCodeHeader struct {
	KeyCode string `json:"keyCode"`
}

type CaptchaData struct {
	CanvasSrc string `json:"canvasSrc"`
	Ticket    string `json:"ticket"`
	BlockSrc  string `json:"blockSrc"`
	BlockY    string `json:"blockY"`
}

func unPaddingLastGroup(plainText []byte) []byte {
	length := len(plainText)
	if length <= 0 {
		return nil
	}
	lastChar := plainText[length-1]
	number := int(lastChar)
	return plainText[:length-number]
}

func DecryptSM4(keyCode string, data string) ([]byte, error) {
	block, _ := sm4.NewCipher([]byte(keyCode[:16]))
	decryptData, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		return nil, err
	}
	cipher.NewCBCDecrypter(block, []byte(keyCode[:8]+keyCode[len(keyCode)-8:])).
		CryptBlocks(decryptData, decryptData)

	return decryptData, nil
}

func ParseDecryptData(jsonData string, keyCode string) ([]byte, error) {
	encryptData := struct {
		EncryptData string `json:"encryptData"`
		Sign        string `json:"sign"`
		Timestamp   string `json:"timestamp"`
	}{}
	err := json.Unmarshal([]byte(jsonData), &encryptData)
	if err != nil {
		log.Println("解析响应数据失败", err)
		return nil, err
	}

	data, _ := DecryptSM4(keyCode, encryptData.EncryptData)
	data = unPaddingLastGroup(data)

	return data, nil
}

func ParseResponse(jsonData []byte, data any) (int, string, error) {
	response := struct {
		Code    int    `json:"code"`
		Message string `json:"message"`
		Data    any    `json:"data"`
	}{Data: data}

	err := json.Unmarshal(jsonData, &response)
	if err != nil {
		log.Println("解析响应数据失败", err)
		return 0, "", err
	}

	return response.Code, response.Message, nil
}

func DecryptData(keyCodeHeader KeyCodeHeader, cipherText string, data any) error {
	plainText, err := ParseDecryptData(cipherText, keyCodeHeader.KeyCode)
	if err != nil {
		return err
	}

	//log.Println(string(plainText))

	code, msg, err := ParseResponse(plainText, &data)
	if err != nil {
		return err
	}
	if code != 1 {
		log.Printf("非正常响应\nCode: %d\nMessage: %s", code, msg)
		return errors.New("非正常响应")
	}

	return nil
}

func DecryptCaptchaData(keyCodeHeader KeyCodeHeader, jsonData string) (CaptchaData, error) {
	var captchaData CaptchaData

	err := DecryptData(keyCodeHeader, jsonData, &captchaData)
	if err != nil {
		return CaptchaData{}, err
	}

	return captchaData, nil
}

func ParseBase64Img(base64Data string) ([]byte, error) {
	const base64PngPrefix = `data:image/png;base64,`
	data, err := base64.StdEncoding.DecodeString(base64Data[len(base64PngPrefix):])
	if err != nil {
		return nil, err
	}

	return data, nil
}
