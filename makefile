PYTHON    := python3
WINE_PY   := wine python

SRC       := raycastingDungeon.py

NAME := RaycastingDungeonCrawler

DATA_LOCATION := assets:assets

.PHONY: all linux windows clean

all: linux windows

linux:
	@echo "Building Linux standalone..."
	$(PYTHON) -m PyInstaller \
		--onefile \
		--add-data "$(DATA_LOCATION)" \
		--name "$(NAME)-linux" \
		$(SRC)

windows:
	@echo "Building Windows EXE via Wine..."
	wine pyinstaller \
		--onefile \
		--windowed \
		--add-data "$(DATA_LOCATION)" \
		--name "$(NAME)-win" \
		$(SRC)

clean:
	@echo "Cleaning build/dist/spec..."
	rm -rf build/ dist/ __pycache__ *.spec
