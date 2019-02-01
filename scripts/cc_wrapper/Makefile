CC=gcc
CXX=g++
CFLAGS=-std=c99 -march=native -O3 -Wall -pedantic -flto
LDFLAGS=

TARGET_CC_PATH=$(word 2,$(shell whereis $(CC)))
TARGET_CC_NAME=$(CC)

TARGET_CXX_PATH=$(word 2,$(shell whereis $(CXX)))
TARGET_CXX_NAME=$(CXX)

OUTPUT_FILE=/tmp/timing_data-1.txt

RM=rm -f

all: $(TARGET_CC_NAME) $(TARGET_CXX_NAME)

$(TARGET_CC_NAME): $(TARGET_CC_NAME).o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(TARGET_CXX_NAME): $(TARGET_CXX_NAME).o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(TARGET_CC_NAME).o: cc_wrapper.c
	$(CC) $(CFLAGS) -DOUTPUT_FILE=\"$(OUTPUT_FILE)\" -DCOMPILER_PATH=\"$(TARGET_CC_PATH)\" -DCOMPILER_NAME=\"$(TARGET_CC_NAME)\" -c $< -o $@

$(TARGET_CXX_NAME).o: cc_wrapper.c
	$(CC) $(CFLAGS) -DOUTPUT_FILE=\"$(OUTPUT_FILE)\" -DCOMPILER_PATH=\"$(TARGET_CXX_PATH)\" -DCOMPILER_NAME=\"$(TARGET_CXX_NAME)\" -c $< -o $@

.PHONY: clean
clean:
	$(RM) *.o $(TARGET_CC_NAME) $(TARGET_CXX_NAME)
