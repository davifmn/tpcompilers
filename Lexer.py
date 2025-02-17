import sys
import enum


class Token:
    """
    This class contains the definition of Tokens. A token has two fields: its
    text and its kind. The "kind" of a token is a constant that identifies it
    uniquely. See the TokenType to know the possible identifiers (if you want).
    You don't need to change this class.
    """
    def __init__(self, tokenText, tokenKind):
        # The token's actual text. Used for identifiers, strings, and numbers.
        self.text = tokenText
        # The TokenType that this token is classified as.
        self.kind = tokenKind


class TokenType(enum.Enum):
    """
    These are the possible tokens. You don't need to change this class at all.
    """
    EOF = -1  # End of file
    NLN = 0   # New line
    WSP = 1   # White Space
    COM = 2   # Comment
    NUM = 3   # Number (integers)
    STR = 4   # Strings
    TRU = 5   # The constant true
    FLS = 6   # The constant false
    VAR = 7   # An identifier
    LET = 8   # The 'let' of the let expression
    INX = 9   # The 'in' of the let expression
    END = 10  # The 'end' of the let expression
    EQL = 201 # x = y
    ADD = 202 # x + y
    SUB = 203 # x - y
    MUL = 204 # x * y
    DIV = 205 # x / y
    LEQ = 206 # x <= y
    LTH = 207 # x < y
    NEG = 208 # ~x
    NOT = 209 # not x
    LPR = 210 # (
    RPR = 211 # )
    ASN = 212 # The assignment '<-' operator
    ORX = 213 # x or y
    AND = 214 # x and y
    IFX = 215 # The 'if' of a conditional expression
    THN = 216 # The 'then' of a conditional expression
    ELS = 217 # The 'else' of a conditional expression
    FNX = 218 # The 'fn' that declares an anonymous function
    ARW = 219 # The '=>' that separates the parameter from the body of function


class Lexer:
    
    def __init__(self, source):
        """
        The constructor of the lexer. It receives the string that shall be
        scanned.
        TODO: You will need to implement this method.
        """
        self.source = source
        self.position = 0
        self.length = len(source)

        self.diff_signals = {
            '<': self.l_lt,
            '(': self.l_left_par,
            '-': self.l_minus,
            '=': self.l_equal
        }

        self.base_signals = {
            '*': Token("*", TokenType.MUL),
            '/': Token("/", TokenType.DIV),
            '~': Token("~", TokenType.NEG),
            ')': Token(")", TokenType.RPR),
            " ": Token(" ", TokenType.WSP),
            '\n': Token("\n", TokenType.NLN),
            '=': Token("=", TokenType.EQL),
            '+': Token("+", TokenType.ADD),
        }

    def tokens(self):
        """
        This method is a token generator: it converts the string encapsulated
        into this object into a sequence of Tokens. Notice that this method
        filters out three kinds of tokens: white-spaces, comments and new lines.

        Examples:

        >>> l = Lexer("1 + 3")
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.ADD: 202>, <TokenType.NUM: 3>]

        >>> l = Lexer('1 * 2\\n')
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.MUL: 204>, <TokenType.NUM: 3>]

        >>> l = Lexer('1 * 2 -- 3\\n')
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.MUL: 204>, <TokenType.NUM: 3>]

        >>> l = Lexer("1 + var")
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.ADD: 202>, <TokenType.VAR: 7>]

        >>> l = Lexer("let v <- 2 in v end")
        >>> [tk.kind.name for tk in l.tokens()]
        ['LET', 'VAR', 'ASN', 'NUM', 'INX', 'VAR', 'END']
        """
        token = self.getToken()
        while token.kind != TokenType.EOF:
            if token.kind != TokenType.WSP and token.kind != TokenType.COM and token.kind != TokenType.NLN:
                yield token
            token = self.getToken()
        
    def l_digit(self, char):
        number = char
        while self.position < self.length and self.source[self.position].isdigit():
            number += self.source[self.position]
            self.position += 1
        return Token(number, TokenType.NUM)
    
    def l_lt(self):
        if self.position < self.length:
            if self.source[self.position] == '=':
                self.position += 1
                return Token("<=", TokenType.LEQ)
            
            if self.source[self.position] == '-':
                self.position += 1
                return Token("<-", TokenType.ASN)
        
        return Token("<", TokenType.LTH)
    
    def l_minus(self):
        if self.position < self.length and self.source[self.position] == '-':
            while self.position < self.length and self.source[self.position] != '\n':
                self.position += 1
            self.position += 1
            return Token("--", TokenType.COM)
        return Token("-", TokenType.SUB)
    
    def l_left_par(self):
        if self.position < self.length and self.source[self.position] == '*':
            while self.position < self.length -1 and not (self.source[self.position] == '*' and self.source[self.position + 1] == ')'):
                self.position += 1
            self.position += 2
            return Token("(*", TokenType.COM)
        return Token("(", TokenType.LPR)

    def l_string(self, char):
        string = char
        while self.position < self.length and (self.source[self.position].isalpha() or self.source[self.position].isdigit()):
            string += self.source[self.position]
            self.position += 1

        keys = {
            "true": TokenType.TRU, 
            "false": TokenType.FLS, 
            "not": TokenType.NOT, 
            "let": TokenType.LET, 
            "in": TokenType.INX, 
            "end": TokenType.END,
            "if": TokenType.IFX,
            "then": TokenType.THN,
            "else": TokenType.ELS,
            "or": TokenType.ORX,
            "and": TokenType.AND,
            "fn": TokenType.FNX,
        }
        return Token(string, keys.get(string, TokenType.VAR))
    
    def l_equal(self):
        if self.position < self.length and self.source[self.position] == '>':
            self.position += 1
            return Token("=>", TokenType.ARW)
        return Token("=", TokenType.EQL)

    def getToken(self):
        if(self.position >= self.length):
            return Token("", TokenType.EOF)
        
        char = self.source[self.position]
        self.position += 1

        if char.isdigit():
            return self.l_digit(char)

        if char.isalpha():
            return self.l_string(char)

        if char in self.diff_signals:
            return self.diff_signals[char]()
            
        if char in self.base_signals:
            return self.base_signals[char]

        raise ValueError(f"Argh!! Invalid character: {char}")
