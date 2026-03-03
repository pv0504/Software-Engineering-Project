# Getting Started With

##

---

# UML Diagram Generation Pipeline

This project automatically generates UML class diagrams from a C++ CMake repository using:
- `cmake`
- `clang-uml`
- `plantuml`
- `graphviz`
- optional Python analysis (`boosted_community_rep.py`)
  
---

## 1. System Requirements

Make sure the following tools are installed:

```bash
cmake --version
clang-uml --version
plantuml -version
python3 --version
```

If any are missing, install:

```bash
sudo apt update
sudo apt install git build-essential cmake gcc g++ make \
python3 python3-pip default-jre graphviz plantuml clang-uml
```

---

## 2. Repository Structure Requirement

The target repository must:
- Be a C++ project
- Contain a `CMakeLists.txt` file at its root
  
Example:

```gcode
my_cpp_project/  
 ├── CMakeLists.txt  
 ├── src/  
 └── include/
```

Below is a clean, structured **README.md** section you can paste into your repository.
It explains usage clearly and looks professional.

---

## 3. Running the Pipeline

From this repository root:

```bash
make run REPO=<path-to-cpp-repo>
```

Example:

```bash
make run REPO=../my_cpp_project
```

---

## 4. What the Command Does

When you run:
```bash
make run REPO=...
```
It performs:
1. Validates repository path
2. Runs CMake to generate compile database
3. Generates UML diagrams using `clang-uml`
4. Converts `.puml` → `.svg` using `plantuml`
5. Optionally runs `boosted_community_rep.py` if present
6. Copies final diagrams into:
  
```bash
output/<repository-name>/
```
---

## 5. Output Location
Generated diagrams will be available at:

```bash
output/<repo-name>/
```
---

## 6. Cleaning Generated Files
To remove generated artifacts:

```bash
make clean
```
This removes:

- `build/`
- `output/`
  

---

## Minimal Usage Summary

```bash
make run REPO=<repo-path>
make clean
```

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
