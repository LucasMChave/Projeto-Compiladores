# Analisador Lexico:
class Token:
    def __init__(termo, tipo, valor):
        termo.tipo = tipo
        termo.valor = valor

    def __repr__(termo):
        return f"Token({termo.tipo}, {repr(termo.valor)})"

class Lexer:
    def __init__(termo, codigo):
        termo.codigo = codigo
        termo.posicao = 0
        termo.caractere_atual = codigo[termo.posicao] if codigo else None

    def avancar(termo):
        termo.posicao += 1
        if termo.posicao < len(termo.codigo):
            termo.caractere_atual = termo.codigo[termo.posicao]
        else:
            termo.caractere_atual = None

    def ignorar_espacos(termo):
        while termo.caractere_atual and termo.caractere_atual.isspace():
            termo.avancar()

    def ignorar_comentarios(termo):
        if termo.caractere_atual == '/':
            termo.avancar()
            if termo.caractere_atual == '/':
                while termo.caractere_atual and termo.caractere_atual != '\n':
                    termo.avancar()
            elif termo.caractere_atual == '*':
                termo.avancar()
                while termo.caractere_atual and not (
                    termo.caractere_atual == '*' and termo.codigo[termo.posicao + 1] == '/'
                ):
                    termo.avancar()
                termo.avancar()
                termo.avancar()


    def proximo_token(termo):
        termo.ignorar_espacos()
        termo.ignorar_comentarios()

        if not termo.caractere_atual:
            return Token("EOF", None)

        if termo.caractere_atual.isalpha():
            inicio = termo.posicao
            while termo.caractere_atual and (termo.caractere_atual.isalnum() or termo.caractere_atual == '_'):
                termo.avancar()
            palavra = termo.codigo[inicio:termo.posicao]
            palavras_chave = {
                "if": "s_IF",
                "else": "s_ELSE",
                "while": "s_WHILE",
                "for": "s_FOR",
                "switch": "s_SWITCH",
                "break": "s_BREAK",
                "continue": "s_CONTINUE",
                "return": "s_RETURN"
            }
            if palavra in palavras_chave:
                return Token(palavras_chave[palavra], palavra)
            if palavra in {"int", "float", "double", "char", "boolean", "void"}:
                return Token("TIPO", palavra)
            return Token("ID", palavra)

        if termo.caractere_atual.isdigit():
            inicio = termo.posicao
            while termo.caractere_atual and termo.caractere_atual.isdigit():
                termo.avancar()
            if termo.caractere_atual == '.':
                termo.avancar()
                while termo.caractere_atual and termo.caractere_atual.isdigit():
                    termo.avancar()
                return Token("NUM_DEC", termo.codigo[inicio:termo.posicao])
            return Token("NUM_INT", termo.codigo[inicio:termo.posicao])

        simbolos = {
            ';': "SEMICOLON",
            '=': "EQUALS",
            '+': "PLUS",
            '-': "MINUS",
            '*': "MULTIPLY",
            '/': "DIVIDE",
            '{': "LBRACE",
            '}': "RBRACE",
            '(': "LPAREN",
            ')': "RPAREN",
            ',': "COMMA",
            '[': "LBRACKET",
            ']': "RBRACKET",
            '>': "GT",
            '>=': "GTEq",
            '<': "LT",
            '<=': "LTEq",
            '==': "isEQ",
            '!=': "NEQ",
            '!': "NOT",
            '&&': "AND",
            '||': "OR"
        }

        if termo.caractere_atual in simbolos:
            # Verificar operadores compostos primeiro
            dois_caracteres = termo.codigo[termo.posicao:termo.posicao+2]
            if dois_caracteres in simbolos:
                termo.avancar()
                termo.avancar()
                return Token(simbolos[dois_caracteres], dois_caracteres)

            # Operadores de um único caractere
            token = Token(simbolos[termo.caractere_atual], termo.caractere_atual)
            termo.avancar()
            return token

        raise ValueError(f"Caractere inesperado: {termo.caractere_atual}")

    def gerar_tokens(termo):
        tokens = []
        while True:
            token = termo.proximo_token()
            tokens.append(token)
            if token.tipo == "EOF":
                break
        return tokens

# Parser para analise sintatica
class Parser:
    def __init__(termo, tokens):
        termo.tokens = tokens
        termo.posicao = 0
        termo.token_atual = tokens[termo.posicao]

    def avancar(termo):
        termo.posicao += 1
        if termo.posicao < len(termo.tokens):
            termo.token_atual = termo.tokens[termo.posicao]
        else:
            termo.token_atual = Token("EOF", None)

    def consumir(termo, tipo):
        if termo.token_atual.tipo == tipo:
            termo.avancar()
        else:
            raise ValueError(f"Token inesperado: {termo.token_atual}, esperado {tipo}")

    # Regras gramaticais

    def expressao_condicional(termo):
        if termo.token_atual.tipo == "s_IF":
            termo.consumir("s_IF")
            termo.consumir("LPAREN")
            condicao = termo.expressao()
            termo.consumir("RPAREN")
            corpo_if = termo.bloco()
            corpo_else = None
            if termo.token_atual.tipo == "s_ELSE":
                termo.consumir("s_ELSE")
                corpo_else = termo.bloco()
            return Condicional(condicao, corpo_if, corpo_else)
        else:
            raise ValueError(f"Esperado 'if', mas encontrado {termo.token_atual}")

    def laço_while(termo):
        if termo.token_atual.tipo == "s_WHILE":
            termo.consumir("s_WHILE")
            termo.consumir("LPAREN")
            condicao = termo.expressao()
            termo.consumir("RPAREN")
            corpo = termo.bloco()
            return WhileLoop(condicao, corpo)
        else:
            raise ValueError(f"Esperado 'while', mas encontrado {termo.token_atual}")

    def expressao_comando(termo):
        if termo.token_atual.tipo == "s_RETURN":
            termo.consumir("s_RETURN")
            valor = termo.expressao()
            termo.consumir("SEMICOLON")
            return Return(valor)
        elif termo.token_atual.tipo == "s_BREAK":
            termo.consumir("s_BREAK")
            termo.consumir("SEMICOLON")
            return Break()
        elif termo.token_atual.tipo == "s_CONTINUE":
            termo.consumir("s_CONTINUE")
            termo.consumir("SEMICOLON")
            return Continue()
        else:
            return termo.expressao()

    def programa(termo):
        nos = []
        while termo.token_atual.tipo != "EOF":
            if termo.token_atual.tipo == "TIPO":
                nos.append(termo.declaracao_variavel())
            elif termo.token_atual.tipo == "s_IF":
                nos.append(termo.expressao_condicional())
            elif termo.token_atual.tipo == "s_WHILE":
                nos.append(termo.laço_while())
            elif termo.token_atual.tipo == "ID":
                nos.append(termo.declaracao_atribuicao())
            elif termo.token_atual.tipo in {"s_RETURN", "s_BREAK", "s_CONTINUE"}:
                nos.append(termo.expressao_comando())
            else:
                raise ValueError(f"Declaração inválida: {termo.token_atual}")
        return nos

    def declaracao(termo):
        if termo.token_atual.tipo == "TIPO":
            if termo.tokens[termo.posicao + 1].tipo == "ID" and termo.tokens[termo.posicao + 2].tipo == "LPAREN":
                return termo.declaracao_funcao()
            else:
                return termo.declaracao_variavel()
        elif termo.token_atual.tipo == "ID":
            if termo.tokens[termo.posicao + 1].tipo == "EQUALS":
                return termo.declaracao_atribuicao()
            else:
                raise ValueError(f"Declaração inválida: {termo.token_atual}")
        else:
            raise ValueError(f"Declaração inválida: {termo.token_atual}")


    def declaracao_variavel(termo):
        tipo = termo.token_atual.valor
        termo.consumir("TIPO")
        nome = termo.token_atual.valor
        termo.consumir("ID")
        valor = None
        if termo.token_atual.tipo == "EQUALS":
            termo.consumir("EQUALS")
            valor = termo.expressao()
        termo.consumir("SEMICOLON")
        return DeclaracaoVariavel(tipo, nome, valor)

    def declaracao_atribuicao(termo):
        nome = termo.token_atual.valor
        termo.consumir("ID")
        termo.consumir("EQUALS")
        expressao = termo.expressao()
        termo.consumir("SEMICOLON")
        return Atribuicao(nome, expressao)

    def declaracao_funcao(termo):
        tipo = termo.token_atual.valor
        termo.consumir("TIPO")
        nome = termo.token_atual.valor
        termo.consumir("ID")
        termo.consumir("LPAREN")
        
        parametros = []
        if termo.token_atual.tipo != "RPAREN":
            parametros.append(termo.parametro())
            while termo.token_atual.tipo == "COMMA":
                termo.consumir("COMMA")
                parametros.append(termo.parametro())
        termo.consumir("RPAREN")
        
        corpo = termo.bloco()
        return Funcao(tipo, nome, parametros, corpo)

    def parametros(termo):
        termo.parametro()
        while termo.token_atual.tipo == "COMMA":
            termo.consumir("COMMA")
            termo.parametro()

    def parametro(termo):
        termo.consumir("TIPO")
        termo.consumir("ID")

    def bloco(termo):
        termo.consumir("LBRACE")
        declaracoes = []
        while termo.token_atual.tipo != "RBRACE":
            declaracoes.append(termo.declaracao())
        termo.consumir("RBRACE")
        return declaracoes

    
    def expressao_logica(termo):
        no = termo.comparacao()
        while termo.token_atual.tipo in {"AND", "OR"}:
            operador = termo.token_atual.valor
            termo.consumir(termo.token_atual.tipo)
            no = ExpressaoLogica(operador, no, termo.comparacao())
        return no

    def comparacao(termo):
        no = termo.expressao()
        while termo.token_atual.tipo in {"GT", "LT", "GTEq", "LTEq", "isEQ", "NEQ"}:
            operador = termo.token_atual.valor
            termo.consumir(termo.token_atual.tipo)
            no = ExpressaoComparacao(operador, no, termo.expressao())
        return no


    def expressao(termo):
        no = termo.produto()
        while termo.token_atual.tipo in {"PLUS", "MINUS"}:
            operador = termo.token_atual.valor
            termo.consumir(termo.token_atual.tipo)
            no = ExpressaoBinaria(operador, no, termo.produto())
        return no

    def produto(termo):
        no = termo.fator()
        while termo.token_atual.tipo in {"MULTIPLY", "DIVIDE"}:
            operador = termo.token_atual.valor
            termo.consumir(termo.token_atual.tipo)
            no = ExpressaoBinaria(operador, no, termo.fator())
        return no

    def fator(termo):
        if termo.token_atual.tipo == "NOT":
            operador = termo.token_atual.valor
            termo.consumir("NOT")
            no = termo.fator()  # Negação
            return ExpressaoUnaria(operador, no)
        elif termo.token_atual.tipo in {"NUM_INT", "NUM_DEC"}:
            valor = Valor(termo.token_atual.valor)
            termo.consumir(termo.token_atual.tipo)
            return valor
        elif termo.token_atual.tipo == "ID":
            valor = Valor(termo.token_atual.valor)
            termo.consumir("ID")
            return valor
        elif termo.token_atual.tipo == "LPAREN":
            termo.consumir("LPAREN")
            no = termo.expressao_logica()
            termo.consumir("RPAREN")
            return no
        else:
            raise ValueError(f"Expressão inválida: {termo.token_atual}")

# Criação dos Nós:

class NoAST:
    pass

class Condicional(NoAST):
    def __init__(termo, condicao, corpo_if, corpo_else=None):
        termo.condicao = condicao
        termo.corpo_if = corpo_if
        termo.corpo_else = corpo_else

    def __repr__(termo):
        return f"Condicional(condicao={termo.condicao}, corpo_if={termo.corpo_if}, corpo_else={termo.corpo_else})"

class WhileLoop(NoAST):
    def __init__(termo, condicao, corpo):
        termo.condicao = condicao
        termo.corpo = corpo

    def __repr__(termo):
        return f"WhileLoop(condicao={termo.condicao}, corpo={termo.corpo})"

class Return(NoAST):
    def __init__(termo, valor):
        termo.valor = valor

    def __repr__(termo):
        return f"Return(valor={termo.valor})"

class Break(NoAST):
    def __repr__(termo):
        return "Break()"

class Continue(NoAST):
    def __repr__(termo):
        return "Continue()"

class DeclaracaoVariavel(NoAST):
    def __init__(termo, tipo, nome, valor=None):
        termo.tipo = tipo
        termo.nome = nome
        termo.valor = valor

    def __repr__(termo):
        return f"DeclaracaoVariavel(tipo={termo.tipo}, nome={termo.nome}, valor={termo.valor})"

class Atribuicao(NoAST):
    def __init__(termo, nome, expressao):
        termo.nome = nome
        termo.expressao = expressao

    def __repr__(termo):
        return f"Atribuicao(nome={termo.nome}, expressao={termo.expressao})"

class ExpressaoBinaria(NoAST):
    def __init__(termo, operador, esquerda, direita):
        termo.operador = operador
        termo.esquerda = esquerda
        termo.direita = direita

    def __repr__(termo):
        return f"ExpressaoBinaria(operador={termo.operador}, esquerda={termo.esquerda}, direita={termo.direita})"

class Valor(NoAST):
    def __init__(termo, valor):
        termo.valor = valor

    def __repr__(termo):
        return f"Valor(valor={termo.valor})"

class Funcao(NoAST):
    def __init__(termo, tipo, nome, parametros, corpo):
        termo.tipo = tipo
        termo.nome = nome
        termo.parametros = parametros
        termo.corpo = corpo

    def __repr__(termo):
        return f"DeclaracaoFuncao (Tipo = {termo.tipo}, Nome = {termo.nome}, Parametros = {termo.parametros}, Corpo = {termo.corpo})"
    
class ExpressaoLogica(NoAST):
    def __init__(termo, operador, esquerda, direita):
        termo.operador = operador
        termo.esquerda = esquerda
        termo.direita = direita

    def __repr__(termo):
        return f"ExpressaoLogica(operador={termo.operador}, esquerda={termo.esquerda}, direita={termo.direita})"

class ExpressaoComparacao(NoAST):
    def __init__(termo, operador, esquerda, direita):
        termo.operador = operador
        termo.esquerda = esquerda
        termo.direita = direita

    def __repr__(termo):
        return f"ExpressaoComparacao(operador={termo.operador}, esquerda={termo.esquerda}, direita={termo.direita})"

class ExpressaoUnaria(NoAST):
    def __init__(termo, operador, operando):
        termo.operador = operador
        termo.operando = operando

    def __repr__(termo):
        return f"ExpressaoUnaria(operador={termo.operador}, operando={termo.operando})"



# Testando o analisador
codigo_fonte = """
int x = 10;
int y = 5;
int z = 2;
int W;
W = x + (y * z);
"""

lexer = Lexer(codigo_fonte)
tokens = lexer.gerar_tokens()

print("\nTokens:")
print(tokens)

parser = Parser(tokens)
ast = parser.programa()

print("\nÁrvore Sintática Abstrata:")
for no in ast:
    print(no)
