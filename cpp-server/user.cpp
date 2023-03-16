#include "user.h"

UserIdentifier User::idCounter = 0;

User::User(const std::string& name, const int socket, const sockaddr_in& connectionData) : 
  name_(name),
  id_(idCounter++),
  socket_(socket),
  connectionData_(connectionData)
{
}
