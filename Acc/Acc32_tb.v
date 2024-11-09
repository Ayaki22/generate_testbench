`timescale 1ns/1ps
module Acc32_tb;

    reg clk;
    reg reset;
    wire [31:0] Acc_out;
    reg [0:0] w_en;

    // 模組實例化
    Acc32 uut (
        .Acc_out(Acc_out),
        .w_en(w_en),
        .clk(clk),
        .reset(reset)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        reset = 1;
        #10 reset = 0;
    end

    initial begin
        // 初始化輸入信號
        w_en = 1'b0;
        #20;

        // 隨機變化輸入信號
        w_en = 1'b0;
        #20;
        w_en = 1'b0;
        #20;
        w_en = 1'b1;
        #20;
        w_en = 1'b0;
        #20;
        w_en = 1'b0;
        #20;
        $finish;
    end

    initial begin
        $monitor("Time=%0d, Acc_out=%b, w_en=%b, clk=%b, reset=%b", $time, Acc_out, w_en, clk, reset);
    end

    initial begin
        $dumpfile("Acc32_tb.vcd");
        $dumpvars;
    end

endmodule
