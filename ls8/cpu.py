"""CPU functionality."""

import re
import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.sp = self.reg[7]
        self.ram = [None] * 256
        self.pc = 0
        self.running = True
        self.branchtable = {
            0b10000010: self.LDI,
            0b01000111: self.PRN, 
            0b00000001: self.HLT, 
            0b10100010: self.MUL, 
            0b01000101: self.PUSH,
            0b01000110: self.POP
        }
        

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR
        print(f"Address: {MAR} = {MDR}")

    def load(self, argument):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        try:
            with open(argument, "r") as f:
                program = f.read()

            instructions = re.findall(r'\d{8}', program)
            for address, instruction in enumerate(instructions):
                x = int(instruction, 2)
                self.ram[address] = x
        except FileNotFoundError:
            print("File error from CL")


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "SUB":
            self.reg[reg_a] += -self.reg[reg_b]
        elif op == "MUL":
            product = self.reg[reg_a] * self.reg[reg_b]
            self.reg[reg_a] = product
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        LDI  = 0b10000010 
        PRN = 0b01000111		        
        HLT = 0b00000001		
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110


        while self.running:
            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if IR in self.branchtable:
                self.branchtable[IR](operand_a, operand_b)
            else:
                print("Something's up here")
                self.running = False
           
    def HLT(self, operand_a, operand_b):
        self.running = False

    def LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3

    def PRN(self, operand_a, operand_b):
        print(self.reg[operand_a])
        self.pc += 2

    def PUSH(self, operand_a, operand_b):
        self.sp += -1
        self.ram[self.sp] = self.reg[operand_a]
        self.pc += 2

    def POP(self, operand_a, operand_b):
        value = self.ram[self.sp]
        self.reg[operand_a]= value
        self.sp += 1
        self.pc += 2

    def MUL(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3    