# TaskTonic/ttTonicStore/ttNetworking/ttHttpSockets.py

from .ttTcpSockets import TcpSocketHandler


class HttpServerHandler(TcpSocketHandler):
    """
    A lightweight, asynchronous HTTP server designed to receive
    webhooks from local IoT devices (like Shelly buttons or relays).
    """

    def __init__(self, port=8080, **kwargs):
        super().__init__(as_server=True, host='0.0.0.0', port=port, **kwargs)
        self.request_buffer = b''

    def rcv_data_conversion(self, bdata):
        """
        Parses the raw incoming TCP stream to extract the HTTP request line.
        """
        self.request_buffer += bdata

        # Check if the HTTP headers are complete (identified by a double CRLF)
        if b'\r\n\r\n' in self.request_buffer:
            headers_raw, body = self.request_buffer.split(b'\r\n\r\n', 1)

            # Decode the headers safely
            header_text = headers_raw.decode('utf-8', errors='ignore')
            header_lines = header_text.split('\r\n')

            # The first line is the Request Line (e.g., "GET /relay/0?turn=on HTTP/1.1")
            request_line = header_lines[0]
            parts = request_line.split(' ')

            if len(parts) >= 2:
                method = parts[0]
                url = parts[1]

                # Send a standard HTTP 200 OK back to the device to close the transaction
                response = b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK"
                self._send(response)

                # Reset the buffer for the next incoming request
                self.request_buffer = b''

                # Return the parsed data as a dictionary
                return [{'method': method, 'url': url}]

        return []

class HttpClientHandler(TcpSocketHandler):
    """
    A lightweight, asynchronous HTTP client designed to send quick
    commands to local IoT devices.
    """

    def __init__(self, host, port=80, **kwargs):
        super().__init__(as_client=True, host=host, port=port, **kwargs)
        self.target_host = host
        # self.response_buffer = b''

    def ttsc_connected__get(self, path="/"):
        request = f"GET {path} HTTP/1.1\r\nHost: {self.target_host}\r\nConnection: close\r\n\r\n"
        self.ttsc__send_data(request.encode('utf-8'))

    def rcv_data_conversion(self, bdata):
        return [{'body': bdata.decode('utf-8', errors='ignore')}]

        self.response_buffer += bdata

        # Nu zoeken we veilig in de gecombineerde buffer
        if b'\r\n\r\n' in self.response_buffer:
            headers, body = self.response_buffer.split(b'\r\n\r\n', 1)
            res = [{'body': body.decode('utf-8', errors='ignore')}]
            self.response_buffer = b''  # Reset na succes
            return res

        return []