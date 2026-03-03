#pragma once
#include <string>


namespace ootest { namespace render {


    class Texture {
        public:
            Texture(std::string path);
            const std::string &path() const { return path_; }
        private:
            std::string path_;
    };


} }
