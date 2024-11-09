import re
import argparse
import os
import random

def parse_verilog_file(file_path):
    module_name = None
    ports = {}

    with open(file_path, 'r') as file:
        content = file.read()

    start_index = content.find('module') + len('module')
    end_index = content.find('(', start_index)
    module_header = content[start_index:end_index]

    module_parts = module_header.split('(')
    module_name = module_parts[0].strip()

    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith('input') or line.startswith('output') or line.startswith('inout'):
            parts = line.split()
            if len(parts) < 2:
                continue  # 略過不完整的行
            
            direction = parts[0]
            bit_width = 1
            match = re.search(r'\[(\d+):0\]', line)
            if match:
                bit_width = int(match.group(1)) + 1

            port_names = [part.strip().split()[-1] for part in line.replace(';', '').split(',') if part.strip()]
            for port in port_names:
                if port and port not in ports:
                    ports[port] = {"direction": direction, "bit_width": bit_width}

    return module_name, ports


def generate_testbench(module_name, ports, output_file, clock_signal="clk", reset_signal="rst", randomize=False, randomize_count=1):
    tb_module_name = f"{module_name}_tb"
    
    with open(output_file, "w") as tb_file:
        tb_file.write("`timescale 1ns/1ps\n")
        tb_file.write(f"module {tb_module_name};\n\n")

        tb_file.write(f"    reg {clock_signal};\n" if clock_signal else "")
        tb_file.write(f"    reg {reset_signal};\n" if reset_signal else "")

        for port, info in ports.items():
            if info["direction"] == "input" and port not in [clock_signal, reset_signal]:
                tb_file.write(f"    reg [{info['bit_width']-1}:0] {port};\n")
            elif info["direction"] in ["output", "inout"]:
                tb_file.write(f"    wire [{info['bit_width']-1}:0] {port};\n")
        tb_file.write("\n")

        tb_file.write("    // 模組實例化\n")
        tb_file.write(f"    {module_name} uut (\n")
        for idx, port in enumerate(ports):
            comma = "," if idx < len(ports) - 1 else ""
            tb_file.write(f"        .{port}({port}){comma}\n")
        tb_file.write("    );\n\n")

        if clock_signal:
            tb_file.write("    initial begin\n")
            tb_file.write(f"        {clock_signal} = 0;\n")
            tb_file.write(f"        forever #5 {clock_signal} = ~{clock_signal};\n")
            tb_file.write("    end\n\n")

        if reset_signal:
            tb_file.write("    initial begin\n")
            tb_file.write(f"        {reset_signal} = 1;\n")
            tb_file.write(f"        #10 {reset_signal} = 0;\n")
            tb_file.write("    end\n\n")

        tb_file.write("    initial begin\n")
        tb_file.write("        // 初始化輸入信號\n")
        for port, info in ports.items():
            if info["direction"] == "input" and port not in [clock_signal, reset_signal]:
                tb_file.write(f"        {port} = {info['bit_width']}'b0;\n")
        tb_file.write("        #20;\n\n")

        if randomize:
            tb_file.write("        // 隨機變化輸入信號\n")
            for _ in range(randomize_count):
                for port, info in ports.items():
                    if info["direction"] == "input" and port not in [clock_signal, reset_signal]:
                        random_value = random.randint(0, 2**info["bit_width"] - 1)
                        tb_file.write(f"        {port} = {info['bit_width']}'b{random_value:0{info['bit_width']}b};\n")
                tb_file.write("        #20;\n")
        tb_file.write("        $finish;\n")
        tb_file.write("    end\n\n")

        tb_file.write("    initial begin\n")
        tb_file.write('        $monitor("Time=%0d, ')
        tb_file.write(', '.join(f'{port}=%b' for port in ports.keys()))
        tb_file.write('", $time')
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
    parser.add_argument("--clock", type=str, default="clk", help="時鐘信號名稱，默認為 'clk'")
    parser.add_argument("--reset", type=str, default="rst", help="重置信號名稱，默認為 'rst'")
    parser.add_argument("--randomize", action="store_true", help="啟用隨機輸入信號")
    parser.add_argument("--rand_count", type=int, default=1, help="隨機變化的次數")
    
    args = parser.parse_args()

    verilog_file = args.verilog_file
    clock_signal = args.clock
    reset_signal = args.reset
    randomize = args.randomize
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

    generate_testbench(module_name, ports, tb_file_path, clock_signal, reset_signal, randomize, randomize_count)

if __name__ == "__main__":
    main()
