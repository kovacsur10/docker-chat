import socket
import logging

# 1. Fogad kliens csatlakozasi kerelmeket.
# 2. Hitelesiti a kerelmeket. Vagy elutasitja vagy elfogadja.
# 3. Az elfogadott kerelmeket konyveli az adatbazisban.

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
      connection, client_address = self.sock.accept()
      try:
        print('Connection from {address}'.format(address=client_address))
        logging.info('Connection from {address}'.format(address=client_address))

        # Receive the data in small chunks and retransmit it
        while True:
          data = connection.recv(16)
          print('received {!r}'.format(data))
          logging.info('Received {!r}.'.format(data))
          if data:
            print('sending data back to the client')
            logging.debug('Sending data back to the client.')
            connection.sendall(data)
          else:
            print('no data from {address}'.format(address=client_address))
            logging.info('No data from {address}, closing connection.'.format(address=client_address))
            break
      finally:
        # Clean up the connection
        connection.close()

if __name__ == "__main__":
  logging.basicConfig(filename='logon.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s:%(message)s', encoding='utf-8')

  server = Server('localhost', 10000)
  server.start()