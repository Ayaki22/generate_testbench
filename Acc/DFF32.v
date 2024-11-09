module DFF32(Dout, Din, clk, reset, w_en);
output reg [31:0] Dout;
input [31:0] Din;
input clk, reset, w_en;

always@(posedge clk)begin
if (reset)
	Dout <= 32'd0;
else
	Dout <= (w_en) ? Din : Dout;
end

endmodule