"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = int('F4', 16)
        self.fl = 0b00000000
    
    def load(self, filename):
        """Load a program into memory."""
        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    # Ignore comments
                    comment_split = line.split("#")
                    num = comment_split[0].strip()
                    if num == "":
                        continue

                    value = int(num, 2) #base 2, adds 0b in front
                    self.ram[address] = value
                    address += 1

        except FileNotFoundError:
            print(f"{filename} not found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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
    
    def ram_read(self, address):
      return self.ram[address]
      
    def ram_write(self, value, address):
      self.ram[address] = value

    def run(self):
        """Run the CPU."""

        LDI = 0b10000010
        PRN = 0b01000111
        HLT = 0b00000001
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        ADD = 0b10100000
        CMP = 0b10100111
        JEQ = 0b01010101
        JNE = 0b01010110
        JMP = 0b01010100


        def handle_CALL(operand_a, operand_b):
          index_to_go = self.reg[operand_a]
          save_return_index = self.pc + 2
          self.sp -= 1
          self.ram[self.sp] = save_return_index
          self.pc = index_to_go
        
        def handle_RET(operand_a, operand_b):
            self.pc = self.ram[self.sp]
            self.sp += 1
        
        def handle_ADD(operand_a, operand_b):
          value1 = self.reg[operand_a]
          value2 = self.reg[operand_b]
          self.reg[operand_a] = value1 + value2
          self.pc += 3
        
        def handle_LDI(operand_a, operand_b):
          self.reg[operand_a] = operand_b
          self.pc += 3
        
        def handle_PRN(operand_a, operand_b=None):
          print(self.reg[operand_a])
          self.pc += 2
        
        def handle_MUL(operand_a, operand_b):
          self.reg[operand_a] = self.reg[operand_a] * self.reg[operand_b]
          self.pc += 3
        
        def handle_PUSH(operand_a=None, operand_b=None):
          reg = self.ram_read(self.pc + 1)
          val = self.reg[reg]
          self.sp -= 1
          self.ram[self.sp] = val
          self.pc += 2

        def handle_POP(operand_a=None, operand_b=None):
          reg = self.ram[self.pc + 1]
          val = self.ram[self.sp]
          self.reg[reg] = val
          self.sp += 1
          self.pc += 2
        
        def handle_CMP(operand_a, operand_b):
          value1 = self.reg[operand_a]
          value2 = self.reg[operand_b]
          if value1 < value2:
            self.fl = bin(4)
          if value1 > value2:
            self.fl = bin(2)
          if value1 == value2:
            self.fl = bin(1)
          
          self.pc += 3
        
        def handle_JEQ(operand_a, operand_b):
          jump_to = self.reg[operand_a]
          if self.fl == bin(1):
            self.pc = jump_to
          else:
            self.pc += 2
        
        def handle_JNE(operand_a, operand_b):
          jump_to = self.reg[operand_a]
          if self.fl == bin(4) or self.fl == bin(2):
            self.pc = jump_to
          else:
            self.pc += 2
        
        def handle_JMP(operand_a, operand_b):
          jump_to = self.reg[operand_a]
          self.pc = jump_to


        dispatch = {
          LDI: handle_LDI,
          PRN: handle_PRN,
          MUL: handle_MUL,
          PUSH: handle_PUSH,
          POP: handle_POP,
          CALL: handle_CALL,
          RET: handle_RET,
          ADD: handle_ADD,
          CMP: handle_CMP,
          JEQ: handle_JEQ,
          JNE: handle_JNE,
          JMP: handle_JMP
        }

        while True:
          IR = self.ram[self.pc]
          operand_a = self.ram_read(self.pc + 1)
          operand_b = self.ram_read(self.pc + 2)

          if IR == HLT:
            break
          else:
            if dispatch[IR]:
              dispatch[IR](operand_a, operand_b)
            else:
              print(f"Error: Unknown command: {IR}")
              break

