package chromium

type NodeTree struct {
	NodeId   int        `json:"nodeId"`
	NodeName string     `json:"nodeName"`
	Children []NodeTree `json:"children"`
}

type NodeMap map[string]int

type BoxModel struct {
	Content []int `json:"content"`
	Padding []int `json:"padding"`
	Border  []int `json:"border"`
	Margin  []int `json:"margin"`
	Width   int   `json:"width"`
	Height  int   `json:"height"`
}

func traverseTree(node NodeTree, nodes *NodeMap) {
	(*nodes)[node.NodeName] = node.NodeId

	// 遍历子节点
	for _, child := range node.Children {
		traverseTree(child, nodes)
	}
}

func (chromium *Chromium) DomGetDocument() NodeMap {
	result := struct {
		Root NodeTree `json:"root"`
	}{}
	err := chromium.ExecuteMethod("DOM.getDocument", nil, &result)
	if err != nil {
		return nil
	}

	nodes := make(NodeMap)
	traverseTree(result.Root, &nodes)

	return nodes
}

// https://chromedevtools.github.io/devtools-protocol/tot/DOM/#method-setInspectedNode
// Enables console to refer to the node with given id via $x
func (chromium *Chromium) DomSetInspectedNode(nodeId int) {
	param := struct {
		NodeId int `json:"nodeId"`
	}{NodeId: nodeId}
	_, _ = chromium.SendMethod("DOM.setInspectedNode", param)
}

func (chromium *Chromium) DomSearchCount(query string) int {
	param := struct {
		Query string `json:"query"`
	}{Query: query}
	result := struct {
		ResultCount int `json:"resultCount"`
	}{}
	err := chromium.ExecuteMethod("DOM.performSearch", param, &result)
	if err != nil {
		return -1
	}
	return result.ResultCount
}

func (chromium *Chromium) DomSearch(query string) []int {
	paramsPerformSearch := struct {
		Query string `json:"query"`
	}{Query: query}
	resultPerformSearch := struct {
		SearchId    string `json:"searchId"`
		ResultCount int    `json:"resultCount"`
	}{}
	err := chromium.ExecuteMethod("DOM.performSearch", paramsPerformSearch, &resultPerformSearch)
	if err != nil || resultPerformSearch.ResultCount < 1 {
		return nil
	}

	paramsGetSearchResults := struct {
		SearchId  string `json:"searchId"`
		FromIndex int    `json:"fromIndex"`
		ToIndex   int    `json:"toIndex"`
	}{SearchId: resultPerformSearch.SearchId, FromIndex: 0, ToIndex: resultPerformSearch.ResultCount}
	resultGetSearchResults := struct {
		NodeIds []int `json:"nodeIds"`
	}{}
	err = chromium.ExecuteMethod("DOM.getSearchResults", paramsGetSearchResults, &resultGetSearchResults)
	if err != nil {
		return nil
	}

	return resultGetSearchResults.NodeIds
}

func (chromium *Chromium) DomGetBoxModel(nodeId int) BoxModel {
	param := struct {
		NodeId int `json:"nodeId"`
	}{NodeId: nodeId}
	result := struct {
		Model BoxModel `json:"model"`
	}{}
	_ = chromium.ExecuteMethod("DOM.getBoxModel", param, &result)
	return result.Model
}

func GetCenterLocation(boxModel BoxModel) (int, int) {
	x := boxModel.Content[0] + boxModel.Width/2
	y := boxModel.Content[1] + boxModel.Height/2
	return x, y
}
