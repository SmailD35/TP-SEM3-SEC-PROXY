package Repeater

import (
	"ProxyServer/Pkg"
	"net/http"
	"net/http/httputil"
	"os"
	"strconv"
	"time"
)

const (
	delimReq="------------------REQUEST----------------------\n"
	delimResp="\n------------------RESPONSE----------------------\n"
)

func getFileName(method string, url string) string {
	return "./Repeater/static/"+strconv.Itoa(int(time.Now().Unix())) + "_" + method + "_" + url + ".txt"
}

func SaveReq(r *http.Request) (string, error) {
	if r == nil {
		return "", nil
	}

	file, err := os.Create(getFileName(r.Method, Pkg.GetHost(r.Host)))
	if err != nil{
		return "", err
	}

	defer file.Close()

	isBodyExist := true
	if r.Body == nil{
		isBodyExist = false
	}

	dumped := delimReq + "<{["
	tmp, _ := httputil.DumpRequest(r, isBodyExist)
	dumped += string(tmp) + "]}>" + delimResp

	_, _ = file.WriteString(dumped)

	return  getFileName(r.Method, Pkg.GetHost(r.Host)), nil
}

func SaveResp(r string, filename string) error{
	file, err := os.OpenFile(filename, os.O_APPEND|os.O_WRONLY, 0644)
	if err != nil{
		return err
	}
	defer file.Close()

	_, _ = file.WriteString(r)
	return nil
}
