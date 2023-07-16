build:
	 g++ -std=c++11 -o main main.cpp `pkg-config --cflags --libs opencv4 libfreenect`

run: build
	./main

.PHONY: build