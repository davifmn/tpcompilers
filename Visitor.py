import sys
from abc import ABC, abstractmethod
from Expression import *
import Asm as AsmModule


class Visitor(ABC):
    """
    The visitor pattern consists of two abstract classes: the Expression and the
    Visitor. The Expression class defines on method: 'accept(visitor, args)'.
    This method takes in an implementation of a visitor, and the arguments that
    are passed from expression to expression. The Visitor class defines one
    specific method for each subclass of Expression. Each instance of such a
    subclasse will invoke the right visiting method.
    """

    @abstractmethod
    def visit_var(self, exp, arg):
        pass

    @abstractmethod
    def visit_bln(self, exp, arg):
        pass

    @abstractmethod
    def visit_num(self, exp, arg):
        pass

    @abstractmethod
    def visit_eql(self, exp, arg):
        pass

    @abstractmethod
    def visit_add(self, exp, arg):
        pass

    @abstractmethod
    def visit_sub(self, exp, arg):
        pass

    @abstractmethod
    def visit_mul(self, exp, arg):
        pass

    @abstractmethod
    def visit_div(self, exp, arg):
        pass

    @abstractmethod
    def visit_leq(self, exp, arg):
        pass

    @abstractmethod
    def visit_lth(self, exp, arg):
        pass

    @abstractmethod
    def visit_neg(self, exp, arg):
        pass

    @abstractmethod
    def visit_not(self, exp, arg):
        pass

    @abstractmethod
    def visit_let(self, exp, arg):
        pass


class RenameVisitor(ABC):
    """
    This visitor traverses the AST of a program, renaming variables to ensure
    that they all have different names.

    Usage:
        >>> e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
        >>> e1 = Let('x', e0, Mul(Var('x'), Num(10)))
        >>> e0.identifier == e1.identifier
        True

        >>> e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
        >>> e1 = Let('x', e0, Mul(Var('x'), Num(10)))
        >>> r = RenameVisitor()
        >>> e1.accept(r, {})
        >>> e0.identifier == e1.identifier
        False

        >>> x0 = Var('x')
        >>> x1 = Var('x')
        >>> e0 = Let('x', Num(2), Add(x0, Num(3)))
        >>> e1 = Let('x', e0, Mul(x1, Num(10)))
        >>> x0.identifier == x1.identifier
        True

        >>> x0 = Var('x')
        >>> x1 = Var('x')
        >>> e0 = Let('x', Num(2), Add(x0, Num(3)))
        >>> e1 = Let('x', e0, Mul(x1, Num(10)))
        >>> r = RenameVisitor()
        >>> e1.accept(r, {})
        >>> x0.identifier == x1.identifier
        False
    """

    def __init__(self):
        self.var_scope = {}

    def _generate_unique_name(self, var_name):

        if var_name not in self.var_scope:
            self.var_scope[var_name] = []

        unique_name = f"{var_name}_{len(self.var_scope[var_name])}"

        self.var_scope[var_name].append(unique_name)

        return unique_name

    def _pop_variable(self, var_name):

        if var_name in self.var_scope and self.var_scope[var_name]:
            self.var_scope[var_name].pop()

    def _get_current_var_name(self, var_name):

        if var_name in self.var_scope and self.var_scope[var_name]:
            return self.var_scope[var_name][-1]
        return var_name

    def visit_var(self, exp, arg):
        exp.identifier = self._get_current_var_name(exp.identifier)

    def visit_bln(self, exp, arg):
        pass

    def visit_num(self, exp, arg):
        pass

    def visit_eql(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_add(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_sub(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_mul(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_div(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_leq(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_lth(self, exp, arg):
        exp.left.accept(self, arg)
        exp.right.accept(self, arg)

    def visit_neg(self, exp, arg):
        exp.exp.accept(self, arg)

    def visit_not(self, exp, arg):
        exp.exp.accept(self, arg)

    def visit_let(self, exp, arg):

        exp.exp_def.accept(self, arg)
        self._generate_unique_name(exp.identifier)
        exp.exp_body.accept(self, arg)
        save = exp.identifier
        exp.identifier = self._get_current_var_name(save)

        self._pop_variable(save)


class GenVisitor(Visitor):
    """
    The GenVisitor class compiles arithmetic expressions into a low-level
    language.
    """

    def __init__(self):
        self.next_var_counter = 0
        self.var_scope = {}

    def next_var_name(self):
        self.next_var_counter += 1
        return f"v{self.next_var_counter}"

    def _generate_unique_name(self, var_name):

        if var_name not in self.var_scope:
            self.var_scope[var_name] = []

        unique_name = f"{var_name}_{len(self.var_scope[var_name])}"

        self.var_scope[var_name].append(unique_name)

        return unique_name

    def _pop_variable(self, var_name):

        if var_name in self.var_scope and self.var_scope[var_name]:
            self.var_scope[var_name].pop()

    def _get_current_var_name(self, var_name, prog):

        if var_name in self.var_scope and self.var_scope[var_name]:
            return self.var_scope[var_name][-1]
        else:
            try:
                prog.get_val(var_name)
                return var_name
            except SystemExit:
                sys.exit(f"Variavel inexistente {var_name}")

    def visit_var(self, exp, prog):
        """
        Usage:
            >>> e = Var('x')
            >>> p = AsmModule.Program(0, {"x":1}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            1
        """
        return self._get_current_var_name(exp.identifier, prog)

    def visit_bln(self, exp, prog):
        """
        Usage:
            >>> e = Bln(True)
            >>> p = AsmModule.Program(0, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            1

            >>> e = Bln(False)
            >>> p = AsmModule.Program(0, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            0
        """
        if not exp.bln:
            return "x0"

        v_reg = self.next_var_name()
        prog.add_inst(AsmModule.Addi(v_reg, "x0", 1))
        return v_reg

    def visit_num(self, exp, prog):
        """
        Usage:
            >>> e = Num(13)
            >>> p = AsmModule.Program(0, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            13
        """
        v_reg = self.next_var_name()
        prog.add_inst(AsmModule.Addi(v_reg, "x0", exp.num))
        return v_reg

    def visit_eql(self, exp, prog):
        """
        >>> e = Eql(Num(13), Num(13))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Eql(Num(13), Num(10))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Eql(Num(-1), Num(1))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)
        v1_reg = self.next_var_name()
        prog.add_inst(AsmModule.Slt(v1_reg, left_reg, right_reg))

        v2_reg = self.next_var_name()
        prog.add_inst(AsmModule.Slt(v2_reg, right_reg, left_reg))

        v3_reg = self.next_var_name()
        prog.add_inst(AsmModule.Xor(v3_reg, v1_reg, v2_reg))

        v_reg = self.next_var_name()
        prog.add_inst(AsmModule.Xori(v_reg, v3_reg, 1))

        return v_reg

    def visit_add(self, exp, prog):
        """
        >>> e = Add(Num(13), Num(-13))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Add(Num(13), Num(10))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        23
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)

        v_reg = self.next_var_name()
        prog.add_inst(AsmModule.Add(v_reg, left_reg, right_reg))

        return v_reg

    def visit_sub(self, exp, prog):
        """
        >>> e = Sub(Num(13), Num(-13))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        26

        >>> e = Sub(Num(13), Num(10))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        3
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)

        v_reg = self.next_var_name()
        prog.add_inst(AsmModule.Sub(v_reg, left_reg, right_reg))

        return v_reg

    def visit_mul(self, exp, prog):
        """
        >>> e = Mul(Num(13), Num(2))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        26

        >>> e = Mul(Num(13), Num(10))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        130
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)
        v_reg = self.next_var_name()
        prog.add_inst(AsmModule.Mul(v_reg, left_reg, right_reg))

        return v_reg

    def visit_div(self, exp, prog):
        """
        >>> e = Div(Num(13), Num(2))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        6

        >>> e = Div(Num(13), Num(10))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)
        v_reg = self.next_var_name()
        prog.add_inst(AsmModule.Div(v_reg, left_reg, right_reg))

        return v_reg

    def visit_leq(self, exp, prog):
        """
        >>> e = Leq(Num(3), Num(2))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Leq(Num(3), Num(3))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(2), Num(3))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(-3), Num(-2))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(-3), Num(-3))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(-2), Num(-3))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)
        v_reg = self.next_var_name()
        prog.add_inst(AsmModule.Slt(v_reg, right_reg, left_reg))

        v2_reg = self.next_var_name()
        prog.add_inst(AsmModule.Xori(v2_reg, v_reg, 1))

        return v2_reg

    def visit_lth(self, exp, prog):
        """
        >>> e = Lth(Num(3), Num(2))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Lth(Num(3), Num(3))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Lth(Num(2), Num(3))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1
        """
        left_reg = exp.left.accept(self, prog)
        right_reg = exp.right.accept(self, prog)
        v_reg = self.next_var_name()
        prog.add_inst(AsmModule.Slt(v_reg, left_reg, right_reg))

        return v_reg

    def visit_neg(self, exp, prog):
        """
        >>> e = Neg(Num(3))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        -3

        >>> e = Neg(Num(0))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Neg(Num(-3))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        3
        """
        left_reg = exp.exp.accept(self, prog)
        v_reg = self.next_var_name()
        prog.add_inst(AsmModule.Addi(v_reg, "x0", -1))

        v1_reg = self.next_var_name()
        prog.add_inst(AsmModule.Mul(v1_reg, left_reg, v_reg))

        return v1_reg

    def visit_not(self, exp, prog):
        """
        >>> e = Not(Bln(True))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Not(Bln(False))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Not(Num(0))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Not(Num(-2))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Not(Num(2))
        >>> p = AsmModule.Program(0, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        left_reg = exp.exp.accept(self, prog)

        v_reg = self.next_var_name()
        prog.add_inst(AsmModule.Slt(v_reg, "x0", left_reg))

        v1_reg = self.next_var_name()
        prog.add_inst(AsmModule.Slt(v1_reg, left_reg, "x0"))

        v2_reg = self.next_var_name()
        prog.add_inst(AsmModule.Add(v2_reg, v_reg, v1_reg))

        v3_reg = self.next_var_name()
        prog.add_inst(AsmModule.Xori(v3_reg, v2_reg, 1))

        return v3_reg

    def visit_let(self, exp, prog):
        """
        Usage:
            >>> e = Let('v', Not(Bln(False)), Var('v'))
            >>> p = AsmModule.Program(0, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            1

            >>> e = Let('v', Num(2), Add(Var('v'), Num(3)))
            >>> p = AsmModule.Program(0, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            5

            >>> e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
            >>> e1 = Let('y', e0, Mul(Var('y'), Num(10)))
            >>> p = AsmModule.Program(0, {}, [])
            >>> g = GenVisitor()
            >>> v = e1.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            50
        """
        v_reg = exp.exp_def.accept(self, prog)
        new_name = self._generate_unique_name(exp.identifier)
        prog.add_inst(AsmModule.Addi(new_name, v_reg, 0))

        result_reg = exp.exp_body.accept(self, prog)

        self._pop_variable(exp.identifier)

        return result_reg
