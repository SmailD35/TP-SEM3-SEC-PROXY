import os
import socket
import ssl
import subprocess


def get_decision():
    print(' To view request''s list enter: "l"')
    print(' To view/modify certain request enter: "v {%filename%}"')
    print(' To resend certain request enter: "r {%filename%}"')
    print(' To try SQL injection: "i {%filename%}"')
    print(' To exit enter: "q"')
    decision = input()
    return decision


def indexes_for_insert_symbols_get_params(content: str):
    end = 0
    indexes = []
    while 1:
        pos = content.find('=', end + 2)
        if pos == -1:
            break

        end = content.find('&', end + 2)
        if end == -1:
            end = content.find(' ', pos)
            indexes.append(end)
            break
        indexes.append(end)
    return indexes


def indexes_for_insert_symbols_post_params(content: str):
    data = content.split("\n\n")[0]
    super = len(data) + 2
    content = content.split("\n\n")[-1]
    end = 0
    indexes = []
    while 1:
        pos = content.find('=', end + 2)
        if pos == -1:
            break

        end = content.find('&', end + 2)
        if end == -1:
            indexes.append(super + len(content))
            break
        indexes.append(super + end)
    return indexes


def get_list():
    for root, dirs, files in os.walk("./static"):
        for filename in files:
            print("     ->" + filename)


def view(file):
    subprocess.call(['nano', file])


def get_file_name(command):
    x = command.split()
    return x[len(x) - 1]


def make_https_request(host, data):
    port = 443
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ssl_sock = ssl.wrap_socket(s)
        ssl_sock.connect((host, port))
        ssl_sock.sendall(data.encode())
        data = ssl_sock.recv(1024)

    return data.decode()


def make_http_request(host, data):
    port = 80
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ssl_sock = s
        ssl_sock.connect((host, port))
        ssl_sock.sendall(data.encode())
        data = ssl_sock.recv(1024)

    return data.decode()


def resend(file):
    f = open(file, 'r')
    content = f.read()
    data = ''
    req = get_request_from_file(content)
    if content.find('Host:') != -1:
        data = make_https_request(get_host_from_file_https(content), req)
    else:
        print("Request\n\n" + req + "Response\n\n")
        data = make_http_request(get_host_from_file_http(content), req)
    print(data)


def insert_symbols_by_one_and_send(content: str, indexes: list, symbol: str):
    if content.find('Host:') != -1:
        standard = make_https_request(get_host_from_file_https(content), content)
    else:
        standard = make_http_request(get_host_from_file_http(content), content)
    for i in indexes:
        data = content[:i] + symbol + content[i:]
        if content.find('Host:') != -1:
            resp = make_https_request(get_host_from_file_https(data), data)
        else:
            resp = make_http_request(get_host_from_file_http(data), data)
        if len(standard) != len(resp):
            print("SQL injection found: " + data)


def find_sql_injection(file: str):
    f = open(file, 'r')
    content = f.read()
    content = get_request_from_file(content)
    if content.find('GET') == -1:
        index = indexes_for_insert_symbols_post_params(content)
    else:
        index = indexes_for_insert_symbols_get_params(content)

    insert_symbols_by_one_and_send(content, index, "\'")
    insert_symbols_by_one_and_send(content, index, "\"")


def get_host_from_file_http(content: str):
    pos = content.find('//') + 2
    host = ''
    while content[pos] != '/':
        host += content[pos]
        pos += 1
    return host


def get_host_from_file_https(content: str):
    pos = content.find('Host: ') + 6
    host = ''
    while content[pos] != '\n':
        host += content[pos]
        pos += 1
    return host


def get_request_from_file(content: str):
    pos = content.find('<{[') + 3
    req = ''
    while content[pos] != ']' and content[pos + 1] != '}' and content[pos + 2] != '>':
        req += content[pos]
        pos += 1
    return req


# main

print("Welcome to hacker_master!")
while True:
    r = get_decision()
    if r == 'q':
        exit(0)
    if r == 'l':
        get_list()
    if r[0] == 'v':
        view('./static/' + get_file_name(r))
    if r[0] == 'r':
        resend('./static/' + get_file_name(r))
    if r[0] == 'i':
        find_sql_injection('./static/' + get_file_name(r))
    else:
        print('unknown command')
