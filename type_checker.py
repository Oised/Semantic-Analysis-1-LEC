from __future__ import annotations
from dataclasses import fields
from typing import cast
from ast_nodes import (
    BinaryExpr,
    BinaryOperator,
    BoolLiteral,
    CallExpr,
    Expr,
    IdentifierExpr,
    IntLiteral,
    Node,
    Program,
    TypeName,
    UnaryExpr,
    UnaryOperator,
)
from symbols import FunctionSymbol, Symbol


def infer_type(expression: Expr) -> TypeName:
    """Inferir o tipo de uma expressão.

    Retorna TypeName.VOID se a expressão não for válida.
    """

    if isinstance(expression, IntLiteral): # Verifica se a expressão é um literal inteiro
        return TypeName.INT
    
    elif isinstance(expression, BoolLiteral): # Verifica se a expressão é um literal booleano
        return TypeName.BOOL
    
    elif isinstance(expression, IdentifierExpr): # Verifica se a expressão é um identificador
        symbol = cast(Symbol, expression.metadata["symbol"]) # Obtém o símbolo associado ao identificador
        return symbol.type # Retorna o tipo do símbolo associado ao identificador

    elif isinstance(expression, CallExpr): # Verifica se a expressão é uma chamada de função 
        function = cast(FunctionSymbol, expression.metadata["symbol"]) # Obtém o símbolo da função associada à chamada

        for arguments in expression.arguments:
            infer_type(arguments) # Inferir o tipo de cada argumento da chamada de função
        result = function.type # Retorna o tipo de retorno da função chamada

    elif isinstance(expression, UnaryExpr): # Verifica se a expressão é uma expressão unária
        infer_type(expression.operand) # Inferir o tipo do operando da expressão unária
        if expression.operator is UnaryOperator.NEGATE: # Verifica se o operador unário é de negação
            result = TypeName.INT                       # se é negação, o resultado é do tipo inteiro, senão, o resultado é do tipo booleano
        else:
            result = TypeName.BOOL

    elif isinstance(expression, BinaryExpr): # Verifica se a expressão é uma expressão binária
        infer_type(expression.left) # Infere os tipos dos operandos esquerdo e direito da expressão binária
        infer_type(expression.right)

        if expression.operator in { # Verifica se o operador binário é um operador relacional ou lógico
            BinaryOperator.LESS,
            BinaryOperator.LESS_EQUAL,
            BinaryOperator.GREATER,
            BinaryOperator.GREATER_EQUAL,
            BinaryOperator.EQUAL,
            BinaryOperator.NOT_EQUAL,
            BinaryOperator.LOGICAL_AND,
            BinaryOperator.LOGICAL_OR,
        }:
            result = TypeName.BOOL  #Caso seja um operador relacional ou lógico, o resultado é do tipo booleano, senão, o resultado é do tipo inteiro
        else:
            result = TypeName.INT

    else: # fallback para tipos de expressão não suportados
        raise TypeError(f"tipo de expressão não suportado: {type(expression).__name__}")

    expression.metadata["type"] = result
    return result

def check_types(program: Program) -> None:
    """Determine tipos de expressões e valide seus contextos."""

    def visit(value: object) -> None: # Função auxiliar para visitar os nós da AST e inferir tipos
        if isinstance(value, Expr): # Determina tipos de expressöes
           infer_type(value)
           return

        if isinstance(value, Node): # Determina tipos de nós da AST
            for field in fields(value):
                if field.name != "metadata":
                    visit(getattr(value, field.name)) # Visita de maneira recursiva os campos do nó da AST
            return

        if isinstance(value, list): # Determina tipos de listas de nós da AST
            for item in value:
                visit(item) # visita de maneira recursiva cada item da lista

    visit(program)

    # 1. Use os símbolos anexados pela resolução de nomes.
    # 2. Determine cada expressão de baixo para cima.
    # 3. Valide operadores, chamadas, comandos e declarações.
    # 4. Anote expressões válidas e acumule os diagnósticos da passagem.
    raise NotImplementedError("implemente a verificação de tipos")
