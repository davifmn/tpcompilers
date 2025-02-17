import sys
from Expression import *
from Visitor import *
from Lexer import Lexer
from Parser import Parser
import Asm as AsmModule
from Optimizer import *


def rename_variables(exp):
    """
    Esta funcao invoca o renomeador de variaveis. Ela deve ser usada antes do
    inicio da fase de geracao de codigo.
    """
    ren = RenameVisitor()
    exp.accept(ren, {})
    return exp


def perform_register_allocation(prog, dump=False):
    """
    Esta funcao invoca o alocador de registradores sobre o programa. Caso queira
    depurar sua alocacao, fique a vontade para usar dump == True.
    """
    o = RegAllocator(prog)
    if dump:
        print("Before RA: ---------------")
        prog.print_insts()
    o.optimize()
    if dump:
        print("After RA: ---------------")
        prog.print_insts()
    return o


if __name__ == "__main__":
    """
    Este arquivo nao deve ser alterado, mas deve ser enviado para resolver o
    VPL. O arquivo contem o codigo que testa a implementacao do parser.
    """
    text = sys.stdin.read()
    lexer = Lexer(text)
    parser = Parser(lexer.tokens())
    exp = rename_variables(parser.parse())
    prog = AsmModule.Program(1000, {}, [])
    gen = GenVisitor()
    var_answer = exp.accept(gen, prog)
    opt = perform_register_allocation(prog, False)
    prog.reset_env()
    prog.eval()
    print(f"Answer: {opt.get_val(var_answer)}")