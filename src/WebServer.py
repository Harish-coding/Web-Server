## file contains the implementation of webserver

from socket import *
import sys

port_number = int(sys.argv[1])

# dictionary for key_value service
key_value = {}

# dictionary for counter service
counter = {}



# define a header extractor method to find and return the method, and relevant information

def header_extr(header):

    info = ()
    
    ## update
    header_array = header.split(b" ")
    content_length_index = -1

    # all the 1st substring of header fields are uppercase strings
    index = 0
    while index < len(header_array):
        header_array[index] = header_array[index].decode().upper()
        if header_array[index] == "CONTENT-LENGTH":
            content_length_index = index
        index += 2

    # add the method
    info += (header_array[0],)

    # find which service dictionary
    service_substring = header_array[1][1:]
    pos = service_substring.find(b"/")
    key = ()

    if b"key" in service_substring:
        info += ("key_value",)
        key = (service_substring[pos + 1:],)


    if b"counter" in service_substring:
        info += ("counter",)
        key = (service_substring[pos + 1:],)

    info += key

    body_length = 0
    if content_length_index != -1:
        body_length = int(header_array[content_length_index + 1])

    info += (body_length,)

    return info



# http responses 

class http_response:
    def __init__(self):
        pass

    @staticmethod
    def not_found():
        return b"404 NotFound  "

    @staticmethod
    def okay():
        return b"200 OK  "

    @staticmethod
    def okay_with_body(content):
        length = len(content)
        return b"200 OK content-length " + bytes(str(length).encode()) + b"  " + content



# to process http requests

class http_methods:
    def __init__(self):
        pass

    @staticmethod
    def get(service, key):

        response = b""

        if service == "key_value":
            try: 
                content = key_value[key]
                response = http_response.okay_with_body(content)
            except KeyError:
                response = http_response.not_found()

        if service == "counter":
            try:
                content = counter[key]
                response = http_response.okay_with_body(bytes(str(content).encode()))
            except KeyError:
                counter[key] = 0
                content = counter[key]
                response = http_response.okay_with_body(bytes(str(content).encode()))

        return response
       

    @staticmethod
    def delete(service, key):
        message = http_methods.get(service, key)

        if message == b"404 NotFound  ":
            return message

        key_value.pop(key)
        return message

    @staticmethod
    def post(service, key, content):
        if service == "key_value":
            key_value[key] = content

        if service == "counter":
            try:
                counter[key] = counter[key] + 1
            except KeyError:
                counter[key] = 1

        return http_response.okay()
    


# Create a socket

server_socket = socket(AF_INET, SOCK_STREAM)

server_socket.bind(('', port_number))

# listen for a connection
server_socket.listen()
connection_socket = server_socket.accept()[0]

packet = b""

while True:

    while b"  " not in packet:
        receive = connection_socket.recv(1024)
        packet += receive
        if len(packet) == 0 and len(receive) == 0:
            connection_socket.close()
            connection_socket = server_socket.accept()[0]
        
    pos = packet.find(b"  ")
    header = packet[:pos]
    packet = packet[pos + 2:]  # update the content after removing that header


    # process header and body, send respose
    method, service, key, content_len = header_extr(header)


    packet_len = len(packet)

    def post(service, key):
        global packet
        content = b""
        if packet_len > content_len:
            content = packet[:content_len]
            packet = packet[content_len:]

        else:
            req_len = content_len - packet_len
            while req_len > 0:
                temp = connection_socket.recv(10)
                packet += temp
                req_len -= len(temp)
            content = packet[:content_len]
            packet = packet[content_len:]

        return http_methods.post(service, key, content)

    methods = {"GET": lambda:http_methods.get(service, key), 
               "POST": lambda:post(service, key), 
               "DELETE": lambda:http_methods.delete(service, key)}

    response_message = methods[method]()

    connection_socket.send(response_message)

