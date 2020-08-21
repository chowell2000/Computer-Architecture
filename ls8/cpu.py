"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.fl = 0
        self.ir = 0
        self.pc = 0
        self.ram= [0] * 0xFF

        # print(self.reg)
        # print(self.fl)
        # print(len(self.ram))

        pass

    def load(self):
        """Load a program into memory."""
        address = 0

        if len(sys.argv) != 2:
            print("Program file name needed")
            return
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    comment_split = line.split('#')
                    n = comment_split[0].strip()

                    if n == '':
                        continue
                    x = int(n,2)
                    self.ram[address] = x
                    address += 1
                    # print(f"{x:08b}: {x:d}")
        except:
            print('Program file not found')
            return
        # address = 0

        # For now, we've just hardcoded a program:
        #
        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]
        #
        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1



    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, MAR):
        return self.ram[MAR]


    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR
        return

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
        ADD = 0xA0
        ADDI = 0xFF
        CALL = 0x50
        CMP = 0xA7
        HLT = 0x01
        JMP = 0x54
        JEQ = 0x55
        JNE = 0x56
        LDI = 0b10000010
        PRN = 0x47
        MUL = 0b10100010
        PUSH = 0x45
        POP = 0x46
        RET = 0x11



        ir = self.ram_read(self.pc)
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)

        # print(ir)
        # print(operand_a)
        # print(operand_b)

        while ir != HLT:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if ir == LDI:
                self.ram_write(operand_a, operand_b)
                self.pc += 3
            elif ir == PRN:
                print(self.ram_read(operand_a))
                self.pc +=2
            elif ir == MUL:
                in_a = self.ram_read(operand_a)
                in_b = self.ram_read(operand_b)
                self.ram_write(operand_a, in_a * in_b)
                self.pc += 3
            elif ir == PUSH:
                self.reg[7] -= 1
                value = self.ram_read(operand_a)
                self.ram_write(self.reg[7], value)
                self.pc += 2
            elif ir == POP:
                value = self.ram_read(self.reg[7])
                self.ram_write(operand_a, value)
                self.reg[7] += 1
                self.pc += 2
            elif ir == CALL:
                self.reg[7] -= 1
                self.ram_write(self.reg[7], self.pc + 2)
                self.pc = self.ram_read(operand_a)
            elif ir == RET:
                self.pc = self.ram_read(self.reg[7])
                self.reg[7] += 1
            elif ir == ADD:
                value = self.ram_read(operand_a) + self.ram_read(operand_b)
                self.ram_write(operand_a, value)
                self.pc += 3
                # print(value)
            elif ir == JMP:
                self.pc = self.ram_read(operand_a)
            elif ir == CMP:
                value_a = self.ram_read(operand_a)
                value_b = self.ram_read(operand_b)
                if value_a == value_b:
                    self.fl = 0b00000001
                elif value_a > value_b:
                    self.fl = 0b00000100
                elif value_b > value_a:
                    self.fl = 0b00000010
                else:
                    self.fl = 0
                self.pc += 3
            elif ir == JEQ:
                if self.fl == 0b00000001:
                    self.pc = self.ram_read(operand_a)
                else:
                    self.pc += 2
            elif ir == JNE:
                if self.fl != 0b00000001:
                    self.pc = self.ram_read(operand_a)
                else:
                    self.pc += 2
            elif ir == ADDI:
                value = self.ram_read(operand_a) + operand_b
                self.ram_write(operand_a, value)

        return