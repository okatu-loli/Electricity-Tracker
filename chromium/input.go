package chromium

// mousePressed, mouseReleased, mouseMoved
func (chromium *Chromium) SimpleMouseEvent(event string, x int, y int) {
	params := struct {
		Type       string `json:"type"`
		X          int    `json:"x"`
		Y          int    `json:"y"`
		Button     string `json:"button"`
		ClickCount int    `json:"clickCount"`
	}{Type: event, X: x, Y: y, Button: "left"}
	if event == "mouseMoved" {
		params.ClickCount = 0
	} else {
		params.ClickCount = 1
	}

	_ = chromium.ExecuteMethod("Input.dispatchMouseEvent", params, nil)
}
