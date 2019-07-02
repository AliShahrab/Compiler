def is_intermediate_code(word):
    if word[0] == '#':
        return True
    return False


def find_first_element(statement):
    for word in statement:
        if word[0] == '#':
            continue
        return word


class Parser:
    def __init__(self, compiler):
        self.compiler = compiler
        self.tree = []
        self.semantic_error = False
        self.first = self.compiler.first
        self.follow = self.compiler.follow
        self.current_token = compiler.lexical_analyzer.get_next_token()
        # print(self.compiler.lexical_analyzer.get_next_token()[0])
        self.errors = ['Unexpected Terminal', 'Unexpected Non_Terminal']
        self.parser_error = []
        self.out = ''

    def process(self):
        self.tree.append(['PROGRAM', self.parse(self.find_statement('PROGRAM'))])
        # print()

    def find_statement(self, non_terminal):
        # if non_terminal == 'TEMP_22':
            # print()
        # print(non_terminal)
        if non_terminal in self.compiler.terminals:
            if self.match_token(non_terminal) or non_terminal == self.compiler.epsilon:
                return non_terminal
            else:
                return self.errors[0]
        seconds = self.compiler.grammar.get(non_terminal)
        for statement in seconds:
            first_element = find_first_element(statement)
            if first_element == self.compiler.epsilon and self.match_follow(non_terminal):
                return [first_element]
            if self.match_token(first_element):
                return statement
        return self.errors[1]

    def match_token(self, word):
        # print(word)
        if self.match_first(word):
            return True
        if self.follow.get(word) is None:
            return False

        if self.compiler.epsilon in self.first.get(word):
            if self.current_token[0] in self.follow.get(word):
                return True
            if self.current_token[1] == 'ID':
                if 'id' in self.follow.get(word):
                    return True
            if self.current_token[1] == 'NUM':
                if 'num' in self.follow.get(word):
                    return True

    def match_first(self, word):
        if self.current_token[0] in self.first.get(word):
            return True
        if self.current_token[1] == 'ID':
            if 'id' in self.first.get(word):
                return True
        if self.current_token[1] == 'NUM':
            if 'num' in self.first.get(word):
                return True
        return False

    def match_follow(self, word):
        if self.compiler.epsilon in self.first.get(word):
            return self.match_follow_in(word)

    def match_follow_in(self, word):
        if self.current_token[0] in self.follow.get(word):
            return True
        if self.current_token[1] == 'ID':
            if 'id' in self.follow.get(word):
                return True
        if self.current_token[1] == 'NUM':
            if 'num' in self.follow.get(word):
                return True
        return False

    def match_non_terminal_for_error(self, non_terminal):
        if self.match_first(non_terminal):
            return True
        return self.match_follow_in(non_terminal)

    def parse(self, statement):
        # if statement is not None and statement[0] == 'CALL':
        #     print()
        # if self.current_token[0] == '#multiple':
            # print()
        # print(statement)
        if statement is None:
            return None
        if statement in self.compiler.terminals:
            if statement != self.compiler.epsilon:
                self.current_token = self.compiler.lexical_analyzer.get_next_token()
            return [statement, None]
        result = []
        for word in statement:
            # if self.semantic_error:
            #     break
            # print(word)
            if is_intermediate_code(word):
                if self.have_error() or self.semantic_error:
                    continue
                # if word == '#raise_Illegal_type_of_void':
                #     print()
                result_of_semantic = self.compiler.call_intermediate_code(word)
                if result_of_semantic == 'error':
                        self.semantic_error = True
                        self.compiler.line_of_error = self.current_token[3]
                # print(word)
                # self.show_details()
                # print(word)
                continue
            new_statement = self.find_statement(word)
            if new_statement in self.errors:
                if self.process_error(new_statement, word):
                    result.append([word, self.parse(self.find_statement(word))])
            else:
                result.append([word, self.parse(new_statement)])
        return result

    def show_details(self):
        print('token : ' + str(self.current_token))
        print('current scope : ' + str(self.compiler.current_scope))
        print('semantic stack:')
        print(self.compiler.semantic_stack)
        print('symbol table:')
        print(self.compiler.symbol_table)
        print('PB: ')
        print(self.compiler.PB)
        print('10 first temp')
        for i in range(10):
            print(self.compiler.memory[250 + i], end=', ')
        print('\n*****************')
        print('\n\n')

    def show(self):
        self.show_depth(0, self.tree)
        print(self.out)
        print('_')
        print(self.parser_error)
        print('_')

    def show_depth(self, depth, arr):
        for i in range(len(arr)):
            self.custom_print(arr[i][0], depth)

            if arr[i][0] not in self.compiler.terminals:
                # if arr[i][0] is not None:
                # custom_print(arr[0][0], depth)
                if not (len(arr[i]) > 1 and arr[i][1] is None):
                    self.show_depth(depth + 1, arr[i][1])
                else:
                    self.custom_print(self.compiler.epsilon, depth)

    def custom_print(self, element, depth):
        out = ''
        for i in range(depth):
            out += '|\t'
            # print('|', end='\t')
        out += element
        out += '\n'
        self.out += out
        # print(str(element))

    def process_error(self, type_of_error, word_expected):
        if type_of_error == self.errors[0]:
            previous_token = self.current_token
            # self.current_token = self.compiler.lexical_analyzer.get_next_token()
            self.parser_error.append(str(previous_token[3]) +
                                     '. Syntax Error! Missing TERMINAL \'' + str(word_expected) + '\'')
        elif type_of_error == self.errors[1]:
            ignored_token = ''
            previous_token = self.current_token
            while not self.match_non_terminal_for_error(word_expected):
                if self.current_token[2] == 0:
                    break
                ignored_token += self.current_token[0]
                self.current_token = self.compiler.lexical_analyzer.get_next_token()
            if self.match_token(word_expected):
                self.parser_error.append(str(previous_token[3]) +
                                         '. Syntax Error! Unexpected \'' + str(ignored_token) + '\'')
            else:
                self.parser_error.append(str(previous_token[3]) +
                                         '. Syntax Error! Missing \'' + str(ignored_token) + '\'')

    def show_error(self):
        print(self.parser_error)

    def have_error(self):
        return len(self.parser_error) != 0
