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
        while termo.caractere_atual == '/':
            termo.avancar()
            if termo.caractere_atual == '/':
                # Comentário de linha
                while termo.caractere_atual != '\n' and termo.caractere_atual:
                    termo.avancar()
            elif termo.caractere_atual == '*':
                # Comentário de bloco
                termo.avancar()
                while termo.caractere_atual != '*' and termo.caractere_atual != '/':
                    termo.avancar()
                if termo.caractere_atual == '*':
                    termo.avancar()
                    if termo.caractere_atual == '/':
                        termo.avancar()
                        return
            else:
                break

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
        }

        if termo.caractere_atual in simbolos:
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
    def programa(termo):
        nos = []
        while termo.token_atual.tipo != "EOF":
            if termo.token_atual.tipo == "TIPO":
                nos.append(termo.declaracao_variavel())
            elif termo.token_atual.tipo == "ID":
                if termo.tokens[termo.posicao + 1].tipo == "EQUALS":
                    nos.append(termo.declaracao_atribuicao())
                else:
                    raise ValueError(f"Declaração inválida: {termo.token_atual}")
            else:
                raise ValueError(f"Declaração inválida: {termo.token_atual}")
        return nos

    def declaracao(termo):
        if termo.token_atual.tipo == "TIPO":
            termo.declaracao_variavel()
        elif termo.token_atual.tipo == "ID":
            if termo.tokens[termo.posicao + 1].tipo == "LPAREN":
                termo.declaracao_funcao()
            elif termo.tokens[termo.posicao + 1].tipo == "EQUALS":
                termo.declaracao_atribuicao()
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
        while termo.token_atual.tipo != "RBRACE":
            termo.declaracao()
        termo.consumir("RBRACE")
    
    def expressao(termo):
        no = termo.termo()
        while termo.token_atual.tipo in {"PLUS", "MINUS"}:
            operador = termo.token_atual.valor
            termo.consumir(termo.token_atual.tipo)
            no = ExpressaoBinaria(operador, no, termo.termo())
        return no

    def produto(termo):
        no = termo.fator()
        while termo.token_atual.tipo in {"MULTIPLY", "DIVIDE"}:
            operador = termo.token_atual.valor
            termo.consumir(termo.token_atual.tipo)
            no = ExpressaoBinaria(operador, no, termo.fator())
        return no

    def fator(termo):
        if termo.token_atual.tipo in {"NUM_INT", "NUM_DEC"}:
            valor = Valor(termo.token_atual.valor)
            termo.consumir(termo.token_atual.tipo)
            return valor
        elif termo.token_atual.tipo == "ID":
            valor = Valor(termo.token_atual.valor)
            termo.consumir("ID")
            return valor
        elif termo.token_atual.tipo == "LPAREN":
            termo.consumir("LPAREN")
            no = termo.expressao()
            termo.consumir("RPAREN")
            return no
        else:
            raise ValueError(f"Expressão inválida: {termo.token_atual}")



class NoAST:
    pass


# Criação dos Nós:

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



# Testando o analisador
codigo_fonte = """
int x = 10;
int y = 5;
int z = 2;
x = x + (y * z);
"""

lexer = Lexer(codigo_fonte)
tokens = lexer.gerar_tokens()

print("Tokens:")
for token in tokens:
    print(token)

parser = Parser(tokens)
ast = parser.programa()
print("Árvore Sintática Abstrata:")
for no in ast:
    print(no)
