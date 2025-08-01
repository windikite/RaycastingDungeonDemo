# ──────────────────────────────────────────────────────────────────────────────
# Makefile for RaycastingDungeonCrawler (one-dir builds)
# ──────────────────────────────────────────────────────────────────────────────

# Linux Python
PYTHON     := python3
# Windows Python under Wine
WINE_PY    := wine python

# Where your code lives
SRC_DIR    := src
ENTRY      := $(SRC_DIR)/__main__.py

# Output base name
NAME       := RaycastingDungeonCrawler

# How to ship assets
DATA_LINUX := assets:assets
DATA_WIN   := assets;assets

.PHONY: all linux windows clean

all: linux windows

linux:
	@echo "→ Building Linux one-dir bundle…"
	$(PYTHON) -m PyInstaller \
		--onedir \
		--name "$(NAME)-linux" \
		--paths "$(SRC_DIR)" \
		--add-data "$(DATA_LINUX)" \
		"$(ENTRY)"

windows:
	@echo "→ Building Windows one-dir bundle…"
	$(WINE_PY) -m PyInstaller \
		--debug=imports \
		--onedir \
		--windowed \
		--name "$(NAME)-win" \
		--paths "$(SRC_DIR)" \
		--add-data="$(DATA_WIN)" \
		--collect-submodules core \
		--hidden-import core.uiController \
		--add-data "src/uiController.py;." \
		"$(ENTRY)"

clean:
	@echo "← Cleaning build artifacts…"
	rm -rf build/ dist/ *.spec
