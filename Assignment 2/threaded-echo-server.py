# This example is using Python 2.7
import socket
import thread
import sys

BUFFER_SIZE = 1024
DEFAULT_PORT = 80
GET_HEADER = "GET"
HTTP_VERSION = "HTTP/1.1"
CONNECTION_CLOSE = "Connection: close\r\n"
HTTP_BAD_METHOD = "HTTP/1.1 405 HTTP_BAD_METHOD"
CACHE = []


def receive_request(conn):
    request_buffer = ''
    while "\r\n\r\n" not in request_buffer or "\n\n" not in request_buffer:
        request_buffer += conn.recv(BUFFER_SIZE)
    return request_buffer.split("\n") if "\n\n" in request_buffer else request_buffer.split("\r\n")


def parse_url(url):
    http_pos = url.find("://")
    if http_pos != -1:
        webserver = url[(http_pos + 3):]
    else:
        webserver = url
    file_pos = webserver.find("/")
    target_site = webserver[:file_pos]
    target_file = webserver[file_pos:]
    return target_file, target_site


def handler(conn):
    lines = receive_request(conn)
    header, url, httpv = lines[0].split(" ")
    if GET_HEADER not in header:
        conn.sendall(HTTP_BAD_METHOD)
    webserver, target_file = parse_url(url)
    proxy = create_connection(webserver, DEFAULT_PORT)
    request = GET_HEADER + " " + target_file + " " + HTTP_VERSION + "\r\n" + CONNECTION_CLOSE + ''.join(lines[1:])
    proxy.sendall(request) \
 \
 \
#     Recieve new data


def create_connection(webserver, port):
    t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    t.connect((webserver, port))
    return t


def main():
    server_port = sys.argv[1]
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    s = create_connection(host_ip, server_port)
    s.listen(5)

    while True:
        conn, addr = s.accept()
        print 'Server connected by', addr,
        thread.start_new(handler, (conn,))
