#include "room.h"

RoomIdType Room::idCounter = 0;

Room::Room(const std::string& name) : name_(name) {
	id_ = idCounter++;
}
