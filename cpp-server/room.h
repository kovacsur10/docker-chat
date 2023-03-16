#pragma once

#include <vector>
#include <string>
#include "util.h"

class Room{
public:
	Room(const std::string& name);

  inline std::string getName() const {
    return name_;
  }
    
  inline RoomIdType getId() const {
    return id_;
  }

private:
	std::vector<UserIdentifier> userList_;
	std::string name_;
	RoomIdType id_;

	static RoomIdType idCounter;
};