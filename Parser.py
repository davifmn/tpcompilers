import sys

from Expression import *
from Lexer import Token, TokenType

"""
This file implements the parser of logic and arithmetic expressions.

Precedence table:
    1: not ~ ()
    2: *   /
    3: +   -
    4: <   <=   >=   >
    5: =
    6: and
    7: or
    8: if-then-else

Notice that not 2 < 3 must be a type error, as we are trying to apply a boolean
operation (not) onto a number.

References:
    see https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm#classic
"""

class Parser:
    def __init__(self, tokens):
        """
        Initializes the parser. The parser keeps track of the list of tokens
        and the current token. For instance:
        """
        self.tokens = list(tokens)
        self.cur_token_idx = 0 # This is just a suggestion!
    
    def current_token(self):
        return self.tokens[self.cur_token_idx] if self.cur_token_idx < len(self.tokens) else None


    def parse(self):
        """
        
            Returns the expression associated with the stream of tokens.

            Examples:
            >>> parser = Parser([Token('123', TokenType.NUM)])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            123

            >>> parser = Parser([Token('True', TokenType.TRU)])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            True

            >>> parser = Parser([Token('False', TokenType.FLS)])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            False

            >>> tk0 = Token('~', TokenType.NEG)
            >>> tk1 = Token('123', TokenType.NUM)
            >>> parser = Parser([tk0, tk1])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            -123

            >>> tk0 = Token('3', TokenType.NUM)
            >>> tk1 = Token('*', TokenType.MUL)
            >>> tk2 = Token('4', TokenType.NUM)
            >>> parser = Parser([tk0, tk1, tk2])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            12

            >>> tk0 = Token('3', TokenType.NUM)
            >>> tk1 = Token('*', TokenType.MUL)
            >>> tk2 = Token('~', TokenType.NEG)
            >>> tk3 = Token('4', TokenType.NUM)
            >>> parser = Parser([tk0, tk1, tk2, tk3])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            -12

            >>> tk0 = Token('30', TokenType.NUM)
            >>> tk1 = Token('/', TokenType.DIV)
            >>> tk2 = Token('4', TokenType.NUM)
            >>> parser = Parser([tk0, tk1, tk2])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            7

            >>> tk0 = Token('3', TokenType.NUM)
            >>> tk1 = Token('+', TokenType.ADD)
            >>> tk2 = Token('4', TokenType.NUM)
            >>> parser = Parser([tk0, tk1, tk2])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            7

            >>> tk0 = Token('30', TokenType.NUM)
            >>> tk1 = Token('-', TokenType.SUB)
            >>> tk2 = Token('4', TokenType.NUM)
            >>> parser = Parser([tk0, tk1, tk2])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            26

            >>> tk0 = Token('2', TokenType.NUM)
            >>> tk1 = Token('*', TokenType.MUL)
            >>> tk2 = Token('(', TokenType.LPR)
            >>> tk3 = Token('3', TokenType.NUM)
            >>> tk4 = Token('+', TokenType.ADD)
            >>> tk5 = Token('4', TokenType.NUM)
            >>> tk6 = Token(')', TokenType.RPR)
            >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            14

            >>> tk0 = Token('4', TokenType.NUM)
            >>> tk1 = Token('==', TokenType.EQL)
            >>> tk2 = Token('4', TokenType.NUM)
            >>> parser = Parser([tk0, tk1, tk2])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            True

            >>> tk0 = Token('4', TokenType.NUM)
            >>> tk1 = Token('<=', TokenType.LEQ)
            >>> tk2 = Token('4', TokenType.NUM)
            >>> parser = Parser([tk0, tk1, tk2])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            True

            >>> tk0 = Token('4', TokenType.NUM)
            >>> tk1 = Token('<', TokenType.LTH)
            >>> tk2 = Token('4', TokenType.NUM)
            >>> parser = Parser([tk0, tk1, tk2])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            False

            >>> tk0 = Token('not', TokenType.NOT)
            >>> tk1 = Token('(', TokenType.LPR)
            >>> tk2 = Token('4', TokenType.NUM)
            >>> tk3 = Token('<', TokenType.LTH)
            >>> tk4 = Token('4', TokenType.NUM)
            >>> tk5 = Token(')', TokenType.RPR)
            >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            True

            >>> tk0 = Token('true', TokenType.TRU)
            >>> tk1 = Token('or', TokenType.ORX)
            >>> tk2 = Token('false', TokenType.FLS)
            >>> parser = Parser([tk0, tk1, tk2])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            True

            >>> tk0 = Token('true', TokenType.TRU)
            >>> tk1 = Token('and', TokenType.AND)
            >>> tk2 = Token('false', TokenType.FLS)
            >>> parser = Parser([tk0, tk1, tk2])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            False

            >>> tk0 = Token('let', TokenType.LET)
            >>> tk1 = Token('v', TokenType.VAR)
            >>> tk2 = Token('<-', TokenType.ASN)
            >>> tk3 = Token('42', TokenType.NUM)
            >>> tk4 = Token('in', TokenType.INX)
            >>> tk5 = Token('v', TokenType.VAR)
            >>> tk6 = Token('end', TokenType.END)
            >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, {})
            42

            >>> tk0 = Token('let', TokenType.LET)
            >>> tk1 = Token('v', TokenType.VAR)
            >>> tk2 = Token('<-', TokenType.ASN)
            >>> tk3 = Token('21', TokenType.NUM)
            >>> tk4 = Token('in', TokenType.INX)
            >>> tk5 = Token('v', TokenType.VAR)
            >>> tk6 = Token('+', TokenType.ADD)
            >>> tk7 = Token('v', TokenType.VAR)
            >>> tk8 = Token('end', TokenType.END)
            >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7, tk8])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, {})
            42

            >>> tk0 = Token('if', TokenType.IFX)
            >>> tk1 = Token('2', TokenType.NUM)
            >>> tk2 = Token('<', TokenType.LTH)
            >>> tk3 = Token('3', TokenType.NUM)
            >>> tk4 = Token('then', TokenType.THN)
            >>> tk5 = Token('1', TokenType.NUM)
            >>> tk6 = Token('else', TokenType.ELS)
            >>> tk7 = Token('2', TokenType.NUM)
            >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            1

            >>> tk0 = Token('if', TokenType.IFX)
            >>> tk1 = Token('false', TokenType.FLS)
            >>> tk2 = Token('then', TokenType.THN)
            >>> tk3 = Token('1', TokenType.NUM)
            >>> tk4 = Token('else', TokenType.ELS)
            >>> tk5 = Token('2', TokenType.NUM)
            >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, None)
            2

            >>> tk0 = Token('fn', TokenType.FNX)
            >>> tk1 = Token('v', TokenType.VAR)
            >>> tk2 = Token('=>', TokenType.ARW)
            >>> tk3 = Token('v', TokenType.VAR)
            >>> tk4 = Token('+', TokenType.ADD)
            >>> tk5 = Token('1', TokenType.NUM)
            >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> print(exp.accept(ev, None))
            Fn(v)

            >>> tk0 = Token('(', TokenType.LPR)
            >>> tk1 = Token('fn', TokenType.FNX)
            >>> tk2 = Token('v', TokenType.VAR)
            >>> tk3 = Token('=>', TokenType.ARW)
            >>> tk4 = Token('v', TokenType.VAR)
            >>> tk5 = Token('+', TokenType.ADD)
            >>> tk6 = Token('1', TokenType.NUM)
            >>> tk7 = Token(')', TokenType.RPR)
            >>> tk8 = Token('2', TokenType.NUM)
            >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7, tk8])
            >>> exp = parser.parse()
            >>> ev = EvalVisitor()
            >>> exp.accept(ev, {})
            3
        """
        return self.parse_exp()
        
    
    def advance(self):
        self.cur_token_idx += 1
    
    def expect(self, token_type):
        token = self.current_token()
        if not token or token.kind != token_type:
            raise SyntaxError("Type error")
        self.advance()
    
    def parse_exp(self):
        token = self.current_token()
        if token.kind == TokenType.FNX:
            return self.parse_fn()
        return self.parse_if_then_else()

    def parse_fn(self):
        self.expect(TokenType.FNX)
        var = self.current_token().text
        self.expect(TokenType.VAR)
        self.expect(TokenType.ARW)
        expr = self.parse_exp()
        return Fn(var, expr)

    
    def parse_if_then_else(self):
        token = self.current_token()
        if token.kind == TokenType.IFX:
            self.expect(TokenType.IFX)
            cond = self.parse_exp()
            self.expect(TokenType.THN)
            then_expr = self.parse_exp()
            self.expect(TokenType.ELS)
            else_expr = self.parse_exp()
            return IfThenElse(cond, then_expr, else_expr)
        return self.parse_or()

    
    def parse_or(self):
        left_expr = self.parse_and()
        while self.current_token() and self.current_token().kind == TokenType.ORX:
            self.advance()
            right_expr = self.parse_and()
            left_expr = Or(left_expr, right_expr)
        return left_expr

    def parse_and(self):
        left_expr = self.parse_less_equal_grater_exp()
        while self.current_token() and self.current_token().kind == TokenType.AND:
            self.advance()
            right_expr = self.parse_less_equal_grater_exp()
            left_expr = And(left_expr, right_expr)
        return left_expr

    def parse_less_equal_grater_exp(self):
        left_expr = self.parse_add_sub()
        while self.current_token() and self.current_token().kind in (TokenType.EQL, TokenType.LEQ, TokenType.LTH):
            op = self.current_token()
            self.advance()
            right_expr = self.parse_add_sub()
            if op.kind == TokenType.EQL:
                left_expr = Eql(left_expr, right_expr)
            elif op.kind == TokenType.LEQ:
                left_expr = Leq(left_expr, right_expr)
            elif op.kind == TokenType.LTH:
                left_expr = Lth(left_expr, right_expr)
        return left_expr

    def parse_add_sub(self):
        return self.parse_binary(self.parse_mul_div, (TokenType.ADD, TokenType.SUB),{
            TokenType.ADD: Add,
            TokenType.SUB: Sub
        })

    def parse_mul_div(self):
        return self.parse_binary(self.parse_unary, (TokenType.MUL, TokenType.DIV),{
            TokenType.MUL: Mul,
            TokenType.DIV: Div
        })

    def parse_unary(self):
        token = self.current_token()
        
        if token.kind == TokenType.NOT:
            return self.parse_not(Not)
        
        if token.kind == TokenType.NEG:
            return self.parse_neg(Neg)
        return self.parse_let()
    
    def parse_let(self):
        token = self.current_token()
        if token.kind == TokenType.LET:
            self.expect(TokenType.LET)
            var = self.current_token().text

            self.expect(TokenType.VAR)
            self.expect(TokenType.ASN)

            expr1 = self.parse_exp()
            self.expect(TokenType.INX)
            expr2 = self.parse_exp()
            self.expect(TokenType.END)

            return Let(var, expr1, expr2)
        return self.parse_value()

    def parse_value(self, ops=(TokenType.VAR, TokenType.LPR, TokenType.NUM, TokenType.TRU, TokenType.FLS)):
        exp = self.parse_value_token()
        while self.current_token() and self.current_token().kind in ops:
            exp = App(exp, self.parse_value_token())
        return exp
    
    def parse_value_token(self):
        token = self.current_token()
        if token.kind == TokenType.VAR:
            self.advance()
            return Var(token.text)
        if token.kind == TokenType.LPR:
            self.advance()
            exp = self.parse_exp()
            self.expect(TokenType.RPR)
            return exp
        if token.kind == TokenType.NUM:
            self.advance()
            return Num(int(token.text))
        if token.kind in (TokenType.FLS, TokenType.TRU):
            self.advance()
            return Bln(token.kind == TokenType.TRU)
        raise SyntaxError("Parse error")

    def parse_not(self,operator):
        self.advance()
        return operator(self.parse_unary())

    def parse_neg(self,operator):
        self.advance()
        return operator(self.parse_unary())

    def parse_binary(self, parser, ops, op_cls):
        left_expr = parser()
        while self.current_token() and self.current_token().kind in ops:
            op = self.current_token()
            self.advance()
            if self.current_token() is None:
                raise SyntaxError("Parse error")
            right_expr = parser()
            left_expr = op_cls[op.kind](left_expr, right_expr)
        return left_expr
