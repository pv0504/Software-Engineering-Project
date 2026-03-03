#pragma once
#include <vector>
#include <memory>
#include <string>
#include "core/entity.hpp" 


namespace ootest { namespace system {
    class EntityManager {
        public:
            void add(const std::shared_ptr<class ootest::core::Entity> &e);
            std::shared_ptr<class ootest::core::Entity> find(const std::string &name) const;
            size_t count() const { return entities_.size(); }
        private:
            std::vector<std::shared_ptr<class ootest::core::Entity>> entities_;
    };
} }
