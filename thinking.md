
Tinytapeout

8 input wires
8 output wires
8 bidirectional wires
    - 8 wires
    - 8 selectors

GOAL: 60 FPS with 128 Shapes at 128x128

image format:

128x128 8bit RGB
2^(7+7+2) -> 2^(16) -> 64K image


1 byte = 8 bits

memory layout:

--
input area
0x000000->0x7fffff
2^23 bytes

general info
how many shapes do we have(2 bytes)

"stack of 2d shapes"

each shape
    -bounding box(4 bytes)
    -colour(3 bytes)
    -type(1 byte)
    -(necessary data)(16 bytes)

only the last shape will show, so read the memeory from last shape to first, once we find a shape on our pixel, we stop and display that colour


--
output area
0x800000 -> 0xffffff

--

input:


output:

RGB value: 3 8bit values -> 24 bits
Memory Address: 24 bit address -> 24 bits

48 bits

DURING OUTPUT PHASE:
16 outputs, 8 inputs



Memory Address: 
