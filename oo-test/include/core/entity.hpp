#pragma once
#include <string>
#include <memory>
#include <vector>


namespace ootest { namespace core {


    class Entity {
        public:
            Entity(std::string name);
            virtual ~Entity();


            virtual void update(double dt) = 0; 
            virtual std::string type_name() const { return "Entity"; }


            const std::string &name() const { return name_; }
        protected:
            std::string name_;
    };


} }
