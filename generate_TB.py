import re
import argparse
import os

def parse_verilog_file(file_path):
    """
    解析 Verilog 文件，提取模組名稱和所有端口（inputs, outputs, inouts）。
    返回模組名稱和一個包含端口信息的字典。
    """
    module_name = None
    ports = {}

    with open(file_path, 'r') as file:
        content = file.read()

    # 提取模組名稱和端口列表
    start_index = content.find('module') + len('module')
    end_index = content.find('(', start_index)
    module_header = content[start_index:end_index]

    # 獲取模組名稱
    module_parts = module_header.split('(')
    module_name = module_parts[0].strip()

    # 逐行處理端口聲明
    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        # 檢查行是否為端口聲明
        if line.startswith('input') or line.startswith('output') or line.startswith('inout'):
            # 分離方向和端口聲明
            parts = line.split()
            direction = parts[0]  # 端口方向
            
            # 端口名稱可能包含 reg/wire、數組和多個端口
            port_declaration = ' '.join(parts[1:])  # 排除方向關鍵字
            if ';' in port_declaration:
                port_declaration = port_declaration.split(';')[0]  # 去掉結束符號
            
            # 提取端口名稱
            port_names = []
            for part in port_declaration.split(','):
                part = part.strip()
                if part:
                    port_names.append(part.split()[-1])  # 取得每個端口的最後一部分作為端口名稱

            # 添加端口到字典，檢查是否重複
            for port in port_names:
                if port not in ports:  # 檢查是否重複
                    ports[port] = direction  # 只存儲端口名稱和方向

    return module_name, ports

def generate_testbench(module_name, ports, output_file, clock_signal="clk", reset_signal="rst"):
    """
    根據模組名稱和端口信息生成 Verilog testbench 文件。
    """
    tb_module_name = f"{module_name}_tb"

    with open(output_file, "w") as tb_file:
        # Timescale 和模組定義
        tb_file.write("`timescale 1ns/1ps\n")
        tb_file.write(f"module {tb_module_name};\n\n")

        # 信號宣告
        tb_file.write(f"    // 信號宣告\n")
        """ tb_file.write(f"    reg {clock_signal};\n")
        tb_file.write(f"    reg {reset_signal};\n") """

        declared_regs = set()  # 用來存儲已宣告的 reg 類型端口
        declared_wires = set()  # 用來存儲已宣告的 wire 類型端口

        for port, direction in ports.items():
            if direction == "input":
                if port not in declared_regs:  # 避免重複宣告
                    tb_file.write(f"    reg {port};\n")
                    declared_regs.add(port)  # 加入已宣告的 reg
            elif direction in ["output", "inout"]:
                if port not in declared_wires:  # 避免重複宣告
                    tb_file.write(f"    wire {port};\n")
                    declared_wires.add(port)  # 加入已宣告的 wire
        tb_file.write("\n")

        # 模組實例化
        tb_file.write("    // 模塊實例化\n")
        tb_file.write(f"    {module_name} uut (\n")
        
        port_count = len(ports)
        current_port = 0
        for port, direction in ports.items():
            current_port += 1
            comma = "," if current_port < port_count else ""
            tb_file.write(f"        .{port}({port}){comma}\n")
        tb_file.write("    );\n\n")

        # 時鐘產生邏輯
        tb_file.write("    // 時鐘產生邏輯\n")
        tb_file.write("    initial begin\n")
        tb_file.write(f"        {clock_signal} = 0;\n")
        tb_file.write(f"        forever #5 {clock_signal} = ~{clock_signal};\n")
        tb_file.write("    end\n\n")

        # 重置邏輯
        tb_file.write("    // 重置邏輯\n")
        tb_file.write("    initial begin\n")
        tb_file.write(f"        {reset_signal} = 1;\n")
        tb_file.write(f"        #10 {reset_signal} = 0;\n")
        tb_file.write("    end\n\n")

        # 測試激勵邏輯
        tb_file.write("    // 測試激勵邏輯\n")
        tb_file.write("    initial begin\n")
        tb_file.write("        // 初始化輸入信號\n")
        for port, direction in ports.items():
            if direction == "input":
                tb_file.write(f"        {port} = 0;\n")
        tb_file.write("        #20;\n\n")
        tb_file.write("        // 在這裡添加測試激勵\n")
        tb_file.write('        $display("開始測試...");\n')
        tb_file.write("        // 結束模擬\n")
        tb_file.write("        #100;\n")
        tb_file.write("        $finish;\n")
        tb_file.write("    end\n\n")

        # 輸出監控
        tb_file.write("    // 輸出監控\n")
        tb_file.write("    initial begin\n")
        tb_file.write('        $monitor("Time=%0d, ')

        monitor_signals = []
        for port in ports.keys():
            monitor_signals.append(f'{port}=%b')
        
        monitor_str = ', '.join(monitor_signals)
        tb_file.write(monitor_str + '", $time')
        
        for port in ports.keys():
            tb_file.write(f', {port}')
        tb_file.write(");\n")
        tb_file.write("    end\n\n")

        # 結束模組
        tb_file.write("endmodule\n")

    print(f"Testbench 已生成: {output_file}")



def main():
    # 使用 argparse 來解析命令行參數
    parser = argparse.ArgumentParser(description="自動生成 Verilog testbench")
    
    # Verilog 文件路徑參數
    parser.add_argument("verilog_file", type=str, help="Verilog 原始檔案的路徑")

    # 可選參數：時鐘和重置信號名稱
    parser.add_argument("--clock", type=str, default="clk", help="時鐘信號名稱，默認為 'clk'")
    parser.add_argument("--reset", type=str, default="rst", help="重置信號名稱，默認為 'rst'")

    # 解析參數
    args = parser.parse_args()

    verilog_file = args.verilog_file
    clock_signal = args.clock
    reset_signal = args.reset

    # 檢查文件是否存在
    if not os.path.exists(verilog_file):
        raise FileNotFoundError(f"找不到指定的 Verilog 文件: {verilog_file}")

    # 解析 Verilog 文件
    try:
        module_name, ports = parse_verilog_file(verilog_file)
    except ValueError as e:
        print(f"解析錯誤: {e}")
        return

    # 構建 testbench 文件名稱
    base_name = os.path.splitext(os.path.basename(verilog_file))[0]
    tb_file_name = f"{base_name}_tb.v"
    tb_file_path = os.path.join(os.path.dirname(verilog_file), tb_file_name)

    # 生成 testbench
    generate_testbench(module_name, ports, tb_file_path, clock_signal, reset_signal)

if __name__ == "__main__":
    main()
