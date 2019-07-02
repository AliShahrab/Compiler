def find_next_token(index, statement, length):
    result = ''
    while index < length and statement[index] == ' ':
        index += 1
    while index < length and statement[index] != ' ':
        result += statement[index]
        index += 1
    return result, index


def make_pure(word):
    result = ''
    index = 0
    while word[index] == ' ':
        index += 1
    while index < len(word) and word[index] != ' ':
        result += word[index]
        index += 1
    return result


def find_details(statement):
    index = 0
    length = len(statement)
    result = []
    while index < length:
        word, index = find_next_token(index, statement, length)
        if word != '':
            result.append(word)
    return result


def find_all_of_second(second):
    all_local = second.split('|')
    result = []
    for i in range(len(all_local)):
        sub_result = find_details(all_local[i])
        result.append(sub_result)
    return result


class LL1_Helper:
    def __init__(self):
        self.epsilon = 'Ïµ'
        self.text_input = ''
        self.terminals = ['$',
                          'id',
                          ';',
                          '[',
                          ']',
                          'num',
                          'int',
                          'void',
                          '{',
                          '}',
                          'continue',
                          'break',
                          'if',
                          'else',
                          '(',
                          ')',
                          'while',
                          'return',
                          'switch',
                          'case',
                          ':',
                          'default',
                          '=',
                          '<',
                          '==',
                          '+',
                          '-',
                          '*',
                          ',',
                          'Ïµ']

        self.grammar = {'': []}
        self.first = {'': []}
        self.follow = {'': []}

    def set_rule_of_grammar(self, text_input):
        lines = text_input.splitlines()
        for i in range(len(lines)):
            current_line = lines[i].split('->')
            self.grammar.update({make_pure(current_line[0]): find_all_of_second(current_line[1])})
            self.first.update({make_pure(current_line[0]): []})
            self.follow.update({make_pure(current_line[0]): []})
        for terminal in self.terminals:
            self.first.update({terminal: [terminal]})
        self.grammar.pop('')
        self.first.pop('')
        self.follow.pop('')

    def find_epsilon_of_first(self):
        keys = list(self.grammar.keys())
        for i in range(len(keys)):
            self.find_first_epsilon_by_element(keys[i])

    def is_epsilon_in_first(self, element):
        return self.first.get(element) is not None and self.epsilon in self.first.get(element)

    def add_to_first(self, terminal_element, element):
        if self.first.get(element) is not None and terminal_element not in self.first.get(element):
            self.first.get(element).append(terminal_element)

    def add_first(self, words, element):
        if words is None:
            return
        for word in words:
            self.add_to_first(word, element)

    def find_first_by_element(self, element):
        if element in self.terminals:
            return [element]
        first = []
        # if element == 'VAR_DECLARATION':
            # print()
        second = self.grammar.get(element)
        for statement in second:
            for word in statement:
                if word[0] == '#':
                    continue
                help_list = self.find_first_by_element(word)
                for element_first in help_list:
                    if element_first in self.terminals:
                        first.append(element_first)
                if not self.is_epsilon_in_first(word):
                    break
        for element_first in first:
            if element_first in self.terminals:
                self.add_to_first(element_first, element)
        return first

    def find_all_first(self):
        keys = list(self.grammar.keys())
        for i in range(len(keys)):
            self.find_first_by_element(keys[i])

    def find_first_epsilon_by_element(self, element):
        # print(element)
        if element == self.epsilon:
            return True
        if element in self.terminals:
            return False
        second = self.grammar.get(element)
        have_epsilon = True
        for i in range(len(second)):
            statement = second[i]
            count = 0
            # if element == 'VAR_DECLARATION':
            #     print()
            for j in range(len(statement)):
                # print(statement[j])
                if statement[j][0] == '#':
                    # print('heyyyyyy')
                    continue
                if self.first.get(statement[j]) is not None and self.epsilon in self.first.get(statement[j]):
                    continue
                if not self.find_first_epsilon_by_element(statement[j]):
                    break
                count += 1
            if count == len(statement):
                if self.first.get(element) is not None and self.epsilon not in self.first.get(element):
                    self.first.get(element).append(self.epsilon)
                return True

    def add_follow(self, words, element):
        if words is None:
            return
        for word in words:
            self.add_to_follow(word, element)

    def add_to_follow(self, terminal_element, element):
        if self.follow.get(element) is not None and terminal_element not in self.follow.get(element):
            if terminal_element is not self.epsilon:
                self.follow.get(element).append(terminal_element)

    def find_follow_by_statement(self, statement):
        # print(statement)
        if statement[0] == '{':
            print()
        for i in range(len(statement) - 1):
            if statement[i][0] == '#':
                continue
            count = i + 1
            while count < len(statement) and statement[count][0] == '#':
                count += 1
            if count == len(statement):
                continue
            self.add_follow(self.first.get(statement[count]), statement[i])
            # while count + 1 < len(statement) and self.epsilon in self.first.get(statement[count]):
            #     count += 1
            #     self.add_follow(self.first.get(statement[count]), statement[i])

    def find_follow_second_step(self, element):
        second = self.grammar.get(element)
        for statement in second:
            count = len(statement) - 1
            while statement[count][0] == '#':
                count -= 1
            self.add_follow(self.follow.get(element), statement[count])
            while (count - 1 > 0 and self.epsilon in self.first.get(statement[count])) or \
                    (count - 1 > 0 and statement[count][0] == '#'):
                # print('yesss')
                count -= 1
                if statement[count + 1][0] == '#':
                    continue
                self.add_follow(self.follow.get(element), statement[count])

    def find_follow(self):
        keys = list(self.grammar.keys())
        self.follow.get(keys[0]).append('$')
        for i in range(len(keys)):
            for statement in self.grammar.get(keys[i]):
                # if 'DECLARATION_LIST' in statement:
                #     print('hey')
                self.find_follow_by_statement(statement)
        # print(self.follow)
        for i in range(len(keys)):
            self.find_follow_second_step(keys[i])

    def process_first_follow(self):
        file = open('rules.txt', 'r')
        text = file.read()
        self.set_rule_of_grammar(text)
        self.find_epsilon_of_first()
        self.find_all_first()
        self.find_follow()



# helper = LL1_Helper
# file = open('rules.txt', 'r')
# text = file.read()
# helper = LL1_Helper()
# helper.set_rule_of_grammar(text)
# print(helper.grammar)
# helper.find_epsilon_of_first()
# amo = list(helper.grammar)
# helper.find_all_first()
# print(helper.first)
# # helper.
# helper.find_follow()
# print('******')
# print(helper.follow)

