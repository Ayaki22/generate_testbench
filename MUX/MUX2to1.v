module MUX2to1(c, a, b, sel);
output c;
input a, b, sel;

//dataflow level
assign c = (a&sel) | (b&(!sel));

endmodule