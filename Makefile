build:
	 g++ -std=c++11 -o main.app main.cpp `pkg-config --cflags --libs opencv4 libfreenect`

run: build
	./main.app

.PHONY: build