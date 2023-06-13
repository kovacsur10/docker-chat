import socket
import logging
import datetime
import mysql.connector # mysql-connector-python 

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
    logging.info("New token was inserted: {token}".format(token=token))

  # returns: (authenticated or not, token)
  def _authentication(self, databaseRef, username : str, password : str) -> tuple[bool, str]:
    cursor = databaseRef.cursor()
    try:
      cursor.execute("SELECT id FROM users WHERE username LIKE '{username}' AND password LIKE '{password}';".format(username=username, password=password))
      user = cursor.fetchone()
      if user is not None:
        # 2. token generálás és elmentés az adatbázisba
        newToken = "{username}-{datetime}".format(username=username, datetime=datetime.datetime.now()).replace(' ', '%')
        cursor.execute("DELETE FROM tokens WHERE user_id=%s;", (user[0],))
        cursor.execute("INSERT INTO tokens (user_id, token) VALUES (%s, %s);", (user[0], newToken))
        databaseRef.commit()
        return (True, newToken)
    except RuntimeError as ex:
      databaseRef.rollback()
      logging.error("Could not insert the token to the database. Error: {}".format(ex))
    return (False, "")

  def handleMessage(self, databaseRef):
    if self.buffer:
      try:
        [method, username, password] = self.buffer.split(' ')
        if method != 'LOGIN':
          self._sendError("Expected message: LOGIN.")
          raise RuntimeWarning("Erroneous message from user '{address}'. Closing the connection.".format(address=self.address))
        password = password[:-1]
      except Exception as err:
        self._sendError("Misformatted message.")
        logging.debug("Arrived message: {msg}".format(msg=self.buffer))
        logging.error("Erroneous message from user '{address}'. Closing the connection. Error: {err}".format(address=self.address, err=err))
        raise RuntimeWarning("Erroneous message from user '{address}'. Closing the connection.".format(address=self.address))

      authenticated, token = self._authentication(databaseRef, username, password)
      if authenticated:
        self._accept(token)
      else:
        self._sendError("Wrong username and/or password.")
        logging.error("Wrong username and/or password. Closing the connection.")
        raise RuntimeWarning("Wrong username and/or password. Closing the connection.")
    else:
      print('no data from {address}'.format(address=self.address))
      logging.info('No data from {address}, closing connection.'.format(address=self.address))
      raise RuntimeWarning("Client '{address}' closed the connection.".format(address=self.address))
  
  def close(self):
    self.connection.close()

class Server:
  def __init__(self, host, port):
    logging.info("Staring the logon server...")
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.host = host
    self.port = port

    # TODO: configból
    self.mysqlDb = mysql.connector.connect(
      host="mysql-server",
      user="adminuser",
      password="almafa1",
      database="chatdb"
    )

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
          connection.handleMessage(self.mysqlDb)
      except Warning as warn:
        logging.info(warn)
      finally:
        connection.close()

# client -> server: LOGIN <username|nem tartalmazhat spacet> <password>\n
# server -> client: ACCEPT\n
# server -> client: TOKEN <token>\n
# server -> client: ERROR <message>\n

if __name__ == "__main__":
  logging.basicConfig(filename='logon.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s:%(message)s', encoding='utf-8')

  server = Server('0.0.0.0', 10000)
  server.start()