## Regenerating UML with Custom Configuration

1. Replace the contents of the `.clang-uml` file inside the `oo-test` folder with the contents of the `.yml` file provided in this directory.
2. Run the following commands from the repository root:

```bash
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=1
clang-uml -c .clang-uml -g plantuml -g graphml -g json
plantuml -tsvg docs/diagrams/event_sequence.puml
```

3. The generated diagram will be available at:

```bash
docs/diagrams/event_sequence.svg
```
