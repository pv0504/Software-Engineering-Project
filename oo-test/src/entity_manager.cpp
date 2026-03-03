#include "../include/system/entity_manager.hpp"
using namespace ootest::system;
using namespace ootest::core;

void EntityManager::add(const std::shared_ptr<Entity> &e) { entities_.push_back(e); }
std::shared_ptr<Entity> EntityManager::find(const std::string &name) const
{
    for (auto &p : entities_)
        if (p->name() == name)
            return p;
    return nullptr;
}
