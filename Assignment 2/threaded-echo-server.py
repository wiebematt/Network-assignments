# This example is using Python 2.7
import socket
import thread
import sys

BUFFER_SIZE = 1024
DEFAULT_PORT = 80
GET_HEADER = "GET"
CONNECTION_CLOSE = "Connection: close\r\n"
HTTP_BAD_METHOD = "HTTP/1.1 405 HTTP_BAD_METHOD"
CACHE = []


def receive_request(connection):
    request_buffer = ''
    while "\r\n\r\n" not in request_buffer or "\n\n" not in request_buffer:
        request_buffer += connection.recv(BUFFER_SIZE)
    return request_buffer.split("\n") if "\n\n" in request_buffer else request_buffer.split("\r\n")


def parse_url(url):
    http_pos = url.find("://")
    webserver = url[(http_pos + 3):] if http_pos != -1 else url
    return webserver.split("/", 1)


def handler(connection):
    lines = receive_request(connection)
    header, url, httpv = lines[0].split(" ")
    if GET_HEADER not in header:
        connection.sendall(HTTP_BAD_METHOD)
    webserver, target_file = parse_url(url)
    proxy = create_connection(webserver, DEFAULT_PORT)
    lines = map(lambda x: CONNECTION_CLOSE if "Connection" in x else x, lines)
    request = GET_HEADER + " " + target_file + " " + httpv + ''.join(lines[1:])
    proxy.sendall(request)

    #     Receive new data from webserver
    response = "\n".join(receive_request(proxy))
    connection.sendall(response)
    proxy.close()


def create_connection(webserver, port):
    t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    t.bind((webserver, port))
    return t


if __name__ == '__main__':
    server_port = int(sys.argv[1])
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    s = create_connection(host_ip, server_port)
    s.listen(5)

    while True:
        conn, addr = s.accept()
        print 'Server connected by', addr,
        thread.start_new(handler, (conn,))
