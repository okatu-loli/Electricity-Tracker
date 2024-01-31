package Decrypt_95598

import (
	"bytes"
	"image"
	"image/color"
	"image/png"
	"math/rand"
)

// 感谢群里大佬提供的代码
func SolveCaptcha(canvasSrcData []byte, offsetY int) (slideLen int) {
	canvasSrc, _ := png.Decode(bytes.NewReader(canvasSrcData))

	const YDelta = 60
	const YSize = 37
	baseImg, ok := canvasSrc.(*image.NRGBA)
	if !ok {
		panic("algo changed!")
	}

	offsetY += 9 // 到划框上边距
	var offsetX []int

	maxX := baseImg.Bounds().Max.X
	xCnt := 0

	// 定位左上角
	for x := 0; x < maxX; x++ {
		pt := baseImg.NRGBAAt(x, offsetY)
		Y, _, _ := color.RGBToYCbCr(pt.R, pt.G, pt.B)
		if Y > 255-YDelta {
			xCnt++
			if xCnt >= 13 {
				yCnt := 0
				baseX := x - xCnt + 1
				xCnt--
				for y := offsetY; y < offsetY+8; y++ { // 最左面有对应的高亮度竖条
					pt = baseImg.NRGBAAt(baseX, y)
					Y, _, _ = color.RGBToYCbCr(pt.R, pt.G, pt.B)
					if Y > 255-YDelta {
						yCnt++
					}
				}
				if yCnt < 8 {
					continue
				}
				yCnt = 0
				for x := baseX + 1; x < baseX+9; x++ { // 右下是黑色
					pt = baseImg.NRGBAAt(x, offsetY+1)
					Y, _, _ = color.RGBToYCbCr(pt.R, pt.G, pt.B)
					if Y < 255-YDelta {
						yCnt++
					}
				}
				if yCnt < 8 {
					continue
				}
				offsetX = append(offsetX, baseX)
			}
		}
	}
	if len(offsetX) == 0 {
		return -1
	}
	if len(offsetX) == 1 {
		return offsetX[0]
	}

	newSlice := make([]int, 0, len(offsetX))
	for _, baseX := range offsetX {
		xCnt := 0
		for x := baseX; x < baseX+13; x++ {
			pt := baseImg.NRGBAAt(x, offsetY+YSize)
			Y, _, _ := color.RGBToYCbCr(pt.R, pt.G, pt.B)
			if Y > 255-YDelta {
				xCnt++
				if xCnt >= 13 {
					break
				}
			}
		}
		if xCnt < 12 {
			continue
		}
		yCnt := 0
		for y := offsetY + 38 - 8; y < offsetY+YSize; y++ { // 最左面有对应的高亮度竖条
			pt := baseImg.NRGBAAt(baseX, y)
			Y, _, _ := color.RGBToYCbCr(pt.R, pt.G, pt.B)
			if Y > 255-YDelta {
				yCnt++
				if yCnt >= 8 {
					break
				}
			}
		}
		if yCnt < 7 {
			continue
		}

		newSlice = append(newSlice, baseX)
	}
	offsetX = newSlice
	if len(offsetX) == 0 {
		return -1
	}
	return offsetX[0]
}

func GenTracks(distance int) []int {
	/*
		生成非匀速的滑块位移路径
		参考 https://blog.csdn.net/La_vie_est_belle/article/details/130161844
	*/
	var tracks []int
	mid := float32(distance) * 3 / 5
	t := float32(0.2)
	v := float32(0)

	for current := float32(0); current < float32(distance); {
		var a float32
		if current < mid {
			a = float32(rand.Intn(2) + 3)
		} else {
			a = float32(rand.Intn(2) - 5)
		}
		v0 := v
		v = v0 + a*t
		move := v0*t + 1/2*a*t*t
		current += move
		tracks = append(tracks, int(current))
	}
	return tracks
}
