#include <iostream>
#include <memory>
#include "../include/core/entity.hpp"
#include "../include/core/gameobject.hpp"
#include "../include/render/texture.hpp"
#include "../include/render/renderer.hpp"
#include "../include/system/entity_manager.hpp"
#include "../include/event/event.hpp"


using namespace ootest::core;
using namespace ootest::render;
using namespace ootest::system;
using namespace ootest::event;


int main(){
    auto gm = std::make_shared<GameObject>("Player");
    auto gfx = std::make_shared<Renderer>(gm.get());
    auto tex = std::make_shared<Texture>("player.png");
    gfx->set_texture(tex);
    gm->add_component(gfx);


    EntityManager em;
    em.add(gm);


    Dispatcher disp;
    disp.register_handler([](const Event &e){ if(e.type==Event::Type::Update) std::cout<<"Update event"; });
    disp.dispatch(Event{Event::Type::Update,42});


    std::cout<<"Entities: "<<em.count()<<"";
    return 0;
}
