ROCM_PATH ?= /opt/rocm
CXX := $(ROCM_PATH)/llvm/bin/clang++
CXXFLAGS := -std=c++17 -O2 -g -fPIC -Wall -D__HIP_PLATFORM_AMD__ -I$(ROCM_PATH)/include

lib/libfindingmnemo_stacks.so: shim/launch_stacks.cpp
	mkdir -p lib
	$(CXX) $(CXXFLAGS) -shared $< -o $@ -ldl -lpthread

clean:
	rm -rf lib

.PHONY: clean
