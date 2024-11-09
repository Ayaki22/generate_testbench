<center>
    <h1 align="center">Generate testbench</h1>
    <p align="center">
        <strong>Last updated:</strong> 10 Nov 2024<br>
    </p> 
</center>

# About
This repository is what I used to generate testbench when I was learning Verilog. It has two purposes, generating testbench for combination circuit or sequential circuit. You only need to use command to quickly generate it.

# Getting Started
### Installation
1. Clone this repository:
```
git clone https://github.com/Ayaki22/generate_testbench.git
```
2. Use command
* Combination circuit
```
python gtb_comb.py [your verilog(.v)] --randomize --rand_count [random number of times you want]
```
* Sequential circuit
```
python gtb_seq.py [your verilog(.v)] --clock [your clock name] --reset [your reset name] --randomize --rand_count [random number of times you want]
```

### Example
* Combination circuit
```
python gtb_comb.py ./MUX/MUX2to1.v --randomize --rand_count 10  
```
* Sequential circuit
```
python gtb_seq.py ./FDiv/Acc32.v --clock clk --reset reset --randomize --rand_count 5
```