module Acc32(Acc_out, w_en, clk, reset);
output [31:0] Acc_out;
input w_en, clk, reset;

wire [31:0] Din;

assign Din = Acc_out + 32'd1;

DFF32 d0(.Dout(Acc_out), .Din(Din), .clk(clk), .reset(reset), .w_en(w_en));

endmodule