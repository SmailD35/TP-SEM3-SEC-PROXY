package Proxy

import (
	"ProxyServer/Repeater"
	"bytes"
	"fmt"
	"io"
	"net"
	"net/http"
	"strings"
	"time"
)




func ProxyHttps(w http.ResponseWriter, r *http.Request) {
	dest_conn, err := net.DialTimeout("tcp", r.Host, 10*time.Second)
	if err != nil {
		http.Error(w, err.Error(), http.StatusServiceUnavailable)
		return
	}
	w.WriteHeader(http.StatusOK)
	hijacker, ok := w.(http.Hijacker)
	if !ok {
		http.Error(w, "Hijacking not supported", http.StatusInternalServerError)
		return
	}
	client_conn, _, err := hijacker.Hijack()
	if err != nil {
		http.Error(w, err.Error(), http.StatusServiceUnavailable)
	}
	go transfer(dest_conn, client_conn)
	go transfer(client_conn, dest_conn)
}

func transfer(destination io.WriteCloser, source io.ReadCloser) {
	defer destination.Close()
	defer source.Close()
	buf := new(bytes.Buffer)
	_, _ = buf.ReadFrom(source)
	str:=buf.String()
	fmt.Println("HUI\n\n\n",str)
	io.Copy(destination, strings.NewReader(str))
	fmt.Println("\n\n\nkek")
}

func ProxyHttp(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("Send: %s\n", r.Host)
	resp, err := http.DefaultTransport.RoundTrip(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusServiceUnavailable)
		return
	}
	r.Header.Del("Proxy-Connection")
	r = fixRequest(r)
	_, fname := Repeater.SaveReq(r)
	defer resp.Body.Close()
	copyHeader(w.Header(), resp.Header)
	w.WriteHeader(resp.StatusCode)
	io.Copy(w, resp.Body)
	fmt.Printf("Get: %s\n", resp.Body)
	Repeater.SaveResp(resp, fname)
}

func copyHeader(dst, src http.Header) {
	for k, vv := range src {
		for _, v := range vv {
			dst.Add(k, v)
		}
	}
}

func fixRequest(r *http.Request) *http.Request {
	r.URL.Scheme = ""
	r.URL.Host = ""
	r.RequestURI = ""
	return r
}
