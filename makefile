PYTHON    := python3
WINE_PY   := wine python

SRC       := ./src/gameController.py
SRC_PATH  := ./src

NAME      := RaycastingDungeonCrawler
DATA_LINUX := assets:assets
DATA_WIN   := assets;assets

.PHONY: all linux windows clean

all: linux windows

linux:
	@echo "Building Linux standalone..."
	$(PYTHON) -m PyInstaller \
		--onefile \
		--name "$(NAME)-linux" \
		--paths "$(SRC_PATH)" \
		--add-data "$(DATA_LINUX)" \
		"$(SRC)"

windows:
	@echo "Building Windows EXE via Wine..."
	wine pyinstaller \
		--onefile \
		--windowed \
		--name "$(NAME)-win" \
		--paths "$(SRC_PATH)" \
		--add-data "$(DATA_WIN)" \
		"$(SRC)"

clean:
	@echo "Cleaning build/dist/spec..."
	rm -rf build/ dist/ __pycache__ *.spec
