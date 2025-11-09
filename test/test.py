# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

output_enable = 255
input_enable = 0

class memory():
    def __init__(self, inputSize, outputSize):
        self.input = [0 for _ in range(inputSize)]
        self.output = [0 for _ in range(outputSize)]
    
    def write_output_to_ppm(self, filename):
        outText = "P3\n128 128 255\n"
        for i in range(128*128):
            outText += f"{self.output[i*3]} {self.output[i*3+1]} {self.output[i*3+2]}\n"
        open(filename,"w").write(outText)

async def read_from_memory(dut, mem, address, dataSize):
    for i in range(dataSize):
        mem_address = address+i
        data = mem.input[mem_address]
        assert int(dut.uo_out.value) == mem_address%256 #byte 0 of address
        assert int(dut.uio_out.value) == (mem_address>>8)%256 #byte 1 of the address
        assert int(dut.uio_oe.value) == output_enable

        await ClockCycles(dut.clk, 1)

        assert int(dut.uo_out.value) == (mem_address>>16)%256 # byte 2 of the address
        assert int(dut.uio_out.value) == input_enable # read/write
        assert int(dut.uio_oe.value) == output_enable 
        dut.ui_in.value = data
        await ClockCycles(dut.clk, 1)
        await ClockCycles(dut.clk, 1)
    



async def write_to_memory(dut, mem, address, data, dataSize):
    for i in range(dataSize):
        mem_address = address+i
        assert int(dut.uo_out.value) == mem_address%256 #byte 0 of address
        assert int(dut.uio_out.value) == (mem_address>>8)%256 #byte 1 of the address
        assert int(dut.uio_oe.value) == output_enable

        await ClockCycles(dut.clk, 1)

        assert int(dut.uo_out.value) == (mem_address>>16)%256 # byte 2 of the address
        assert int(dut.uio_out.value) == output_enable # read/write
        assert int(dut.uio_oe.value) == output_enable 
    
        await ClockCycles(dut.clk, 1)

        assert int(dut.uo_out.value) == (data>>(i*8))%256
        mem.output[mem_address - 2**23] = (data>>(i*8))%256 

        await ClockCycles(dut.clk, 1)

async def write_colour_to_memory(dut, mem, address, colour):
    await write_to_memory(dut, mem, address, colour[0], 1);
    await write_to_memory(dut, mem, address + 1, colour[1], 1);
    await write_to_memory(dut, mem, address + 2, colour[2], 1);

@cocotb.test()
async def SingleSquareTest(dut):
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    mem = memory(26,2**16)

    colour = [255,25,128]
    

    mem.input = [
                    1,         #THERE IS 1 SHAPE IN MEMORY
                    32,96,32,96, #BOUNDING BOX FROM (32,32) to (96,96)
                    colour[0],colour[1],colour[2], #RGB COLOUR
                    0,           # TYPE(RECTANGE)
                    0,0,0,0,     #EMPTY
                    0,0,0,0,     #EMPTY
                    0,0,0,0,     #EMPTY
                    0,0,0,0      #EMPTY
                ]

    #chip see number of valid shapes
    await read_from_memory(dut, mem, 0, 1)

    for y in range(128):
        for x in range(128):
            await read_from_memory(dut, mem, 1, 4)
            await ClockCycles(dut.clk, 1) # CHECK BOUNDING BOX
            if(32<=x<=96 and 32 <=y<=96):
                await read_from_memory(dut, mem, 5, 3)
                await write_colour_to_memory(dut, mem, 2**23+(128*y+x)*3, colour)
            else:
                await write_to_memory(dut,mem,2**23+(128*y+x)*3, 0, 3)

    mem.write_output_to_ppm("singleSquareTest.ppm")



@cocotb.test()
async def MultipleSquaresTest(dut):
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    mem = memory(26,2**16)

    colour1 = [255,25,128]
    colour2 = [128,25,255]
    

    mem.input = [
                    2,         #THERE IS 2 SHAPES IN MEMORY
                    32,96,32,96, #BOUNDING BOX FROM (32,32) to (96,96)
                    colour1[0],colour1[1],colour1[2], #RGB COLOUR
                    0,           # TYPE(RECTANGE)
                    0,0,0,0,     #EMPTY
                    0,0,0,0,     #EMPTY
                    0,0,0,0,     #EMPTY
                    0,0,0,0,       #EMPTY
                    64,128,64,128,     #BOUNDING BOX FROM (64,64) to (128,128)
                    colour2[0],colour2[1],colour2[2],     #RGB COLOUR
                    0,     #TYPE(RECTANGLE)
                    0,0,0,0,     #EMPTY
                    0,0,0,0,     #EMPTY
                    0,0,0,0,     #EMPTY
                    0,0,0,0      #EMPTY
                ]

    #chip see number of valid shapes
    await read_from_memory(dut, mem, 0, 1)

    for y in range(128):
        for x in range(128):
            if(64<=x<=128 and 64<=y<=128):
                await read_from_memory(dut, mem, 25, 4) #READ BOUNDING BOX 2
                await ClockCycles(dut.clk, 1) # CHECK BOUNDING BOX
                await read_from_memory(dut, mem, 29, 3) #READ COLOUR
                await write_colour_to_memory(dut, mem, 2**23+(128*y+x)*3, colour2)
            elif(32<=x<=96 and 32<=y<=96):
                await read_from_memory(dut, mem, 25, 4) #READ BOUNDING BOX 2
                await ClockCycles(dut.clk, 1) # CHECK BOUNDING BOX
                await read_from_memory(dut, mem, 1, 4) #READ BOUNDING BOX 1
                await ClockCycles(dut.clk, 1) # CHECK BOUNDING BOX
                await read_from_memory(dut, mem, 5, 3) #READ COLOUR
                await write_colour_to_memory(dut, mem, 2**23+(128*y+x)*3, colour1)
            else:
                await read_from_memory(dut, mem, 25, 4) #READ BOUNDING BOX 2
                await ClockCycles(dut.clk, 1) # CHECK BOUNDING BOX
                await read_from_memory(dut, mem, 1, 4) #READ BOUNDING BOX 1
                await ClockCycles(dut.clk, 1) # CHECK BOUNDING BOX
                await write_colour_to_memory(dut, mem, 2**23+(128*y+x)*3, [0,0,0])

    mem.write_output_to_ppm("multipleSquareTest.ppm")



