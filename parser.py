"""
expression  -> logical_or
logical_or  -> logical_and ("or" logical_or)*
logical_and -> primary ("and" logical_and)*
primary     -> RULE | "(" expression ")"
"""

from pprint import pprint
from enum import Enum






def foo():
    return True

def bar():
    return False

def baz():
    return True

def true():
    return True

def false():
    return False



def requires_login():
    return True

def requires_no_base_credentials():
    return True

def requires_subscription():
    return False


rules = {
    "foo": foo,
    "bar": bar,
    "baz": baz,
    "true": true,
    "false": false,
    "requires_login": requires_login,
    "requires_no_base_credentials": requires_no_base_credentials,
    "requires_subscription": requires_subscription
}











TokenType = Enum("TokenType", [
    "OR",
    "AND",
    "LEFT_PAREN",
    "RIGHT_PAREN",
    "RULE"
])

tokensMap = {
    "or": TokenType.OR,
    "and": TokenType.AND,
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN
}

class Token:
    def __init__(self, lexeme, column):
        self.type = tokensMap.get(lexeme, TokenType.RULE)
        self.literal = lexeme if self.type == TokenType.RULE else None
        self.column = column


class Scanner:
    def __init__(self, source):
        self.source = source

    def scan(self):
        lexeme = ''
        tokens = []

        for i, char in enumerate(self.source):
            isAtEnd = i >= len(self.source) - 1

            if char in { "(", ")" }:
                if lexeme:
                    tokens.append(Token(lexeme, i - len(lexeme)))
                    lexeme = ''

                tokens.append(Token(char, i))
                continue

            if lexeme and (char.isspace() or isAtEnd):

                if isAtEnd and not char.isspace():
                    lexeme += char
                    i += 1

                tokens.append(Token(lexeme, i - len(lexeme)))
                lexeme = ''
                continue

            if char.isspace():
                continue

            lexeme += char

        return tokens



def printError(token, message):
    print(message)


class ParseError(Exception):
    pass


class Expr:
    def __init__(self, type):
        self.type = type


class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def interpret(self):
        if self.operator.type == TokenType.AND:
            return self.left.interpret() and self.right.interpret()
        else:
            return self.left.interpret() or self.right.interpret()
        

class Literal(Expr):
    def __init__(self, literal):
        self.literal = literal

    def interpret(self):
        rule = self.lookup()
        return rule()

    def lookup(self):
        return rules.get(self.literal.literal)


class Grouping(Expr):
    def __init__(self, expression):
        self.expression = expression

    def interpret(self):
        return self.expression.interpret()


class Parser:
    def __init__(self, tokens):
        self.current = 0
        self.tokens = tokens

    def parse(self):
        try:
            result = self.expression()
            return (True, result)
        except ParseError:
            curr = self.previous() if self.isAtEnd() else self.peek()
            return (False, curr)

    def expression(self):
        return self.logical_or()

    def logical_or(self):
        expr = self.logical_and()

        while self.match([TokenType.OR]):
            operator = self.tokens[self.current - 1]
            right = self.logical_and()
            expr = Binary(expr, operator, right)

        return expr

    def logical_and(self):
        expr = self.primary()

        while self.match([TokenType.AND]):
            operator = self.tokens[self.current - 1]
            right = self.primary()
            expr = Binary(expr, operator, right)

        return expr

    def primary(self):
        if self.match([TokenType.RULE]):
            return Literal(self.tokens[self.current - 1])

        if self.match([TokenType.LEFT_PAREN]):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return Grouping(expr)
        
        raise self.error(self.peek(), "Expected an expression")

    def consume(self, type, message):
        if self.check(type):
            return self.advance()

        curr = self.previous() if self.isAtEnd() else self.peek()
        raise self.error(curr, message)

    def error(self, token, message):
        printError(token, message)
        return ParseError()

    def advance(self):
        if self.current >= len(self.tokens):
            return None

        token = self.tokens[self.current]
        self.current += 1
        return token

    def match(self, types):
        for type in types:
            if self.check(type):
                self.advance()
                return True

        return False

    def check(self, type):
        if self.isAtEnd():
            return False

        return self.peek().type == type

    def previous(self):
        return self.tokens[self.current - 1]

    def peek(self):
        return self.tokens[self.current]
    
    def isAtEnd(self):
        return self.current >= len(self.tokens)


if __name__ == "__main__":
    script = """false or (true and true)"""
    scanner = Scanner(script)
    tokens = scanner.scan()
    parser = Parser(tokens)
    isSuccessful, parsed = parser.parse()

    if isSuccessful:
        result = parsed.interpret()
        print(result)
    else:
        print('`' + script + '`')
        print(' ' * (parsed.column + 1) + '^')
