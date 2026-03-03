#pragma once
#include <functional>
#include <vector>


namespace ootest { namespace event {


    struct Event {
        enum class Type { None, Click, Update };
        Type type{Type::None};
        int id{0};
    };


    class Dispatcher {
        public:
            using Handler = std::function<void(const Event&)>;
            void register_handler(Handler h) { handlers_.push_back(h); }
            void dispatch(const Event &e) { for (auto &h: handlers_) h(e); }
        private:
            std::vector<Handler> handlers_;
    };


} }
