#pragma once
#include <string>
#include <netinet/in.h>
#include "util.h"

class User{
public:
  User(const std::string& name, const int socket, const sockaddr_in& connectionData);

  inline std::string getName() const {
    return name_;
  }
    
  inline RoomIdType getId() const {
    return id_;
  }

private:
  std::string name_;
  UserIdentifier id_;
  int socket_;
  sockaddr_in connectionData_;

  static UserIdentifier idCounter;
};
