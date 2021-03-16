package Pkg

import "bytes"

func GetHost(url string) string {
	splitted := bytes.Split([]byte(url), []byte(":"))
	return string(splitted[0])
}
