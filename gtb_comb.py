import re
import argparse
import os
import random

def parse_verilog_file(file_path):
    module_name = None
    ports = {}

    with open(file_path, 'r') as file:
        content = file.read()

    module_match = re.search(r'\bmodule\s+(\w+)', content)
    if module_match:
        module_name = module_match.group(1)

    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith('input') or line.startswith('output') or line.startswith('inout'):
            parts = line.split()
            direction = parts[0]
            
            width_match = re.search(r'\[(\d+):(\d+)\]', line)
            if width_match:
                msb = int(width_match.group(1))
                lsb = int(width_match.group(2))
                width = msb - lsb + 1
            else:
                width = 1

            port_names = [part.strip(',;') for part in parts if not part.startswith('input') and not part.startswith('output') and not part.startswith('inout')]

            for port in port_names:
                if port not in ports:
                    ports[port] = {'direction': direction, 'width': width}

    return module_name, ports

def generate_random_value(width):
    random_value = random.randint(0, (1 << width) - 1)
    return f"{width}'b{format(random_value, f'0{width}b')}"

def generate_testbench(module_name, ports, output_file, randomize_input=False, randomize_count=1):
    tb_module_name = f"{module_name}_tb"

    with open(output_file, "w") as tb_file:
        tb_file.write("`timescale 1ns/1ps\n")
        tb_file.write(f"module {tb_module_name};\n\n")

        tb_file.write(f"    // 信號宣告\n")
        
        declared_regs = set()
        declared_wires = set()

        for port, info in ports.items():
            direction = info['direction']
            width = info['width']
            width_str = f"[{width - 1}:0] " if width > 1 else ""
            
            if direction == "input":
                if port not in declared_regs:
                    tb_file.write(f"    reg {width_str}{port};\n")
                    declared_regs.add(port)
            elif direction in ["output", "inout"]:
                if port not in declared_wires:
                    tb_file.write(f"    wire {width_str}{port};\n")
                    declared_wires.add(port)
        tb_file.write("\n")

        tb_file.write("    // 模塊實例化\n")
        tb_file.write(f"    {module_name} uut (\n")
        
        port_count = len(ports)
        current_port = 0
        for port in ports.keys():
            current_port += 1
            comma = "," if current_port < port_count else ""
            tb_file.write(f"        .{port}({port}){comma}\n")
        tb_file.write("    );\n\n")

        tb_file.write("    // 測試激勵邏輯\n")
        tb_file.write("    initial begin\n")
        tb_file.write("        // 初始化輸入信號\n")
        for port, info in ports.items():
            if info['direction'] == "input":
                if randomize_input:
                    tb_file.write(f"        {port} = {generate_random_value(info['width'])};\n")
                else:
                    tb_file.write(f"        {port} = {info['width']}'b0;\n")
        tb_file.write("        #20;\n\n")
        
        tb_file.write("        // 隨機變化輸入信號\n")
        for i in range(randomize_count):
            tb_file.write(f"        // 第 {i + 1} 次變化\n")
            for port, info in ports.items():
                if info['direction'] == "input":
                    tb_file.write(f"        {port} = {generate_random_value(info['width'])};\n")
            tb_file.write("        #20;\n")
        tb_file.write("\n")

        tb_file.write("        // 結束模擬\n")
        tb_file.write("        #100;\n")
        tb_file.write("        $finish;\n")
        tb_file.write("    end\n\n")

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

        tb_file.write("    initial begin\n")
        tb_file.write(f'        $dumpfile("{tb_module_name}.vcd");\n')
        tb_file.write('        $dumpvars;\n')
        tb_file.write("    end\n\n")

        tb_file.write("endmodule\n")

    print(f"Testbench 已生成: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="自動生成 Verilog testbench")
    parser.add_argument("verilog_file", type=str, help="Verilog 原始檔案的路徑")
    parser.add_argument("--randomize", action="store_true", help="隨機生成輸入信號")
    parser.add_argument("--rand_count", type=int, default=1, help="隨機變化輸入信號的次數")

    args = parser.parse_args()

    verilog_file = args.verilog_file
    randomize_input = args.randomize
    randomize_count = args.rand_count

    if not os.path.exists(verilog_file):
        raise FileNotFoundError(f"找不到指定的 Verilog 文件: {verilog_file}")

    try:
        module_name, ports = parse_verilog_file(verilog_file)
    except ValueError as e:
        print(f"解析錯誤: {e}")
        return

    base_name = os.path.splitext(os.path.basename(verilog_file))[0]
    tb_file_name = f"{base_name}_tb.v"
    tb_file_path = os.path.join(os.path.dirname(verilog_file), tb_file_name)

    generate_testbench(module_name, ports, tb_file_path, randomize_input, randomize_count)

if __name__ == "__main__":
    main()
