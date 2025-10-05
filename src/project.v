/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none



module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  reg [7:0] state;
  reg [23:0] read_address;
  reg [23:0] write_address;
  reg [23:0] colour;
  reg [23:0] bounding_box;
  reg [15:0] current_pixel;
  reg [7:0] uo_out_reg;
  reg [7:0] uio_out_reg;
  reg [7:0] num_shapes;
  reg [1:0] counter;

  // All output pins must be assigned. If not used, assign to 0.
  assign uio_oe  = 255;
  assign uo_out  = uo_out_reg; 
  assign uio_out = uio_out_reg;

  parameter READ_NUM_SHAPES_1 = 0;
  parameter READ_NUM_SHAPES_2 = 1;
  parameter READ_NUM_SHAPES_3 = 2;

  parameter READ_SHAPE_BOUNDING_BOX_1 = 3;
  parameter READ_SHAPE_BOUNDING_BOX_2 = 4;
  parameter READ_SHAPE_BOUNDING_BOX_3 = 5;

  parameter CHECK_BOUNDING_BOX = 6;

  parameter READ_COLOUR_1 = 7;
  parameter READ_COLOUR_2 = 8;
  parameter READ_COLOUR_3 = 9;

  parameter WRITE_COLOUR_1 = 10;
  parameter WRITE_COLOUR_2 = 11;
  parameter WRITE_COLOUR_3 = 12;


  always @(posedge clk) begin
    if(rst_n==0)begin
      state<=0;
      read_address<=0;
      write_address<= 24'h800000;
      colour<=0;
      current_pixel<=0;
      counter <= 0;
      uo_out_reg <= 0;
      uio_out_reg<=0;
    end else begin
	case(state)
	  READ_NUM_SHAPES_1: begin
	    uo_out_reg <= read_address[7:0];
	    uio_out_reg <= read_address[15:8];
	    state <= READ_NUM_SHAPES_2;
	  end
	  READ_NUM_SHAPES_2: begin
	    uo_out_reg <= read_address[23:16];
	    uio_out_reg <= 0;
	    state <= READ_NUM_SHAPES_3;
	  end
	  READ_NUM_SHAPES_3: begin
	    num_shapes <= ui_in;
	    read_address <= 1;
	    state <= READ_SHAPE_BOUNDING_BOX_1;
	  end
	  READ_SHAPE_BOUNDING_BOX_1: begin
	    uo_out_reg <= read_address[7:0];
	    uio_out_reg <= read_address[15:8];
	    state <= READ_SHAPE_BOUNDING_BOX_2;
	  end
	  READ_SHAPE_BOUNDING_BOX_2: begin
	    uo_out_reg <= read_address[23:16];
	    uio_out_reg <= 0;
	    state <= READ_SHAPE_BOUNDING_BOX_3;
	  end
	  READ_SHAPE_BOUNDING_BOX_3: begin
	    counter<= counter+1;

	    if(counter==0) begin
              bounding_box[7:0] <= ui_in;
            end else if(counter==1) begin
              bounding_box[15:8] <= ui_in;
            end else if(counter==2) begin
              bounding_box[23:16] <= ui_in;
            end else if(counter==3) begin
              bounding_box[31:24] <= ui_in;
	    end

	    if(counter==3) begin
              state <= CHECK_BOUNDING_BOX;
            end else begin
              state <= READ_SHAPE_BOUNDING_BOX_1;
	      read_address <= read_address + 1;
            end
	  end
	  CHECK_BOUNDING_BOX: begin
	    if(current_pixel[7:0]<bounding_box[7:0]) begin //Not in bounding box
	       
	       colour <= 0;
	       state <= WRITE_COLOUR_1;
            end else begin
	       state <= READ_COLOUR_1;
	       counter <= 0;
	       read_address <= read_address + 1;
	    end
          end
	  READ_COLOUR_1: begin
	    uo_out_reg <= read_address[7:0];
	    uio_out_reg <= read_address[15:8];
	    state <= READ_COLOUR_2;
	  end
	  READ_COLOUR_2: begin
	    uo_out_reg <= read_address[23:16];
	    uio_out_reg <= 0;
	    state <= READ_COLOUR_3;
	  end
	  READ_COLOUR_3: begin
	    counter<= counter+1;

	    if(counter==0) begin
              colour[7:0] <= ui_in;
            end else if(counter==1) begin
              colour[15:8] <= ui_in;
            end else if(counter==2) begin
              colour[23:16] <= ui_in;
	    end

	    if(counter==2) begin
              state <= WRITE_COLOUR_1;
	      counter <= 0;
            end else begin
              state <= READ_COLOUR_1;
	      read_address <= read_address + 1;
            end
	  end
	  WRITE_COLOUR_1: begin
	    uo_out_reg <= write_address[7:0];
	    uio_out_reg <= write_address[15:8];
	    state <= WRITE_COLOUR_2;
	  end
	  WRITE_COLOUR_2: begin
	    uo_out_reg <= write_address[23:16];
	    uio_out_reg <= 255;
	    state <= WRITE_COLOUR_3;
	  end
	  WRITE_COLOUR_3: begin
	    counter<= counter+1;

	    if(counter==0) begin
              uo_out_reg <= colour[7:0];
            end else if(counter==1) begin
              uo_out_reg <= colour[15:8];
            end else if(counter==2) begin
              uo_out_reg <= colour[23:16];
	    end
	    write_address <= write_address + 1;
	    read_address <= 1;

	    if(counter==2) begin
              current_pixel <= current_pixel + 1;
	      state <= READ_SHAPE_BOUNDING_BOX_1;
            end else begin
              state <= WRITE_COLOUR_1;
            end
	  end
	  default: state<=0;
	endcase
    end
  end


  // List all unused inputs to prevent warnings
  wire _unused = &{ena};

endmodule
