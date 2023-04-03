# WebServer with HTTP-Like Protocol

## Description

In this project, I implemented a HTTP-like server that provides key-value store services and a frequency counter service. The server consists of two components - One is custom protocol simplified from HTTP 1.1. It retains the basic request-response mechanism and the persistent connection feature of HTTP 1.1, but uses a different header format. Two, an interactive in-memory keyvalue store and a frequency counter implemented on top of this protocol.

The lowest-level layer of this server is the TCP socket interface. The server binds to a port, listens to the socket and accepts a new connection. it then parses and responds to client requests. After the client disconnects, the server listens to the socket again. The server can detect disconnection events reliably and support the persistent connection feature originated from HTTP 1.1.  

The port number is passed to the server as a command line argument. 

After establishing a new TCP connection with a client, the server should read a customized HTTP request from the socket, which consists of request headers and an optional request body. The server should parse the request and send the corresponding response. After a request-response cycle, the connection is persisted (i.e. not closing immediately), and the server waits for another request from the same client until a notification of socket disconnection.

The header format of this HTTP-like protocol is simplified such that a header is a string consisting of non-empty substrings delimited with whitespaces. Two consecutive whitespaces mark the end of a header. A header consists of at least two substrings, and the first two substrings (compulsory) contain information specific to requests or responses. Additional (and optional) substrings may follow. Every two substrings form a header field, where the first substring is the case-insensitive name of the header field, and the second is the value of this field.

The server can handle basic requests and response information, as well as the 'Content-Length' header field. 

For a request, the first two substrings (compulsory) are HTTP method and path, respectively. The HTTP method is case-insensitive, while path is case-sensitive. After these two substrings, optional header fields may follow, e.g., 'Content-Length' (case-insensitive) and its value (a non-negative integer) if there is a content body in the request. The header finally ends with two whitespaces. This is followed by the content body, if any.

For a response, the first two substrings (compulsory) are HTTP status code and description of the status code, respectively. Additional (and optional) substrings may follow, forming header fields.

The server should work properly even when requests are delivered in chunks of random sizes with delays between chunks. The server should be responsive and should process the requests and send back the response immediately upon receiving a complete request. The server should also handle data buffering well, including handling chunks that contain incomplete requests.

The Key-Value store is a dictionary data structure that supports insertion, update, retrieval, and deletion of key-value pairs, with keys functioning as pointers to the values.  For simplicity, we restrict keys to be case-sensitive ASCII strings in this project. Due to the use of Content-Length header, values can be any binary string. The server keeps all data in memory only and avoids accessing the disk.

The server supports the following key-value operations over the HTTP-like protocol:
1. Insertion and update
    (a) The HTTP request method is POST and the value to be inserted (or updated) constitutes the content body. There is also a ContentLength header indicating the number of bytes in the content body.
    (b) The server responds with a 200 OK status code after inserting or updating the value. The client always expects success statuses for insertions and updates.
2. Retrieval
    (a) The HTTP request method is GET, and there is no content body.
    (b) If the key does not exist in the key-value store, the server returns a 404 NotFound status code. Otherwise, the server returns a 200 OK code, the correct Content-Length header and the value data in the content body.
3. Deletion
    (a) The HTTP request method is DELETE, and there is no content body.
    (b) If the key does not exist, the server returns a 404 NotFound code. Otherwise, it deletes the key-value pair from the store and respond with a 200 OK code and the deleted value string as the content body. The Content-Length header is also sent accordingly.

A counter store is very similar to key-value store, except that it stores non-negative frequency count, instead of bytes value, of a particular counter key. For simplicity, it supports update, retrieval of counter values, with counter keys functioning as pointers to the frequency values. Counter keys are case-sensitive ASCII strings. Unlike key-value store, no content-length header is present in a POST request, while it is needed in the response to a GET request. The server keeps all data in memory only and avoid accessing the disk.

Note the keys in counter store is independent from the ones in key-value store, i.e. same key may appear in both stores and one stores bytes value while the other stores an integer. The server supports the following counter key operations over the HTTP-like protocol for a counter store:
1. Update
    (a) The HTTP request method is POST without any content body. The frequency value of a corresponding counter key is increased by 1. Any counter key not updated yet has frequency 0. Hence upon first update of a particular counter key, its frequency value becomes 1, and the next time 2, and so on.
    (b) The server responds with a 200 OK status code after updating the counter. The client always expects success status for updates.
2. Retrieval
    (a) The HTTP request method is GET, and there is no content body.
    (b) If the counter key was never updated before, corresponding frequency is 0. The server returns a 200 OK code, the correct Content-Length header and the frequency value in the content body without leading 0s.

## Testing

Make sure that your program and the test folder are in the same directory. Then you can run the following command to test your server program. 

``` 
bash test/WebServer.sh
```

By default, the script runs through all test cases. You can also choose to run a certain test case by specifying the case number in the command:

``` 
bash test/WebServer.sh 3
```

To stop a test, press `ctrl-c`. If pressing the key combination once does not work, hold the keys until the script exits