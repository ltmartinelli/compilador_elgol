import re
import ply.lex as lex


# 1) PALAVRAS RESERVADAS 

reserved = {
    'elgio':      'ELGIO',

    'DECIMAL':    'DECIMAL',
    '_Z_':        'Z',           
    '_NEG_':      'NEG',         
    'EXP':        'EXP',         
    'RESTO':      'RESTO',       

    'enquanto':   'ENQUANTO',
    'se':         'SE',
    'entao':      'ENTAO',
    'senao':      'SENAO',
    'para':       'PARA',

    'inicio':     'INICIO',
    'fim':        'FIM',

    'maior':      'MAIOR',
    'menor':      'MENOR',
    'igual':      'IGUAL',
    'diferente':  'DIFERENTE',
    'migual':     'MENOR_IGUAL',
    'MIgual':     'MAIOR_IGUAL',

    'x':          'MULT',        # operador de multiplicacao (letra x)
}


# 2) LISTA DE TOKENS

tokens = [
    'ID',        # identificador
    'FUNCID',    # função
    'NUMBER',    # numero inteiro positivo

    'ASSIGN',    # =   (tambem usado como atribuicao)
    'PLUS',      # +
    'MINUS',     # -
    'DIV',       # /
    'LPAREN',    # (
    'RPAREN',    # )
    'COMMA',     # ,
    'PONTO',     # .   (termina comando)
] +  sorted(set(reserved.values()))


# 3) REGRAS DE VALIDACAO AUXILIARES
_ID_REGEX = re.compile(r'^[BCDFGHJKLMNPQRSTVWXYZ][A-Za-z]{2,}[a-z]$')


def _identificador_valido(texto):
    return bool(_ID_REGEX.match(texto))


# 4) TOKENS SIMPLES (regex direta, sem logica extra)

t_ASSIGN = r'='
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_DIV    = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA  = r','
t_PONTO  = r'\.'

# Espacos e tabs sao ignorados entre tokens
t_ignore = ' \t'


# 5) TOKENS COM LOGICA 

def t_COMENTARIO(t):
    r'\*.*'
    pass


def t_NUMBER(t):
    r'[1-9][0-9]*'
    t.value = int(t.value)
    return t


def t_FUNCID(t):
    r'\$[A-Za-z_][A-Za-z0-9_]*'
    corpo = t.value[1:]  # remove o "$"
    if _identificador_valido(corpo):
        return t
    print(f"Erro lexico: nome de funcao invalido '{t.value}' "
          f"na linha {t.lineno}")


def t_WORD(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    # 1) palavra reservada?
    if t.value in reserved:
        t.type = reserved[t.value]
        return t
    # 2) identificador valido?
    if _identificador_valido(t.value):
        t.type = 'ID'
        return t
    # 3) nao e nem reservada nem identificador valido -> erro lexico
    print(f"Erro lexico: identificador invalido '{t.value}' "
          f"na linha {t.lineno}")


# 6) CONTROLE DE LINHA

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# 7) TRATAMENTO DE ERROS LEXICOS 
def t_error(t):
    print(f"Erro lexico: caractere ilegal '{t.value[0]}' "
          f"na linha {t.lineno}")
    t.lexer.skip(1)


# 8) CONSTRUCAO DO LEXER
lexer = lex.lex()

# 9) TABELA DE SIMBOLOS

def construir_tabela_simbolos(tokens_lidos):
    """
    Retorna uma lista de dicts {id, tipo, valor}, sem duplicidade.
    Dois simbolos sao iguais se tiverem o mesmo tipo E o mesmo valor.
    O id segue a ordem da primeira aparicao no codigo.
    """
    tabela = {}  
    for tok in tokens_lidos:
        chave = (tok.type, tok.value)
        if chave not in tabela:
            tabela[chave] = len(tabela) + 1

    return [
        {'id': i, 'tipo': tipo, 'valor': valor}
        for (tipo, valor), i in tabela.items()
    ]


def imprimir_tabela_simbolos(tabela):
    print("TABELA DE SIMBOLOS")
    print(f"{'ID':<5} {'TIPO':<14} VALOR")
    print("-" * 40)
    for s in tabela:
        print(f"{s['id']:<5} {s['tipo']:<14} {s['valor']}")
    print()


# 10) LEITURA DO ARQUIVO PELA LINHA DE COMANDO

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Uso: python elgio_lexer.py <arquivo>")
        sys.exit(1)

    nome_arquivo = sys.argv[1]

    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            codigo = arquivo.read()
    except FileNotFoundError:
        print(f"Erro: arquivo '{nome_arquivo}' não encontrado.")
        sys.exit(1)
    except OSError as erro:
        print(f"Erro ao abrir o arquivo: {erro}")
        sys.exit(1)

    lexer.input(codigo)

    tokens_lidos = list(lexer)

    # 1) tabela de simbolos
    tabela = construir_tabela_simbolos(tokens_lidos)
    imprimir_tabela_simbolos(tabela)

    # 2) lista de tokens
    print("TOKENS")
    for tok in tokens_lidos:
        print(tok)