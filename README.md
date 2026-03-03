# Getting Started With

make setup<br>
make run REPO=./oo-test (in general make run REPO=\<path-to-repo-root\>)<br>
<br>
You may test on repos that we have tried:<br>
(1) https://github.com/nlohmann/json<br>
(2) https://github.com/zeux/pugixml<br>
(3) https://github.com/libcpr/cpr<br>
(Note for testing on cpr repo you will need install it's dependencies<br>
(i) sudo apt install meson<br>
(ii) sudo apt install ninja-build)<br>

# Known Issues

You might sometimes see less than topK figures in final images, the exact reason is
there is no direct way to specify nested classes/struct or nested enums via below strategy in clang-uml
   include:
      elements:
for example consider below from oo-test:

```cpp
namespace ootest { namespace core {
    struct Transform {
        double x{0}, y{0}, z{0};
        Transform() = default;
        Transform(double X, double Y, double Z): x(X), y(Y), z(Z) {}
        double magnitude() const;
        struct Helper { 
            static double sq(double v) { return v*v; }
        };
    };
} }
```

Then even if we specify in clang-yml configuration 

```cpp
include:
    elements:
    - "ootest::render::Transform"
    - "ootest::core::Transform::Helper"
```

then also it thinks Transform as a namespace of Helper which does not exsits
only way to include nested stuff is by strategy mentioned in clang-uml documentation:

```cpp
include:
  anyof:
    subclasses:
      - ns1::nsA::A1
    namespaces:
      - ns2::nsB
    context:
      - ns3::nsC::B3
```

for our case in discussion it would be:

```cpp
include:
  anyof:
    subclasses:
    - "ootest::render::Transform"
```

But this will probably blow-up the uml and not necessarily select the top-K our algorithm choose, so we leave it for user to try if they need<br>
Clang-UML documentation link: https://clang-uml.github.io/md_docs_2diagram__filters.html#elements<br>
Refer to Our Report for more details<br>