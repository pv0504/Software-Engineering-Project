#include "../include/core/entity.hpp"
#include <iostream>


using namespace ootest::core;


Entity::Entity(std::string name): name_(std::move(name)) {}
Entity::~Entity() = default;

