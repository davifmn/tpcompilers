"""
This file contains the implementation of a simple interpreter of low-level
instructions. The interpreter takes a program, represented as an array of
instructions, plus an environment, which is a map that associates variables with
values. The following instructions are recognized:

    * add rd, rs1, rs2: rd = rs1 + rs2
    * addi rd, rs1, imm: rd = rs1 + imm
    * mul rd, rs1, rs2: rd = rs1 * rs2
    * sub rd, rs1, rs2: rd = rs1 - rs2
    * xor rd, rs1, rs2: rd = rs1 ^ rs2
    * xori rd, rs1, imm: rd = rs1 ^ imm
    * div rd, rs1, rs2: rd = rs1 // rs2 (signed integer division)
    * slt rd, rs1, rs2: rd = (rs1 < rs2) ? 1 : 0 (signed comparison)
    * slti rd, rs1, imm: rd = (rs1 < imm) ? 1 : 0
    * beq rs1, rs2, lab: pc = lab if rs1 == rs2 else pc + 1
    * jal rd, lab: rd = pc + 1 and pc = lab
    * jalr rd, rs1, offset: rd = pc + 1 and pc = rs1 + offset
    * sw reg, offset(rs1): mem[offset+rs1] = reg
    * lw reg, offset(rs1): reg = mem[offset+rs1]

This file uses doctests all over. To test it, just run python 3 as follows:
"python3 -m doctest Asm.py". The program uses syntax that is excluive of
Python 3. It will not work with standard Python 2.
"""

import sys
from collections import deque
from abc import ABC, abstractmethod


class Program:
    """
    The 'Program' is a list of instructions plus an environment that associates
    names with values, plus a program counter, which marks the next instruction
    that must be executed. The environment contains a special variable x0,
    which always contains the value zero.
    """

    def __init__(self, memory_size, env, insts):
        self.__mem = memory_size * [0]
        self.__env = env
        self.__insts = insts
        self.pc = 0
        self.registers = {"x0", "a0", "a1", "a2", "a3", "ra", "sp"}
        for reg in self.registers:
            self.__env[reg] = 0
        self.__env["sp"] = memory_size

    def reset_env(self):
        for reg in self.registers:
            self.__env[reg] = 0
        self.__env["sp"] = len(self.__mem)

    def get_inst(self):
        if self.pc >= 0 and self.pc < len(self.__insts):
            inst = self.__insts[self.pc]
            self.pc += 1
            return inst
        else:
            return None

    def get_number_of_instructions(self):
        return len(self.__insts)

    def add_inst(self, inst):
        self.__insts.append(inst)

    def get_pc(self):
        return self.pc

    def set_pc(self, pc):
        self.pc = pc

    def set_val(self, name, value):
        if name in self.registers and name != "x0":
            self.__env[name] = value
        else:
            sys.exit(f"Undefined register: {name}")

    def set_mem(self, addr, value):
        self.__mem[addr] = value

    def get_mem(self, addr):
        if addr < 0 or addr >= len(self.__mem):
            sys.exit(f"Invalid memory address: {addr}")
        return self.__mem[addr]

    def get_val(self, name):
        """
        The register x0 always contains the value zero:

        >>> p = Program(0, {}, [])
        >>> p.get_val("x0")
        0
        """
        if name in self.__env:
            return self.__env[name]
        else:
            sys.exit(f"Undefined register: {name}")

    def print_env(self):
        for name, val in sorted(self.__env.items()):
            print(f"{name}: {val}")

    def print_insts(self):
        counter = 0
        for inst in self.__insts:
            print("%03d: %s" % (counter, str(inst)))
            counter += 1
        print("%03d: %s" % (counter, "END"))

    def get_insts(self):
        return self.__insts.copy()

    def set_insts(self, insts):
        self.__insts = insts

    def eval(self):
        """
         This function evaluates a program until there is no more instructions
         to evaluate.

         Example:
             >>> insts = [Add("t0", "b0", "b1"), Sub("x1", "t0", "b2")]
             >>> p = Program(0, {"b0":2, "b1":3, "b2": 4}, insts)
             >>> p.eval()
             >>> p.print_env()
             b0: 2
             b1: 3
             b2: 4
             sp: 0
             t0: 5
             x0: 0
             x1: 1

        Notice that it is not possible to change 'x0':
             >>> insts = [Add("x0", "b0", "b1")]
             >>> p = Program(0, {"b0":2, "b1":3}, insts)
             >>> p.eval()
             >>> p.print_env()
             b0: 2
             b1: 3
             sp: 0
             x0: 0
        """
        inst = self.get_inst()
        while inst:
            inst.eval(self)
            inst = self.get_inst()


def max(a, b):
    """
    This example computes the maximum between a and b.

    Example:
        >>> max(2, 3)
        3

        >>> max(3, 2)
        3

        >>> max(-3, -2)
        -2

        >>> max(-2, -3)
        -2
    """
    p = Program(0, {}, [])
    p.set_val("rs1", a)
    p.set_val("rs2", b)
    p.add_inst(Slt("t0", "rs2", "rs1"))
    p.add_inst(Slt("t1", "rs1", "rs2"))
    p.add_inst(Mul("t0", "t0", "rs1"))
    p.add_inst(Mul("t1", "t1", "rs2"))
    p.add_inst(Add("rd", "t0", "t1"))
    p.eval()
    return p.get_val("rd")


def distance_with_acceleration(V, A, T):
    """
    This example computes the position of an object, given its velocity (V),
    its acceleration (A) and the time (T), assuming that it starts at position
    zero, using the formula D = V*T + (A*T^2)/2.

    Example:
        >>> distance_with_acceleration(3, 4, 5)
        65
    """
    p = Program(0, {}, [])
    p.set_val("rs1", V)
    p.set_val("rs2", A)
    p.set_val("rs3", T)
    p.add_inst(Addi("two", "x0", 2))
    p.add_inst(Mul("t0", "rs1", "rs3"))
    p.add_inst(Mul("t1", "rs3", "rs3"))
    p.add_inst(Mul("t2", "rs2", "t1"))
    p.add_inst(Div("t2", "t2", "two"))
    p.add_inst(Add("rd", "t0", "t2"))
    p.eval()
    return p.get_val("rd")


class Inst(ABC):
    """
    The representation of instructions. Every instruction refers to a program
    during its evaluation.
    """

    def __init__(self):
        pass

    @abstractmethod
    def get_opcode(self):
        raise NotImplementedError

    @abstractmethod
    def eval(self, prog):
        raise NotImplementedError


class BranchOp(Inst):
    """
    The general class of branching instructions. These instructions can change
    the control flow of a program. Normally, the next instruction is given by
    pc + 1. A branch might change pc to point out to a different label..
    """

    def set_target(self, lab):
        assert isinstance(lab, int)
        self.lab = lab


class Beq(BranchOp):
    """
    beq rs1, rs2, lab:
    Jumps to label lab if the value in rs1 is equal to the value in rs2.
    """

    def __init__(self, rs1, rs2, lab=None):
        assert isinstance(rs1, str) and isinstance(rs2, str)
        self.rs1 = rs1
        self.rs2 = rs2
        if lab != None:
            assert isinstance(lab, int)
        self.lab = lab

    def get_opcode(self):
        return "beq"

    def __str__(self):
        op = self.get_opcode()
        return f"{op} {self.rs1} {self.rs2} {self.lab}"

    def eval(self, prog):
        if prog.get_val(self.rs1) == prog.get_val(self.rs2):
            prog.set_pc(self.lab)


class Jal(BranchOp):
    """
    jal rd lab:
    Stores the return address (PC+1) on register rd, then jumps to label lab.
    If rd is x0, then it does not write on the register. In this case, notice
    that `jal x0 lab` is equivalent to an unconditional jump to `lab`.

    Example:
        >>> i = Jal("a", 20)
        >>> str(i)
        'jal a 20'

        >>> p = Program(10, env={}, insts=[Jal("a", 20)])
        >>> p.eval()
        >>> p.get_pc(), p.get_val("a")
        (20, 2)

        >>> p = Program(10, env={}, insts=[Jal("x0", 20)])
        >>> p.eval()
        >>> p.get_pc(), p.get_val("x0")
        (20, 0)
    """

    def __init__(self, rd, lab=None):
        assert isinstance(rd, str)
        self.rd = rd
        if lab != None:
            assert isinstance(lab, int)
        self.lab = lab

    def get_opcode(self):
        return "jal"

    def __str__(self):
        op = self.get_opcode()
        return f"{op} {self.rd} {self.lab}"

    def eval(self, prog):
        if self.rd != "x0":
            # Notice that Jal and Jalr set pc to pc + 1. However, when we fetch
            # an instruction, we already increment the PC. Therefore, by using
            # get_pc, we are indeed, reading pc + 1.
            prog.set_val(self.rd, prog.get_pc())
        prog.set_pc(self.lab)


class Jalr(BranchOp):
    """
    jalr rd, rs, offset
    The jalr rd, rs, offset instruction performs an indirect jump to the
    address computed by adding the value in rs to the immediate offset, and
    stores the address of the instruction following the jump into rd.

    Example:
        >>> i = Jalr("a", "b", 20)
        >>> str(i)
        'jalr a b 20'

        >>> p = Program(10, env={"b":30}, insts=[Jalr("a", "b", 20)])
        >>> p.eval()
        >>> p.get_pc(), p.get_val("a")
        (50, 2)

        >>> p = Program(10, env={"b":30}, insts=[Jalr("x0", "b", 20)])
        >>> p.eval()
        >>> p.get_pc(), p.get_val("x0")
        (50, 0)
    """

    def __init__(self, rd, rs, offset=0):
        assert isinstance(rd, str) and isinstance(rs, str)
        self.rd = rd
        self.rs = rs
        if offset != None:
            assert isinstance(offset, int)
        self.offset = offset

    def get_opcode(self):
        return "jalr"

    def __str__(self):
        op = self.get_opcode()
        return f"{op} {self.rd} {self.rs} {self.offset}"

    def eval(self, prog):
        rs_val = prog.get_val(self.rs)
        if self.rd != "x0":
            prog.set_val(self.rd, prog.get_pc())
        prog.set_pc(rs_val + self.offset)


class MemOp(Inst):
    """
    The general class of instructions that access memory. These instructions
    include loads and stores.
    """

    def __init__(self, rs1, offset, reg):
        assert isinstance(rs1, str) and isinstance(reg, str) and isinstance(offset, int)
        self.rs1 = rs1
        self.offset = offset
        self.reg = reg

    def __str__(self):
        op = self.get_opcode()
        return f"{op} {self.reg}, {self.offset}({self.rs1})"


class Sw(MemOp):
    """
    sw reg, offset(rs1)
    *(rs1 + offset) = reg

    * reg: The source register containing the data to be stored.
    * rs1: The base register containing the memory address.
    * offset: A 12-bit signed immediate that is added to rs1 to form the
      effective address.

    Example:
        >>> i = Sw("a", 0, "b")
        >>> str(i)
        'sw b, 0(a)'

        >>> p = Program(10, env={"b":2, "a":3}, insts=[Sw("a", 0, "b")])
        >>> p.eval()
        >>> p.get_mem(3)
        2
    """

    def eval(self, prog):
        val = prog.get_val(self.reg)
        addr = prog.get_val(self.rs1) + self.offset
        prog.set_mem(addr, val)

    def get_opcode(self):
        return "sw"


class Lw(MemOp):
    """
    lw reg, offset(rs1)
    reg = *(rs1 + offset)

    * reg: The destination register that will be overwritten.
    * rs1: The base register containing the memory address.
    * offset: A 12-bit signed immediate that is added to rs1 to form the
      effective address.

    Example:
        >>> i = Lw("a", 0, "b")
        >>> str(i)
        'lw b, 0(a)'

        >>> p = Program(10, env={"a":2}, insts=[Lw("a", 0, "b")])
        >>> p.eval()
        >>> p.get_val("b")
        0

        >>> insts = [Sw("a", 0, "b"), Lw("a", 0, "c")]
        >>> p = Program(10, env={"a":2, "b":5}, insts=insts)
        >>> p.eval()
        >>> p.get_val("c")
        5
    """

    def eval(self, prog):
        addr = prog.get_val(self.rs1) + self.offset
        val = prog.get_mem(addr)
        prog.set_val(self.reg, val)

    def get_opcode(self):
        return "lw"


class BinOp(Inst):
    """
    The general class of binary instructions. These instructions define a
    value, and use two values.
    """

    def __init__(self, rd, rs1, rs2):
        assert isinstance(rd, str) and isinstance(rs1, str) and isinstance(rs2, str)
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2

    def __str__(self):
        op = self.get_opcode()
        return f"{self.rd} = {op} {self.rs1} {self.rs2}"


class BinOpImm(Inst):
    """
    The general class of binary instructions where the second operand is an
    integer constant. These instructions define a value, and use one variable
    and one immediate constant.
    """

    def __init__(self, rd, rs1, imm):
        assert isinstance(rd, str) and isinstance(rs1, str) and isinstance(imm, int)
        self.rd = rd
        self.rs1 = rs1
        self.imm = imm

    def __str__(self):
        op = self.get_opcode()
        return f"{self.rd} = {op} {self.rs1} {self.imm}"


class Add(BinOp):
    """
    add rd, rs1, rs2: rd = rs1 + rs2

    Example:
        >>> i = Add("a", "b0", "b1")
        >>> str(i)
        'a = add b0 b1'

        >>> p = Program(0, env={"b0":2, "b1":3}, insts=[Add("a", "b0", "b1")])
        >>> p.eval()
        >>> p.get_val("a")
        5
    """

    def eval(self, prog):
        rs1 = prog.get_val(self.rs1)
        rs2 = prog.get_val(self.rs2)
        prog.set_val(self.rd, rs1 + rs2)

    def get_opcode(self):
        return "add"


class Addi(BinOpImm):
    """
    addi rd, rs1, imm: rd = rs1 + imm

    Example:
        >>> i = Addi("a", "b0", 1)
        >>> str(i)
        'a = addi b0 1'

        >>> p = Program(0, env={"b0":2}, insts=[Addi("a", "b0", 3)])
        >>> p.eval()
        >>> p.get_val("a")
        5
    """

    def eval(self, prog):
        rs1 = prog.get_val(self.rs1)
        prog.set_val(self.rd, rs1 + self.imm)

    def get_opcode(self):
        return "addi"


class Mul(BinOp):
    """
    mul rd, rs1, rs2: rd = rs1 * rs2

    Example:
        >>> i = Mul("a", "b0", "b1")
        >>> str(i)
        'a = mul b0 b1'

        >>> p = Program(0, env={"b0":2, "b1":3}, insts=[Mul("a", "b0", "b1")])
        >>> p.eval()
        >>> p.get_val("a")
        6
    """

    def eval(self, prog):
        rs1 = prog.get_val(self.rs1)
        rs2 = prog.get_val(self.rs2)
        prog.set_val(self.rd, rs1 * rs2)

    def get_opcode(self):
        return "mul"


class Sub(BinOp):
    """
    sub rd, rs1, rs2: rd = rs1 - rs2

    Example:
        >>> i = Sub("a", "b0", "b1")
        >>> str(i)
        'a = sub b0 b1'

        >>> p = Program(0, env={"b0":2, "b1":3}, insts=[Sub("a", "b0", "b1")])
        >>> p.eval()
        >>> p.get_val("a")
        -1
    """

    def eval(self, prog):
        rs1 = prog.get_val(self.rs1)
        rs2 = prog.get_val(self.rs2)
        prog.set_val(self.rd, rs1 - rs2)

    def get_opcode(self):
        return "sub"


class Xor(BinOp):
    """
    xor rd, rs1, rs2: rd = rs1 ^ rs2

    Example:
        >>> i = Xor("a", "b0", "b1")
        >>> str(i)
        'a = xor b0 b1'

        >>> p = Program(0, env={"b0":2, "b1":3}, insts=[Xor("a", "b0", "b1")])
        >>> p.eval()
        >>> p.get_val("a")
        1
    """

    def eval(self, prog):
        rs1 = prog.get_val(self.rs1)
        rs2 = prog.get_val(self.rs2)
        prog.set_val(self.rd, rs1 ^ rs2)

    def get_opcode(self):
        return "xor"


class Xori(BinOpImm):
    """
    xori rd, rs1, imm: rd = rs1 ^ imm

    Example:
        >>> i = Xori("a", "b0", 10)
        >>> str(i)
        'a = xori b0 10'

        >>> p = Program(0, env={"b0":2}, insts=[Xori("a", "b0", 3)])
        >>> p.eval()
        >>> p.get_val("a")
        1
    """

    def eval(self, prog):
        rs1 = prog.get_val(self.rs1)
        prog.set_val(self.rd, rs1 ^ self.imm)

    def get_opcode(self):
        return "xori"


class Div(BinOp):
    """
    div rd, rs1, rs2: rd = rs1 // rs2 (signed integer division)
    Notice that RISC-V does not have an instruction exactly like this one.
    The div operator works on floating-point numbers; not on integers.

    Example:
        >>> i = Div("a", "b0", "b1")
        >>> str(i)
        'a = div b0 b1'

        >>> p = Program(0, env={"b0":8, "b1":3}, insts=[Div("a", "b0", "b1")])
        >>> p.eval()
        >>> p.get_val("a")
        2
    """

    def eval(self, prog):
        rs1 = prog.get_val(self.rs1)
        rs2 = prog.get_val(self.rs2)
        prog.set_val(self.rd, rs1 // rs2)

    def get_opcode(self):
        return "div"


class Slt(BinOp):
    """
    slt rd, rs1, rs2: rd = (rs1 < rs2) ? 1 : 0 (signed comparison)

    Example:
        >>> i = Slt("a", "b0", "b1")
        >>> str(i)
        'a = slt b0 b1'

        >>> p = Program(0, env={"b0":2, "b1":3}, insts=[Slt("a", "b0", "b1")])
        >>> p.eval()
        >>> p.get_val("a")
        1

        >>> p = Program(0, env={"b0":3, "b1":3}, insts=[Slt("a", "b0", "b1")])
        >>> p.eval()
        >>> p.get_val("a")
        0

        >>> p = Program(0, env={"b0":3, "b1":2}, insts=[Slt("a", "b0", "b1")])
        >>> p.eval()
        >>> p.get_val("a")
        0
    """

    def eval(self, prog):
        rs1 = prog.get_val(self.rs1)
        rs2 = prog.get_val(self.rs2)
        prog.set_val(self.rd, 1 if rs1 < rs2 else 0)

    def get_opcode(self):
        return "slt"


class Slti(BinOpImm):
    """
    slti rd, rs1, imm: rd = (rs1 < imm) ? 1 : 0
    (signed comparison with immediate)

    Example:
        >>> i = Slti("a", "b0", 0)
        >>> str(i)
        'a = slti b0 0'

        >>> p = Program(0, env={"b0":2}, insts=[Slti("a", "b0", 3)])
        >>> p.eval()
        >>> p.get_val("a")
        1

        >>> p = Program(0, env={"b0":3}, insts=[Slti("a", "b0", 3)])
        >>> p.eval()
        >>> p.get_val("a")
        0

        >>> p = Program(0, env={"b0":3}, insts=[Slti("a", "b0", 2)])
        >>> p.eval()
        >>> p.get_val("a")
        0
    """

    def eval(self, prog):
        rs1 = prog.get_val(self.rs1)
        prog.set_val(self.rd, 1 if rs1 < self.imm else 0)

    def get_opcode(self):
        return "slti"