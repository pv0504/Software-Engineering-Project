Replace The .clang-uml's content inside oo-test folder by the content in the yml file in this directory.
Then just run:
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=1
clang-uml -c .clang-uml -g plantuml -g graphml -g json
plantuml -tsvg docs/diagrams/event_sequence.puml