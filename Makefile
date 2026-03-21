CC ?= cc
CFLAGS ?= -O2 -std=c11 -Wall -Wextra -pedantic

TARGET := serial_tc

.PHONY: all clean

all: $(TARGET)

$(TARGET): serial_tc.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(TARGET)
