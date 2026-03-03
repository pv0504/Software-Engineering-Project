#include "../include/render/renderer.hpp"
#include "../include/render/texture.hpp"
#include <iostream>


using namespace ootest::render;
using namespace ootest::core;


Renderer::Renderer(Entity* owner): Component(owner) {}
void Renderer::tick(double dt){ (void)dt;  }
