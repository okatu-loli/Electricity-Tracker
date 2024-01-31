package chromium

import (
	"github.com/gorilla/websocket"
	"os"
)

type Chromium struct {
	baseUrl              string
	executable           string
	args                 []string
	logFile              *os.File
	proc                 *os.Process
	webSocketDebuggerUrl string
	webSocketconnect     *websocket.Conn
	cdpMessageID         int
}
