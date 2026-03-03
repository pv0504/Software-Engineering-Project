#pragma once
#include "transform.hpp"
#include "component.hpp"
#include "entity.hpp"
#include <vector>
#include <memory>


namespace ootest { namespace core {


    class GameObject : public Entity {
        public:
            GameObject(std::string name);
            ~GameObject() override;
            void update(double dt) override;
            void add_component(std::shared_ptr<Component> c);
            size_t component_count() const { return components_.size(); }


            
            void set_parent(std::shared_ptr<GameObject> p) { parent_ = p; }
            std::shared_ptr<GameObject> parent() const { return parent_.lock(); }


        private:
            Transform transform_; 
            std::vector<std::shared_ptr<Component>> components_; 
            std::weak_ptr<GameObject> parent_;
    };


} }
