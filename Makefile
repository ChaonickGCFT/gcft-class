.PHONY: all clean python run_zlimit
all:        ; $(MAKE) -C class_public
clean:      ; $(MAKE) -C class_public clean
python:     ; source class_public/.venv/bin/activate && python -c "import classy; print('classy OK')"
run_zlimit: ; ./class_public/class gcft_zlimit_highz.ini
