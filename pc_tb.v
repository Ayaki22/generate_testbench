`timescale 1ns/1ps
module pc_reg_tb;

    // 信號宣告
    reg clk;
    reg rst;
    wire pc;
    wire ce;

    // 模塊實例化
    pc_reg uut (
        .clk(clk),
        .rst(rst),
        .pc(pc),
        .ce(ce)
    );

    // 時鐘產生邏輯
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // 重置邏輯
    initial begin
        rst = 1;
        #10 rst = 0;
    end

    // 測試激勵邏輯
    initial begin
        // 初始化輸入信號
        clk = 0;
        rst = 0;
        #20;

        // 在這裡添加測試激勵
        $display("開始測試...");
        // 結束模擬
        #100;
        $finish;
    end

    // 輸出監控
    initial begin
        $monitor("Time=%0d, clk=%b, rst=%b, pc=%b, ce=%b", $time, clk, rst, pc, ce);
    end

endmodule
