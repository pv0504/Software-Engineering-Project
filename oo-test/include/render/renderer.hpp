#pragma once
#include "../core/component.hpp"
#include "texture.hpp"
#include <memory>


namespace ootest { namespace render {


    class Renderer : public ootest::core::Component {
        public:
            Renderer(ootest::core::Entity* owner);
            void tick(double dt) override;
            void set_texture(std::shared_ptr<Texture> t) { texture_ = t; }
        private:
            std::shared_ptr<Texture> texture_; 
    };


} }
