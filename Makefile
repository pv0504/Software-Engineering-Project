SHELL := /bin/bash
CMAKE := cmake
CLANG_UML := clang-uml
PLANTUML := plantuml
VENV_DIR := venv
VENV_PY := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip
OUTPUT_BASE := output
REQ_FILE := requirements.txt
.PHONY: setup install run clean
setup:
	sudo apt update && sudo apt upgrade -y
	sudo apt install -y git build-essential cmake pkg-config gcc g++ make python3 python3-pip python3-venv default-jre graphviz plantuml software-properties-common
	-sudo add-apt-repository -y ppa:bkryza/clang-uml || true
	sudo apt update || true
	-sudo apt install -y clang-uml || true
	if [ ! -d "$(VENV_DIR)" ]; then \
	  python3 -m venv $(VENV_DIR); \
	else \
	  echo "Virtualenv $(VENV_DIR) already exists; skipping creation."; \
	fi
	$(VENV_PIP) install --upgrade pip setuptools wheel || true
	if [ -f "$(REQ_FILE)" ]; then \
	  $(VENV_PIP) install -r $(REQ_FILE); \
	else \
	  echo "No $(REQ_FILE) in CWD; skipping python installs."; \
	fi
install:
	if [ ! -d "$(VENV_DIR)" ]; then python3 -m venv $(VENV_DIR); fi
	$(VENV_PIP) install --upgrade pip setuptools wheel || true
	if [ -f "$(REQ_FILE)" ]; then $(VENV_PIP) install -r $(REQ_FILE); else echo "No $(REQ_FILE) in CWD; nothing to install."; fi
run:
	@if [ -z "$(REPO)" ]; then \
	  echo "Error: REPO not set. Usage: make run REPO=<repo-name-or-path>"; \
	  exit 1; \
	fi
	@REPO_INPUT="$(REPO)"; \
	case "$$REPO_INPUT" in \
	  /*|./*|../*) REPO_DIR="$$REPO_INPUT"; ;; \
	  *) REPO_DIR="./$$REPO_INPUT"; ;; \
	esac; \
	REPO_DIR=$$(echo "$$REPO_DIR" | sed 's:/*$$::'); \
	REPO_BASENAME=$$(basename "$$REPO_DIR"); \
	echo "Repository directory: $$REPO_DIR (name: $$REPO_BASENAME)"; \
	\
	if [ ! -d "$(VENV_DIR)" ]; then \
	  echo "Error: virtualenv '$(VENV_DIR)' not found. Run 'make setup' or 'make install' first."; \
	  exit 1; \
	fi; \
	VENV_PY_PATH="$$(pwd)/$(VENV_PY)"; \
	if [ ! -f "$$VENV_PY_PATH" ]; then \
	echo "ERROR: Python not found at $$VENV_PY_PATH"; \
	exit 1; \
	fi; \
	echo "Using Python: $$VENV_PY_PATH"; \
	\
	if [ ! -d "$$REPO_DIR" ]; then \
	  echo "Error: repository '$$REPO_DIR' not found."; \
	  exit 1; \
	fi; \
	if [ ! -f "$$REPO_DIR/CMakeLists.txt" ]; then \
	  echo "Error: CMakeLists.txt not found in '$$REPO_DIR' — not a pure C++ repo."; \
	  exit 1; \
	fi; \
	\
	DIAGRAM_SUBDIR="docs/diagrams"; \
	BUILD_SUBDIR="build"; \
	CLANG_UML_FILE="$$REPO_DIR/.clang-uml"; \
	DIAGRAM_DIR="$$REPO_DIR/$$DIAGRAM_SUBDIR"; \
	OUTPUT_DIR="$(OUTPUT_BASE)/$$REPO_BASENAME"; \
	\
	mkdir -p "$$DIAGRAM_DIR"; \
	if [ ! -f "$$CLANG_UML_FILE" ]; then \
	  echo "# .clang-uml" > "$$CLANG_UML_FILE"; \
	  echo "compilation_database_dir: $$BUILD_SUBDIR" >> "$$CLANG_UML_FILE"; \
	  echo "output_directory: $$DIAGRAM_SUBDIR" >> "$$CLANG_UML_FILE"; \
	  echo "generate_method_arguments: none" >> "$$CLANG_UML_FILE"; \
	  echo "diagrams:" >> "$$CLANG_UML_FILE"; \
	  echo "  all_classes:" >> "$$CLANG_UML_FILE"; \
	  echo "    type: class" >> "$$CLANG_UML_FILE"; \
	  echo "Created default $$CLANG_UML_FILE"; \
	else \
	  echo "Using existing $$CLANG_UML_FILE"; \
	fi; \
	\
	COPIED=0; HAD_ORIG=0; \
	if [ -f "./boosted_community_rep.py" ]; then \
	  if [ -f "$$REPO_DIR/boosted_community_rep.py" ]; then mv "$$REPO_DIR/boosted_community_rep.py" "$$REPO_DIR/boosted_community_rep.py.bak"; HAD_ORIG=1; fi; \
	  cp ./boosted_community_rep.py "$$REPO_DIR/"; COPIED=1; \
	fi; \
	\
	( cd "$$REPO_DIR" && $(CMAKE) -S . -B $$BUILD_SUBDIR -DCMAKE_EXPORT_COMPILE_COMMANDS=1 ) || { echo "cmake failed"; exit 1; }; \
	( cd "$$REPO_DIR" && $(CLANG_UML) -c .clang-uml -g plantuml -g graphml -g json ) || { echo "clang-uml failed"; exit 1; }; \
	( cd "$$REPO_DIR" && $(PLANTUML) -tsvg $$DIAGRAM_SUBDIR/all_classes.puml ) || echo "plantuml render step failed or no puml; continuing"; \
	\
	if [ -f "$$REPO_DIR/boosted_community_rep.py" ]; then \
	  echo "Running boosted_community_rep.py (venv python)..."; \
	  "$$VENV_PY_PATH" "$$REPO_DIR/boosted_community_rep.py" --graphml "$$DIAGRAM_DIR/all_classes.graphml" --topk 15 --yaml-out "$$REPO_DIR/optmised_output.yml" --no-namespaces || echo "boosted_community_rep.py failed; continuing"; \
	else \
	  echo "boosted_community_rep.py not found in $$REPO_DIR; skipping analysis"; \
	fi; \
	\
	if [ -f "$$REPO_DIR/optmised_output.yml" ]; then \
	  ( cd "$$REPO_DIR" && $(CLANG_UML) -c optmised_output.yml -g plantuml -g graphml -g json ) || echo "regenerate step failed"; \
	else \
	  echo "optmised_output.yml not found; skipping focused regeneration"; \
	fi; \
	\
	mkdir -p "$$OUTPUT_DIR"; \
	cp -r "$$DIAGRAM_DIR/"* "$$OUTPUT_DIR/" 2>/dev/null || echo "No diagrams to copy."; \
	if [ -f "./uml_beautifier.py" ]; then cp ./uml_beautifier.py "$$OUTPUT_DIR/"; fi; \
	if [ -d "$$OUTPUT_DIR" ]; then \
	  pushd "$$OUTPUT_DIR" > /dev/null; \
	  if [ -f "uml_beautifier.py" ] && [ -f "selected_auto.puml" ]; then \
	    echo "Running uml_beautifier.py (venv python) -> final.puml..."; \
	    "$$VENV_PY_PATH" uml_beautifier.py selected_auto.puml > final.puml || echo "uml_beautifier.py failed"; \
	    if command -v $(PLANTUML) >/dev/null 2>&1 || command -v plantuml >/dev/null 2>&1; then plantuml -tsvg ./final.puml || echo "plantuml final.puml failed"; fi; \
	  else \
	    echo "uml_beautifier.py or selected_auto.puml missing; skipping uml_beautifier step"; \
	  fi; \
	  if [ -f "all_classes.svg" ]; then mv -f all_classes.svg intial.svg; fi; \
	  echo "Cleaning output dir: keeping only intial.svg and final.svg..."; \
	  find . -maxdepth 1 ! -name . ! -name intial.svg ! -name final.svg -exec rm -rf {} + || true; \
	  popd > /dev/null; \
	fi; \
	\
	if [ "$$COPIED" -eq 1 ]; then \
	  if [ "$$HAD_ORIG" -eq 1 ]; then rm -f "$$REPO_DIR/boosted_community_rep.py"; mv "$$REPO_DIR/boosted_community_rep.py.bak" "$$REPO_DIR/boosted_community_rep.py"; else rm -f "$$REPO_DIR/boosted_community_rep.py"; fi; \
	fi
clean:
	@echo "Removing virtualenv '$(VENV_DIR)' if present..."; \
	rm -rf "$(VENV_DIR)"
ifneq ($(strip $(REPO_ROOT)),)
	@REPO_DIR="$(REPO_ROOT)"; \
	REPO_BASENAME=$$(basename "$$REPO_DIR"); \
	echo "Also removing build and output for $$REPO_BASENAME ..."; \
	rm -rf "$$REPO_DIR/build" "$(OUTPUT_BASE)/$$REPO_BASENAME"
else ifneq ($(strip $(REPO)),)
	@echo "Also removing build and output for $(REPO) ..."; \
	rm -rf "$(REPO)/build" "$(OUTPUT_BASE)/$(REPO)"
endif
