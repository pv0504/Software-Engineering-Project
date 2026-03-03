#include "../include/core/component.hpp"
#include "../include/core/entity.hpp"
#include <iostream>


using namespace ootest::core;


Component::Component(Entity* owner): owner_(owner) {}
Component::~Component() = default;


PhysicsComponent::PhysicsComponent(Entity* owner): Component(owner) {}
void PhysicsComponent::tick(double dt) { velocity += 9.8*dt; }


ScriptComponent::ScriptComponent(Entity* owner): Component(owner) {}
void ScriptComponent::tick(double dt) {  }
void ScriptComponent::run_script(const std::string &code){ (void)code; }
