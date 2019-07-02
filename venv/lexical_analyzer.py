import re


class LexicalParser:
    def __init__(self):
        self.input = ''
        self.index = 0
        self.number_of_line = 1
        self.all_token = []
        self.INDEX_OF_CATEGORY = 0
        self.INDEX_OF_TOKEN = 1
        self.INDEX_OF_NUMBER_OF_LINE = 2
        self.all_error = []
        self.open_file()
        self.KEYWORD = ["if",
                        "else",
                        "void",
                        "int",
                        "while",
                        "break",
                        "continue",
                        "switch",
                        "default",
                        "case",
                        "return"]

        self.SYMBOL = [',',
                       ':',
                       ';',
                       '{',
                       '}',
                       '(',
                       ')',
                       '[',
                       ']',
                       '+',
                       '-',
                       '*',
                       '<',
                       '=',
                       '==']

        self.WHITESPACE = [chr(32),
                           chr(10),
                           chr(11),
                           chr(12),
                           chr(13),
                           chr(9)]

    def open_file(self, input_file='inp.txt'):
        self.input = open(input_file, "r").read()
        print(self.input)

    def get_next_token(self):
        token = self.get_next_token_in()
        # if token[] == 'ERROR':
        #     print()
        while token[1] == 'ERROR':
            if token[0] == '$':
                break
            token = self.get_next_token_in()
        return token

    def get_next_token_in(self):
        aux = ""
        if self.index >= len(self.input):
            return 0, 0, 0, self.number_of_line
        while self.basic_check() and (
                (self.check_current_char() in self.WHITESPACE) or (self.check_current_char() == '/')):
            aux += self.read_current_char()
            if aux == '/':
                if self.check_current_char() == '/':
                    while self.basic_check() and self.check_current_char() != '\n':
                        aux += self.read_current_char()
                    aux = ''
                    if not self.basic_check():
                        return 0, 0, 0, self.number_of_line
                    self.read_current_char()

                elif self.check_current_char() == '*':
                    while self.basic_check() and \
                            (not (self.basic_check() and (aux[len(aux) - 1] == '*') and (
                                    self.check_current_char() == '/'))):
                        aux += self.read_current_char()
                    aux = ''
                    if not self.basic_check():
                        return 0, 0, 0, self.number_of_line
                    self.read_current_char()
                else:
                    return self.set_error(aux)
            else:
                while self.basic_check() and self.check_current_char() in self.WHITESPACE:
                    self.read_current_char()
                aux = ''

        if re.match("^[0-9]+$", self.check_current_char()):
            while self.basic_check() and (re.match("^[0-9]+$", self.check_current_char())):
                aux += self.read_current_char()
        elif re.match("^[A-Za-z]*$", self.check_current_char()):
            aux += self.read_current_char()
            while self.basic_check() and (re.match("^[A-Za-z0-9]+$", self.check_current_char())):
                aux += self.read_current_char()
                # print(aux)
        elif self.check_current_char() in self.SYMBOL:
            if self.check_current_char() != '=':
                aux += self.read_current_char()
                return aux, self.set_token_category(aux), self.index, self.number_of_line
            else:
                aux += self.read_current_char()
                if self.check_current_char() == '=':
                    aux += self.read_current_char()
                    return aux, self.set_token_category(aux), self.index, self.number_of_line
                elif self.is_invalid_char(self.check_current_char()):
                    return self.set_error(aux), self.number_of_line
                else:
                    return aux, self.set_token_category(aux), self.index, self.number_of_line

        if self.basic_check() and self.is_invalid_char(self.check_current_char()):
            return self.set_error(aux)
        else:
            return aux, self.set_token_category(aux), self.index, self.number_of_line

    def set_error(self, aux):
        aux += self.read_current_char()
        return aux, 'ERROR', self.index, self.number_of_line

    def current_char_is_starter_for_parse(self, char):
        return (char in self.SYMBOL) or (re.match("^[A-Za-z0-9]*$", char))

    def basic_check(self):
        return self.index < len(self.input)

    def read_current_char(self):
        self.index += 1
        if self.input[self.index - 1] == '\n':
            self.number_of_line += 1
        return self.input[self.index - 1]

    def check_current_char(self):
        if not self.basic_check():
            return
        return self.input[self.index]

    def is_invalid_char(self, char):
        # print('**' + char + '**')
        return not ((char in self.SYMBOL) or (re.match("^[A-Za-z0-9]*$", char)) or (char in self.WHITESPACE) or (
                    char is '/'))

    def set_token_category(self, token):

        category = None
        if re.match("^[0-9]+$", token):
            category = "NUM"

        elif token in self.KEYWORD:
            category = "KEYWORD"

        elif token in self.SYMBOL:
            category = "SYMBOL"

        elif token == "//":
            category = "cmt//"

        elif token == "/*":
            category = "cmt/*"

        elif token in self.WHITESPACE:
            category = "WHITESPACE"

        elif re.match("^[A-Za-z][A-Za-z0-9]*$", token):
            category = "ID"

        return category

    def process(self):
        # print(self.input)
        self.index = 0
        while True:
            token, token_category, self.index, number_if_line = self.get_next_token_in()
            if token == token_category == self.index == 0:
                break
            if token_category != 'ERROR':
                self.all_token.append([token_category, token, number_if_line])
            else:
                if token != '$':
                    self.all_error.append(['invalid input', token, number_if_line])
            # print(token, token_category, self.index)
        self.index = 0
        self.number_of_line = 1

    def reset_index(self):
        self.index = 0

    def show_tokens(self):
        counter = 0
        for i in range(self.number_of_line):
            j = i + 1
            if counter < len(self.all_token) and j == self.all_token[counter][self.INDEX_OF_NUMBER_OF_LINE]:
                print(str(j) + '. ', end='')
                while counter < len(self.all_token) and j == self.all_token[counter][self.INDEX_OF_NUMBER_OF_LINE]:
                    print('(' + str(self.all_token[counter][self.INDEX_OF_CATEGORY]) + ', ' +
                          str(self.all_token[counter][self.INDEX_OF_TOKEN]) + ')', end='')
                    counter += 1
                print()

    def show_error(self):
        counter = 0
        # print(self.all_error)
        for i in range(self.number_of_line):
            j = i + 1
            if counter < len(self.all_error) and j == self.all_error[counter][self.INDEX_OF_NUMBER_OF_LINE]:
                print(str(j) + '. ', end='')
                while counter < len(self.all_error) and j == self.all_error[counter][self.INDEX_OF_NUMBER_OF_LINE]:
                    print('(' + str(self.all_error[counter][self.INDEX_OF_TOKEN]) + ', ' +
                          str(self.all_error[counter][self.INDEX_OF_CATEGORY]) + ')', end='')
                    counter += 1
                print()

    def export_token(self):
        counter = 0
        output = ''
        for i in range(self.number_of_line):
            j = i + 1
            if counter < len(self.all_token) and j == self.all_token[counter][self.INDEX_OF_NUMBER_OF_LINE]:
                output += str(j) + '. '
                while counter < len(self.all_token) and j == self.all_token[counter][self.INDEX_OF_NUMBER_OF_LINE]:
                    output += '(' + str(self.all_token[counter][self.INDEX_OF_CATEGORY]) + ', ' + \
                              str(self.all_token[counter][self.INDEX_OF_TOKEN]) + ')'
                    counter += 1
                output += '\n'
        writer = open('scanner.txt', 'w')
        writer.write(output)

    def export_error(self):
        counter = 0
        output = ''
        for i in range(self.number_of_line):
            j = i + 1
            if counter < len(self.all_error) and j == self.all_error[counter][self.INDEX_OF_NUMBER_OF_LINE]:
                output += str(j) + '. '
                while counter < len(self.all_error) and j == self.all_error[counter][self.INDEX_OF_NUMBER_OF_LINE]:
                    output += '(' + str(self.all_error[counter][self.INDEX_OF_TOKEN]) + ', ' + \
                              str(self.all_error[counter][self.INDEX_OF_CATEGORY]) + ')'
                    counter += 1
                output += '\n'
        writer = open('lexical_errors.txt', 'w')
        writer.write(output)


# my_compiler = LexicalParser()
# my_compiler.open_file('inp.txt')
# my_compiler.process()
# my_compiler.show_tokens()
# my_compiler.show_error()
# my_compiler.export_token()
# my_compiler.export_error()
