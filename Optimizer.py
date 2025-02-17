from abc import ABC, abstractmethod
from Asm import *


class Optimizer(ABC):
    """
    This class implements an "Optimization Pass". The pass receives a sequence
    of instructions stored in a program, and produces a new sequence of
    instructions.
    """

    def __init__(self, prog):
        self.prog = prog

    @abstractmethod
    def optimize(self):
        pass


class RegAllocator(Optimizer):
    """This file implements the register allocation pass."""

    def __init__(self, prog):
        self.prog = prog
        self.reg_map = {}
        self.mem_map = {}
        self.usable_regs = ["a1", "a2", "a3", "a0"]
        self.other_regs = ["x0", "ra", "sp"]
        self.alloc_action = {
            "addi": self.alloc_binary_op,
            "add": self.alloc_binary_op,
            "sub": self.alloc_binary_op,
            "mul": self.alloc_binary_op,
            "div": self.alloc_binary_op,
            "xor": self.alloc_binary_op,
            "xori": self.alloc_binary_op,
            "slt": self.alloc_binary_op,
            "slti": self.alloc_binary_op,
            "lw": self.alloc_load,
            "sw": self.alloc_store,
        }
        self.instructions_to_store = [
            "addi", "add", "sub", "mul", "div", "xor", "xori", "slt", "slti"]
        self.mem_counter = -1

    def inc_mem_counter(self):
        self.mem_counter += 1
        return self.mem_counter

    def get_val(self, var):
        """
        Informs the value that is associated with the variable var within
        the program prog.
        """
        if var in self.reg_map:
            return self.prog.get_val(self.reg_map[var])
        elif var in self.mem_map:
            return self.prog.get_mem((self.mem_map[var]))

        sys.exit(f"Variable {var} not found")

    def next_var_name(self):
        """Returns the name of the next available register."""
        for reg in self.usable_regs:
            if reg not in self.reg_map.values():
                return reg
        return None

    def get_var_name(self, var):
        """Returns the physical location (register or memory) for a virtual variable."""
        if var in self.other_regs:
            return var, None
        if var in self.reg_map:
            return self.reg_map[var], None
        elif var in self.mem_map:
            reg = self.next_var_name()
            self.reg_map[var] = reg
            return reg, Lw("x0", self.mem_map[var], reg)
        else:
            reg = self.next_var_name()
            self.reg_map[var] = reg
            return reg, None

    def optimize(self):
        """
        This function perform register allocation. It maps variables into
        memory, and changes instructions, so that they use one of the following
        registers:
        * x0: always the value zero. Can't change.
        * sp: the stack pointer. Starts with the memory size.
        * ra: the return address.
        * a0: function argument 0 (or return address)
        * a1: function argument 1
        * a2: function argument 2
        * a3: function argument 3

        Notice that next to each register we have suggested a usage. You can,
        of course, write on them and use them in other ways. But, at least x0
        and sp you should not overwrite. The first register you can't overwrite,
        actually. And sp is initialized with the number of memory addresses.
        It's good to use it to control the function stack.

        Examples:
        >>> insts = [Addi("a", "x0", 3)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        3

        >>> insts = [Addi("a", "x0", 1), Slti("b", "a", 2)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        1

        >>> insts = [Addi("a", "x0", 3), Slti("b", "a", 2), Xori("c", "b", 5)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        5

        >>> insts = [Addi("sp", "sp", -1),Addi("a", "x0", 7),Sw("sp", 0, "a")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_mem(p.get_val("sp"))
        7

        >>> insts = [Addi("sp", "sp", -1),Addi("a", "x0", 7),Sw("sp", 0, "a")]
        >>> insts += [Lw("sp", 0, "b"), Addi("c", "b", 6)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        13

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Add("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        7

        >>> insts = [Addi("a", "x0", 28),Addi("b", "x0", 4),Div("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        7

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Mul("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        12

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Xor("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        7

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Slt("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        1

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Slt("c", "b", "a")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_val("a1")
        0

        If you want, you can allocate Jal/Jalr/Beq instructions, but that's not
        necessary for this exercise.

        >>> insts = [Jal("a", 30)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> (p.get_pc(), p.get_val("a1") > 0)
        (30, True)

        >>> insts = [Addi("a", "x0", 30), Jalr("b", "a")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> (p.get_pc(), p.get_val("a1") > 0)
        (30, True)

        >>> insts = [Addi("a", "x0", 3), Addi("b", "a", 0), Beq("a", "b", 30)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_pc()
        30
        """

        new_insts = []
        for inst in self.prog.get_insts():
            action = self.alloc_action[inst.get_opcode()]
            last_insts = action(inst)
            new_insts += last_insts
        self.prog.set_insts(new_insts)

    def alloc_binary_op(self, inst):
        insts = []

        new_rs1, inst1 = self.get_var_name(inst.rs1)

        if hasattr(inst, 'imm'):
            new_rs2 = inst.imm
            inst2 = None
        else:
            new_rs2, inst2 = self.get_var_name(inst.rs2)

        if new_rs1 in self.other_regs or new_rs2 in self.other_regs:
            new_rd, inst3 = self.get_var_name(inst.rd)
        else:
            if new_rs1 not in self.other_regs:
                new_rd = new_rs1
            else:
                new_rd = new_rs2

            inst3 = None

        if inst1:
            insts.append(inst1)
        if inst2:
            insts.append(inst2)
        if inst3:
            insts.append(inst3)

        insts.append(inst.__class__(new_rd, new_rs1, new_rs2))

        if new_rd not in self.other_regs:
            mem_pos = self.inc_mem_counter()
            insts.append(Sw("x0", mem_pos, new_rd))
            self.mem_map[inst.rd] = mem_pos

            self.cleanup_maps(inst.rd)

        self.cleanup_maps(inst.rs1)

        if hasattr(inst, 'rs2'):
            self.cleanup_maps(inst.rs2)

        return insts

    def alloc_load(self, inst):
        insts = []
        new_reg, inst1 = self.get_var_name(inst.reg)
        new_rs1, inst2 = self.get_var_name(inst.rs1)

        if inst1:
            insts.append(inst1)

        if inst2:
            insts.append(inst2)

        insts.append(Lw(new_rs1, inst.offset, new_reg))

        self.cleanup_maps(inst.rs1)

        return insts

    def alloc_store(self, inst):
        insts = []
        new_reg, inst1 = self.get_var_name(inst.reg)
        new_rs1, inst2 = self.get_var_name(inst.rs1)

        if inst1:
            insts.append(inst1)

        if inst2:
            insts.append(inst2)

        insts.append(Sw(new_rs1, inst.offset, new_reg))

        mem_pos = self.prog.get_val(new_rs1) + inst.offset
        self.mem_map[inst.reg] = mem_pos

        self.cleanup_maps(inst.reg)
        return insts

    def cleanup_maps(self, *vars):
        for var in vars:
            if var in self.reg_map:
                del self.reg_map[var]
