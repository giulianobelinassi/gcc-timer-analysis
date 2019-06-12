CC=gcc
CXX=g++
CFLAGS=-march=native -O3 -Wall -pedantic -flto
LDFLAGS=
RM=rm -f

all: power_sensor

power_sensor: power_sensor.o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

power_sensor.o: power_sensor.c sensors.def
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: clean
clean:
	$(RM) *.o power_sensor
