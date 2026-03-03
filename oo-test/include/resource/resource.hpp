#pragma once
#include <string>
#include <map>
#include <memory>


namespace ootest { namespace resource {


    
    template<typename T>
        class ResourceHandle {
            public:
                ResourceHandle() = default;
                explicit ResourceHandle(std::shared_ptr<T> p): ptr_(p) {}
                std::shared_ptr<T> get() const { return ptr_; }
            private:
                std::shared_ptr<T> ptr_;
        };


    class TextureResource {
        public:
            static std::shared_ptr<TextureResource> load(const std::string &path);
            std::string path() const { return path_; }
        private:
            TextureResource(std::string p): path_(p) {}
            std::string path_;
    };


} }
