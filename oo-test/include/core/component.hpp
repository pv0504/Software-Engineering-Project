#pragma once
#include <string>
#include <memory>


namespace ootest { namespace core {
    class Entity;


    class Component {
        public:
            explicit Component(Entity* owner);
            virtual ~Component();
            virtual void tick(double dt) = 0;
            Entity* owner() const { return owner_; }
        protected:
            Entity* owner_;
    };


    class PhysicsComponent : public Component {
        public:
            PhysicsComponent(Entity* owner);
            void tick(double dt) override;
            double velocity{0.0};
            double mass{1.0};
    };


    class ScriptComponent : public Component {
        public:
            ScriptComponent(Entity* owner);
            void tick(double dt) override;
            void run_script(const std::string &code);
    };


} }
