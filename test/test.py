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


async def read_from_memory(dut, mem, address, dataSize):
    await ClockCycles(dut.clk, 1)
    for i in range(dataSize):
        mem_address = address+i
        dut._log.info(f"MEMORY ADDRESS READ: {mem_address}")
        dut._log.info(f"UO OUT: {dut.uo_out.value}")
        data = mem.input[mem_address]
        assert int(dut.uo_out.value) == mem_address%256 #byte 0 of address
        assert int(dut.uio_out.value) == (mem_address>>8)%256 #byte 1 of the address
        assert int(dut.uio_oe.value) == output_enable

        await ClockCycles(dut.clk, 1)

        assert int(dut.uo_out.value) == (mem_address>>16)%256 # byte 2 of the address
        assert int(dut.uio_out.value) == input_enable # read/write
        assert int(dut.uio_oe.value) == output_enable 
    
        await ClockCycles(dut.clk, 1)

        dut.ui_in.value=data
        await ClockCycles(dut.clk, 1)


async def write_to_memory(dut, mem, address, data, dataSize):
    for i in range(dataSize):
        mem_address = address+i
        dut._log.info(f"MEMORY ADDRESS WRITE: {mem_address}")
        dut._log.info(f"MEMORY ADDRESS WRITE: {mem_address%256}")
        dut._log.info(f"UO OUT: {dut.uo_out.value}")
        assert int(dut.uo_out.value) == mem_address%256 #byte 0 of address
        assert int(dut.uio_out.value) == (mem_address>>8)%256 #byte 1 of the address
        assert int(dut.uio_oe.value) == output_enable

        await ClockCycles(dut.clk, 1)

        dut._log.info(f"UO OUT: {dut.uo_out.value}")
        assert int(dut.uo_out.value) == (mem_address>>16)%256 # byte 2 of the address
        dut._log.info(f"UIO OUT: {dut.uio_out.value}")
        assert int(dut.uio_out.value) == output_enable # read/write
        assert int(dut.uio_oe.value) == output_enable 
    
        await ClockCycles(dut.clk, 1)

        dut._log.info(f"UO OUT: {dut.uo_out.value}")
        dut._log.info(f"DATA: {data}")

        assert int(dut.uo_out.value) == (data>>(i*8))%256
        mem.output[mem_address - 2**23] = (data>>(i*8))%256 

        await ClockCycles(dut.clk, 1)

@cocotb.test()
async def SingleShapeTest(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("read start of memory with 1 square in the middle and display it")

    mem = memory(26,2**16)
    mem.input = [
                    1,         #THERE IS 1 SHAPE IN MEMORY
                    32,96,32,96, #BOUNDING BOX FROM (32,32) to (96,96)
                    255,255,255, #RGB COLOUR
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
            if(x<32 or x>96 or y<32 or y>96):
                await ClockCycles(dut.clk, 1)
                await write_to_memory(dut,mem,2**23+128*y+x, 0, 3)
            else:
                await read_from_memory(dut, mem, 5, 3)
                await ClockCycles(dut.clk, 1)
                await write_to_memory(dut,mem,2**23+128*y+x, 255, 3)


