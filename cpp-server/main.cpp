#include <iostream>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include "room.h"

// g++ main.cpp room.cpp user.cpp -std=c++17 -g -Wall -Wextra 

// https://www.linuxhowtos.org/C_C++/socket.htm
// https://man7.org/linux/man-pages/man2/socket.2.html
// https://man7.org/linux/man-pages/man2/bind.2.html
// https://man7.org/linux/man-pages/man2/listen.2.html
// https://man7.org/linux/man-pages/man2/select.2.html
// https://man7.org/linux/man-pages/man2/accept.2.html

// SZERVER
//   | szoba1  ===> user list
//   | szoba2  ===> user list
//   | default = SZERVER  ===> user list 1

int main() {
  constexpr int LISTENING_PORT = 12555;
  constexpr int MAXIMUM_CLIENTS = 30;
  int serverFd{0};
  fd_set fdSet;
  int readyFds{0};

  std::cout << "INFO: Starting the server..." << std::endl;
  // Create the socket (initialize the server endpoint)
  serverFd = socket(AF_INET,     // internet socket
                    SOCK_STREAM, // TCP (stream) transport layer
                    0);
  if (serverFd < 0) {
    std::cout << "ERROR: Cannot start server and error creating the socket." << std::endl;
    return 1;
  }

  sockaddr_in serverAddress;
  serverAddress.sin_addr.s_addr = INADDR_ANY;
  serverAddress.sin_family = AF_INET;
  serverAddress.sin_port = LISTENING_PORT;

  if(bind(serverFd, reinterpret_cast<sockaddr*>(&serverAddress), sizeof(serverAddress)) == -1) {
    std::cout << "ERROR: Cannot start server and error binding the socket." << std::endl;
    return 1;
  }

  if(listen(serverFd, MAXIMUM_CLIENTS) == -1) {
    std::cout << "ERROR: Cannot start server and error listen to the socket." << std::endl;
    return 1;
  }

  std::vector<int> clients;
  char* buffer;
  buffer = (char*) malloc(1200 * sizeof(char));

  std::cout << "INFO: Waiting for connections..." << std::endl;

  FD_ZERO(&fdSet);
  FD_SET(serverFd, &fdSet);
  while(true) {
    fd_set tempFdSet{fdSet};
    readyFds = select(MAXIMUM_CLIENTS, &tempFdSet, nullptr, nullptr, nullptr);
    if(readyFds == -1) {
      std::cout << "ERROR: Cannot make select on filedescriptor set." << std::endl;
    } else {
      if(FD_ISSET(serverFd, &tempFdSet)){
        sockaddr_in clientAddress;
        socklen_t size = sizeof(clientAddress);
        int clientFd = accept(serverFd, reinterpret_cast<sockaddr*>(&clientAddress), &size);
        if(clientFd == -1 ){
          std::cout << "ERROR: Cannot accept client connection." << std::endl;
        } else {
          // TODO ide jön a user és kezelni a dolgait
          FD_SET(clientFd, &fdSet);
          clients.push_back(clientFd);
        }
      }

      // Client handling
      for(const auto clientFd : clients) {
        if(FD_ISSET(clientFd, &tempFdSet)){
          int byteok = recv(clientFd, (void*)&buffer[0], 1200 * sizeof(char), 0);
          send(clientFd, buffer, byteok, 0);
        }
      }
    }
  }

  std::cout << "INFO: Exiting..." << std::endl;
  return 0;
}
