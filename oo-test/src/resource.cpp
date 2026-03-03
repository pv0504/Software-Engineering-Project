#include "../include/resource/resource.hpp"
#include "../include/render/texture.hpp"


using namespace ootest::resource;


std::shared_ptr<TextureResource> TextureResource::load(const std::string &path){
    return std::shared_ptr<TextureResource>(new TextureResource(path));
}
