import socket
import logging


# 1. Fogad kliens csatlakozasi kerelmeket.
# 2. Hitelesiti a kerelmeket. Vagy elutasitja vagy elfogadja.
# 3. Az elfogadott kerelmeket konyveli az adatbazisban.

class Connection:
  def __init__(self, conn, address):
    self.connection = conn # file descriptor
    self.address = address

    print('Connection from {address}'.format(address=address))
    logging.info('Connection from {address}'.format(address=address))
    
  def getMessage(self):
    logging.debug('Receiving from {addr}.'.format(addr=self.address))
    max_len = 255
    data = self.connection.recv(max_len)
    self.buffer = data.decode('utf-8')
    while '\n' not in self.buffer and len(self.buffer) < max_len and data:
      data = self.connection.recv(max_len)
      self.buffer = self.buffer + data.decode('utf-8')
    print('received {msg}'.format(msg=self.buffer))
    logging.debug('Received from {addr} message: {msg}.'.format(msg=self.buffer, addr=self.address))
    
  def _sendError(self, msg : str):
    self.connection.sendall(("ERROR {msg}\n".format(msg=msg)).encode())

  def _accept(self, token : str):
    self.connection.sendall("ACCEPT\nTOKEN {token}\n".format(token=token).encode())

  # returns: (authenticated or not, token)
  def _authentication(self, username : str, password : str) -> tuple[bool, str]:
    return (False, "") # TODO

  def handleMessage(self):
    if self.buffer:
      try:
        [method, username, password] = self.buffer.split(' ')
        if method != 'LOGIN':
          self._sendError("Expected message: LOGIN.")
          raise RuntimeWarning("Erroneous message from user '{address}'. Closing the connection.".format(address=self.address))
        password = password[:-1]

        authenticated, token = self._authentication(username, password)
        if authenticated:
          self._accept(token)
        else:
          self._sendError("Wrong username and/or password.")

      except Exception as err:
        self._sendError("Misformatted message.")
        logging.debug("Arrived message: {msg}".format(msg=self.buffer))
        logging.error("Erroneous message from user '{address}'. Closing the connection. Error: {err}".format(address=self.address, err=err))
        raise RuntimeWarning("Erroneous message from user '{address}'. Closing the connection.".format(address=self.address))
    else:
      print('no data from {address}'.format(address=self.address))
      logging.info('No data from {address}, closing connection.'.format(address=self.address))
      raise RuntimeWarning("Client '{address}' closed the connection.".format(address=self.address))
  
  def close(self):
    self.connection.close()

class Server:
  def __init__(self, host, port):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.host = host
    self.port = port

    # Bind the socket to the port
    server_address = (host, port)
    logging.info('Starting logon server on {host}:{port}.'.format(host=server_address[0], port=server_address[1]))
    print('Starting logon server on {host}:{port}.'.format(host=server_address[0], port=server_address[1]))
    self.sock.bind(server_address)
  
  def start(self):
    # Listen for incoming connections
    self.sock.listen(1)

    while True:
      # Wait for a connection
      print('waiting for a connection')
      logging.debug('Waiting for a connection.')
      connFd, client_address = self.sock.accept()
      connection = Connection(connFd, client_address)
      try:
        # Receive the data in small chunks and retransmit it
        while True:
          connection.getMessage()
          connection.handleMessage()
      except Warning as warn:
        logging.info(warn)
      finally:
        connection.close()

# client -> server: LOGIN <username|nem tartalmazhat spacet> <password>\n
# server -> client: ACCEPT\n
# server -> client: TOKEN <token>\n
# server -> client: ERROR <message>\n

if __name__ == "__main__":
  logging.basicConfig(filename='logon.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s:%(message)s', encoding='utf-8')

  server = Server('localhost', 10000)
  server.start()