`timescale 1ns/1ps
module MUX2to1_tb;

    // 信號宣告
    wire c;
    reg a;
    reg b;
    reg sel;

    // 模塊實例化
    MUX2to1 uut (
        .c(c),
        .a(a),
        .b(b),
        .sel(sel)
    );

    // 測試激勵邏輯
    initial begin
        // 初始化輸入信號
        a = 1'b0;
        b = 1'b1;
        sel = 1'b0;
        #20;

        // 隨機變化輸入信號
        // 第 1 次變化
        a = 1'b0;
        b = 1'b0;
        sel = 1'b1;
        #20;
        // 第 2 次變化
        a = 1'b1;
        b = 1'b1;
        sel = 1'b1;
        #20;
        // 第 3 次變化
        a = 1'b1;
        b = 1'b0;
        sel = 1'b0;
        #20;
        // 第 4 次變化
        a = 1'b1;
        b = 1'b1;
        sel = 1'b1;
        #20;
        // 第 5 次變化
        a = 1'b0;
        b = 1'b0;
        sel = 1'b1;
        #20;
        // 第 6 次變化
        a = 1'b0;
        b = 1'b1;
        sel = 1'b0;
        #20;
        // 第 7 次變化
        a = 1'b0;
        b = 1'b1;
        sel = 1'b0;
        #20;
        // 第 8 次變化
        a = 1'b1;
        b = 1'b0;
        sel = 1'b1;
        #20;
        // 第 9 次變化
        a = 1'b1;
        b = 1'b1;
        sel = 1'b0;
        #20;
        // 第 10 次變化
        a = 1'b0;
        b = 1'b1;
        sel = 1'b1;
        #20;

        // 結束模擬
        #100;
        $finish;
    end

    // 輸出監控
    initial begin
        $monitor("Time=%0d, c=%b, a=%b, b=%b, sel=%b", $time, c, a, b, sel);
    end

    initial begin
        $dumpfile("MUX2to1_tb.vcd");
        $dumpvars;
    end

endmodule
