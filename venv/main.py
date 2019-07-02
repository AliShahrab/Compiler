lexical_analyzer = __import__('lexical_analyzer')
helper_ll1 = __import__('ll1_helper')
parser = __import__('Parser')


def map_address(address):
    return int(address / 4)


def make_immediate(input_element):
    return '#' + str(input_element)


def make_indirect(input_element):
    return '@' + str(input_element)


def create_name_of_return_value(name_of_function):
    return '_return_value_' + str(name_of_function) + '_'


def create_name_of_return_address(name_of_function):
    return '_return_address_' + str(name_of_function) + '_'


class Compiler:
    def __init__(self):
        self.START_OF_STORE_OF_VARIABLE = 500
        self.START_OF_TEMP = 1000
        self.PB = 125 * ['']
        self.memory = 375 * [-1]
        self.semantic_stack = [0]
        self.code_counter = 1
        self.symbol_table = {'output': [996, 'void', 0, 0, 'int', 992]}
        self.symbol_table.update({'zxcklncvb': [992, 'int', 0]})
        # self.symbol_table.pop('')
        self.pointer_of_variable = 500
        self.pointer_of_temp = 1000
        self.size_of_int = 4
        self.current_scope = 0
        self.counter_of_scope = 0
        self.scopes = [[0]]
        self.ADDRESS = 0
        self.TYPE = 1
        self.SCOPE = 2
        self.START_OF_FUNCTION = 3
        self.START_OF_VARIABLE = 4
        self.ignore_scope_check = False
        self.have_error = False
        self.error = ''
        self.line_of_error = -1

        self.in_text = ''
        self.output = []
        self.pointer = 0
        self.lexical_analyzer = lexical_analyzer.LexicalParser()
        self.lexical_analyzer.process()
        self.helper_ll1 = helper_ll1.LL1_Helper()
        self.helper_ll1.process_first_follow()
        self.first = self.helper_ll1.first
        self.follow = self.helper_ll1.follow
        self.grammar = self.helper_ll1.grammar
        self.terminals = self.helper_ll1.terminals
        self.epsilon = self.helper_ll1.epsilon
        self.parser = parser.Parser(self)
        self.parser.process()
        # self.parser.show()
        self.tree = self.parser.tree
        # print(self.memory)

    def set_in_text(self, text):
        self.in_text = text

    def next_element(self):
        self.pointer += 1
        return self.in_text[self.pointer]

    def find_address(self, id_of_input):
        keys = self.symbol_table.keys()
        if keys is not None and id_of_input in keys:
            return self.symbol_table.get(id_of_input)[0]
        else:
            self.symbol_table.update({id_of_input: [self.pointer_of_variable]})
            return self.pointer_of_variable

    def raise_illegal_type_of_void(self):
        self.have_error = True
        self.error = 'Illegal type of void'
        return 'error'

    def get_temp(self):
        self.pointer_of_temp += 4
        return self.pointer_of_temp - 4

    def push(self, variable):
        self.semantic_stack.append(variable)

    def pid(self):
        symbol_of_id = self.parser.current_token[0]
        address_of_id = self.find_address(symbol_of_id)
        self.push(address_of_id)

    def ss_read(self, distance_from_top):
        if len(self.semantic_stack) == 0:
            print('semantic stack is empty and you want to read from it!!!')
            return None
        return self.semantic_stack[len(self.semantic_stack) - 1 - distance_from_top]

    def set_id(self):
        if self.check_type() == 'error':
            return 'error'
        self.pointer_of_variable += self.size_of_int
        self.symbol_table.get(str(self.find_symbol_by_address(self.ss_read(0)))).append('int')
        self.symbol_table.get(str(self.find_symbol_by_address(self.ss_read(0)))).append(self.current_scope)
        self.pop(2)

    def check_type(self):
        type_of_variable = self.ss_read(1)
        if type_of_variable == 'void':
            self.have_error = True
            self.error = 'Illegal type of word!'
            return 'error'

    def set_array(self):
        if self.check_type() == 'error':
            return 'error'
        size_of_array = int(self.parser.current_token[0])
        self.pointer_of_variable += size_of_array * self.size_of_int
        self.symbol_table.get(str(self.find_symbol_by_address(self.ss_read(0)))).append('int*')
        self.symbol_table.get(str(self.find_symbol_by_address(self.ss_read(0)))).append(self.ss_read(2))
        self.pop(2)

    def hello_world(self):
        print(hasattr(self, 'pid'))

    def call_intermediate_code(self, word):
        if hasattr(self, word[1:]):
            getattr(self, word[1:])()
            if self.have_error:
                return 'error'
        else:
            print('name of function is not True')

    def pop(self, number_of_element=1):
        for i in range(number_of_element):
            self.semantic_stack.pop()

    def push_token(self):
        self.push(self.parser.current_token[0])

    def find_symbol_by_address(self, address):
        keys = self.symbol_table.keys()
        for key in keys:
            if self.symbol_table.get(key)[0] == address:
                return key
        return False

    def define_function(self):
        self.pointer_of_variable += self.size_of_int
        name_of_function = self.find_symbol_by_address(self.ss_read(0))
        self.symbol_table.get(str(self.find_symbol_by_address(self.ss_read(0)))).append(self.ss_read(1))
        self.symbol_table.get(str(self.find_symbol_by_address(self.ss_read(0)))).append(self.current_scope)
        self.symbol_table.get(name_of_function).append(self.code_counter)

        self.memory[map_address(self.ss_read(0))] = self.code_counter

        # define return value

        self.find_address(create_name_of_return_value(name_of_function))
        self.pointer_of_variable += self.size_of_int
        self.symbol_table.get(create_name_of_return_value(name_of_function)).append(self.ss_read(1))

        # define return address

        self.find_address(create_name_of_return_address(name_of_function))
        self.pointer_of_variable += self.size_of_int
        self.symbol_table.get(create_name_of_return_address(name_of_function)).append('int')

        # self.pop(2)

    def set_void_for_input(self):
        self.symbol_table.get(str(self.find_symbol_by_address(self.ss_read(0)))).append(self.parser.current_token[0])

    def end_define_function(self):
        self.push('function')
        self.jp_intermediate_code(self.code_counter + 4, self.code_counter)
        self.plus_code_counter()

        self.push_code_counter()

        address_of_function = self.ss_read(2)
        name_of_function = self.find_symbol_by_address(address_of_function)
        self.jp_intermediate_code(make_indirect(self.find_address(create_name_of_return_address(name_of_function))),
                                  self.code_counter)

        self.plus_code_counter()

        if self.is_void(self.find_address(create_name_of_return_value(name_of_function))):
            self.jp_intermediate_code(self.code_counter + 1, self.code_counter)
            self.plus_code_counter()
        else:
            self.assign_intermediate_code(self.find_address(create_name_of_return_value(name_of_function)),
                                          make_immediate(0))
        self.assign_intermediate_code(self.find_address(create_name_of_return_address(name_of_function)),
                                      make_immediate(0))

        # self.pop(2)

    def push_scope_and_save_jump(self):
        self.push_and_save_code_counter()
        self.push(self.current_scope)
        self.define_new_scope()

    def push_and_save_code_counter(self):
        self.push(self.code_counter)
        self.plus_code_counter()

    def plus_code_counter(self):
        self.code_counter += 1

    def set_jump_to_current_with_top_of_stack_and_pop(self):
        t = self.ss_read(1)
        self.PB[t] = '(JP, ' + str(self.code_counter) + ', , )'
        # self.pop()

    # def read_from_memory(self, address):
    #     return self.memory[map_address(address)]

    # def assign_immediate_intermediate_code(self, address, value):
    #     self.PB[self.code_counter] = '(ASSIGN,#' + str(value) + ',' + str(address) + ',)'

    def define_new_scope(self):
        self.counter_of_scope += 1
        self.scopes.append([self.counter_of_scope])
        self.scopes[self.current_scope].append(self.counter_of_scope)
        self.current_scope = self.counter_of_scope

    def delete_current_scope_and_set_scope(self):
        self.current_scope = self.ss_read(0)
        self.pop(2)
        # self.pop()

    # def write_on_temp(self, value):
    #     t = self.get_temp()
    #     self.assign_immediate(t, value)
    #     return t

    def get_element_of_array(self):
        distance = self.ss_read(0)
        start = self.ss_read(1)
        t = self.get_temp()
        self.mult_intermediate_code(distance, make_immediate(self.size_of_int), distance)
        self.add_intermediate_code(distance, make_immediate(start), t)
        self.pop(2)
        self.push(make_indirect(t))

    def assign(self):
        right = self.ss_read(0)
        left = self.ss_read(1)
        self.pop()
        self.assign_intermediate_code(left, right)

    def set_pb(self, instruction):
        self.PB[self.code_counter] = instruction
        self.code_counter += 1

    def assign_intermediate_code(self, left, right):
        if self.fault_scope(left):
            self.set_fault_scope(left)
            return 'error'
        if self.fault_scope(right):
            self.set_fault_scope(right)
            return 'error'
        if self.fault_type(left, right):
            self.set_fault_type()
            return 'error'

        self.PB[self.code_counter] = '(ASSIGN, ' + str(right) + ', ' + str(left) + ', )'
        self.plus_code_counter()

    def assign_to_temp_token_and_push_temp(self):
        t = self.get_temp()
        value = self.parser.current_token[0]
        self.assign_intermediate_code(t, make_immediate(value))
        self.push(t)

    def add_intermediate_code(self, right_first, right_second, left):
        if self.fault_scope(right_first):
            self.set_fault_scope(right_first)
            return 'error'
        if self.fault_scope(right_second):
            self.set_fault_scope(right_second)
            return 'error'
        if self.fault_scope(left):
            self.set_fault_scope(left)
            return 'error'
        if self.fault_type(right_second, right_first):
            self.set_fault_type()
            return 'error'
        if self.fault_type(right_first, left):
            self.set_fault_type()
            return 'error'

        self.PB[self.code_counter] = '(ADD,' + str(right_first) + ',' + str(right_second) + ',' + str(left) + ')'
        self.plus_code_counter()

    def mult_intermediate_code(self, right_first, right_second, left):
        if self.fault_scope(right_first):
            self.set_fault_scope(right_first)
            return 'error'
        # if self.fault_scope(right_second):
        #     print()
        if self.fault_scope(right_second):
            self.set_fault_scope(right_second)
            return 'error'
        if self.fault_scope(left):
            self.set_fault_scope(left)
            return 'error'
        if self.fault_type(right_second, right_first):
            self.set_fault_type()
            return 'error'
        if self.fault_type(right_first, left):
            self.set_fault_type()
            return 'error'

        self.PB[self.code_counter] = '(MULT,' + str(right_first) + ',' + str(right_second) + ',' + str(left) + ')'
        self.plus_code_counter()

    def export(self):
        out = ''
        for i in range(self.code_counter):
            # print(i, end='\t')
            # print(self.PB[self.code_counter])
            out += str(i) + '\t' + str(self.PB[i]) + '\n'
        print(out)
        open('output.txt', 'w').write(out)

    def adding(self):
        first = self.ss_read(0)
        second = self.ss_read(1)
        t = self.get_temp()
        self.add_intermediate_code(first, second, t)
        self.pop(2)
        self.push(t)

    def subtraction(self):
        second = self.ss_read(0)
        first = self.ss_read(1)
        t = self.get_temp()
        self.subtraction_intermediate_code(first, second, t)
        self.pop(2)
        self.push(t)

    def subtraction_intermediate_code(self, right_first, right_second, left):
        if self.fault_scope(right_first):
            self.set_fault_scope(right_first)
            return 'error'
        if self.fault_scope(right_second):
            self.set_fault_scope(right_second)
            return 'error'
        if self.fault_scope(left):
            self.set_fault_scope(left)
            return 'error'
        if self.fault_type(right_second, right_first):
            self.set_fault_type()
            return 'error'
        if self.fault_type(right_first, left):
            self.set_fault_type()
            return 'error'

        self.PB[self.code_counter] = '(SUB,' + str(right_first) + ',' + str(right_second) + ',' + str(left) + ')'
        self.plus_code_counter()

    def multiple(self):
        first = self.ss_read(0)
        second = self.ss_read(1)
        t = self.get_temp()
        self.mult_intermediate_code(first, second, t)
        self.pop(2)
        self.push(t)

    def mirror(self):
        first = self.ss_read(0)
        t = self.get_temp()
        self.subtraction_intermediate_code(make_immediate(0), first, t)
        self.pop()
        self.push(t)

    def less(self):
        right = self.ss_read(0)
        left = self.ss_read(1)
        self.pop(2)
        t = self.get_temp()
        self.lt_intermediate_code(left, right, t)
        self.push(t)

    def lt_intermediate_code(self, left, right, result):
        if self.fault_scope(left):
            self.set_fault_scope(left)
            return 'error'
        if self.fault_scope(right):
            self.set_fault_scope(right)
            return 'error'
        if self.fault_scope(result):
            self.set_fault_scope(result)
            return 'error'
        if self.fault_type(right, left):
            self.set_fault_type()
            return 'error'
        if self.fault_type(left, result):
            self.set_fault_type()
            return 'error'

        self.PB[self.code_counter] = '(LT,' + str(left) + ',' + str(right) + ',' + str(result) + ')'
        self.plus_code_counter()

    def equal(self):
        right = self.ss_read(0)
        left = self.ss_read(1)
        self.pop(2)
        t = self.get_temp()
        self.eq_intermediate_code(left, right, t)
        self.push(t)

    def eq_intermediate_code(self, left, right, result):
        if self.fault_scope(left):
            self.set_fault_scope(left)
            return 'error'
        if self.fault_scope(right):
            self.set_fault_scope(right)
            return 'error'
        if self.fault_scope(result):
            self.set_fault_scope(result)
            return 'error'
        if self.fault_type(right, left):
            self.set_fault_type()
            return 'error'
        if self.fault_type(left, result):
            self.set_fault_type()
            return 'error'

        self.PB[self.code_counter] = '(EQ,' + str(left) + ',' + str(right) + ',' + str(result) + ')'
        self.plus_code_counter()

    def push_code_counter(self):
        self.push(self.code_counter)

    def push_code_counter_and_save(self):
        self.push_code_counter()
        self.plus_code_counter()

    def while_intermediate_code(self):
        before_expression = self.ss_read(2)
        condition = self.ss_read(1)
        after_expression = self.ss_read(0)
        self.jp_intermediate_code(self.code_counter + 1, before_expression + 1)
        self.jpf_intermediate_code(condition, self.code_counter + 1, after_expression)
        self.jp_intermediate_code(before_expression, self.code_counter)
        self.plus_code_counter()
        self.pop(4)

    def jpf_intermediate_code(self, condition, label, code_counter):
        if self.fault_scope(condition):
            self.set_fault_scope(condition)
            return 'error'
        if self.fault_scope(label):
            self.set_fault_scope(label)
            return 'error'

        self.PB[code_counter] = '(JPF,' + str(condition) + ',' + str(label) + ',)'

    def jp_intermediate_code(self, label, code_counter):
        if self.fault_scope(label):
            self.set_fault_scope(label)
            return 'error'

        self.PB[code_counter] = '(JP,' + str(label) + ', ,)'

    def set_jpf_and_push_code_counter_and_save(self):
        condition = self.ss_read(1)
        before_expression = self.ss_read(0)
        self.jpf_intermediate_code(condition, self.code_counter + 1, before_expression)
        self.pop(2)
        self.push_code_counter()
        self.plus_code_counter()

    def equal_zero(self):
        self.push(make_immediate(0))
        self.equal()

    def if_intermediate_code(self):
        label = self.ss_read(0)
        self.jp_intermediate_code(self.code_counter, label)
        self.pop()

    def push_int_type(self):
        self.push('int')

    def push_arr_type(self):
        self.push('int*')

    def set_param_of_function(self):
        type_of_param = self.ss_read(0)
        id_of_param = self.ss_read(1)
        address_of_function = self.ss_read(2)
        self.symbol_table.get(self.find_symbol_by_address(address_of_function)).append(type_of_param)
        self.symbol_table.get(self.find_symbol_by_address(address_of_function)).append(id_of_param)

        self.symbol_table.get(self.find_symbol_by_address(id_of_param)).append(type_of_param)
        self.symbol_table.get(self.find_symbol_by_address(id_of_param)).append(self.current_scope)

        self.pointer_of_variable += self.size_of_int
        self.pop(2)

    def push_call(self):
        # self.ke
        self.push('call')

    def set_arguments(self):
        number_of_input = 0
        while self.ss_read(number_of_input) != 'call':
            number_of_input += 1
        address_of_function = self.ss_read(number_of_input + 1)
        name_of_function = self.find_symbol_by_address(address_of_function)
        if len(self.symbol_table.get(name_of_function)) < 2:
            self.have_error = True
            self.error = str(name_of_function) + ' is not defined!'
            return 'error'
        inputs = []
        # if name_of_function == 'foo2':
        #     print()
        if self.fault_scope(address_of_function):
            self.set_fault_scope(address_of_function)
            self.error = str(name_of_function) + ' is not defined!'
            return 'error'
        # print(address_of_function)
        args = self.get_address_of_args_of_function(address_of_function)
        for i in range(number_of_input):
            inputs.append(self.ss_read(number_of_input - i - 1))
        if len(inputs) != len(args):
            self.have_error = True
            self.error = 'Mismatch in number of arguments ' + str(name_of_function)
            return 'error'
        self.ignore_scope_check = True
        for i in range(number_of_input):
            self.assign_intermediate_code(args[i][1], inputs[i])
        self.ignore_scope_check = False
        self.pop(number_of_input)

    def get_address_of_args_of_function(self, address_of_function):
        name_of_function = self.find_symbol_by_address(address_of_function)
        result = []
        counter = self.START_OF_VARIABLE
        t = self.symbol_table.get(name_of_function)
        if t[counter] == 'void':
            return []
        while counter < len(t):
            result.append([t[counter], t[counter + 1]])
            counter += 2
        return result

    def set_jp_to_end_of_function(self):
        # place_of_jump = self.ss_read(0)
        # self.jp_intermediate_code(self.code_counter, place_of_jump)
        self.pop(4)

    def calling(self):
        address_of_function = self.ss_read(1)
        name_of_function = self.find_symbol_by_address(address_of_function)
        start_of_function = self.symbol_table.get(name_of_function)[0]

        if name_of_function == 'output':
            address_of_input = self.symbol_table.get(name_of_function)[self.START_OF_VARIABLE + 1]
            self.print_intermediate_code(address_of_input)
        else:
            return_address = self.find_address(create_name_of_return_address(name_of_function))
            self.assign_intermediate_code(return_address, make_immediate(self.code_counter + 3))
            self.assign_intermediate_code(self.find_address(name_of_function),
                                          make_immediate(
                                              self.symbol_table.get(name_of_function)[self.START_OF_FUNCTION]))
            self.jp_intermediate_code(make_indirect(start_of_function), self.code_counter)
            self.plus_code_counter()

        self.pop(2)
        return_value = self.find_address(create_name_of_return_value(name_of_function))
        self.push(return_value)

    def push_void(self):
        self.push('void')

    def find_first_of_function(self):
        counter = 0
        while self.ss_read(counter) != 'function':
            counter += 1
        return counter

    def set_return_value_and_set_jmp_to_first_of_function(self):
        index_of_function = self.find_first_of_function()
        first_of_function = self.ss_read(index_of_function - 1)
        address_of_function = self.ss_read(index_of_function + 1)
        name_of_function = self.find_symbol_by_address(address_of_function)
        if not self.is_void(self.find_address(create_name_of_return_value(name_of_function))):
            self.assign_intermediate_code(self.find_address(create_name_of_return_value(name_of_function)),
                                          self.ss_read(0))
        self.jp_intermediate_code(first_of_function, self.code_counter)
        self.plus_code_counter()
        self.pop()

    def find_index_of_call(self):
        counter = 0
        while self.ss_read(counter) != 'call':
            counter += 1
        return counter

    def print_intermediate_code(self, value):
        if self.fault_scope(value):
            self.set_fault_scope(value)
            return 'error'
        self.PB[self.code_counter] = '(PRINT,' + str(value) + ', ,)'
        self.plus_code_counter()

    def in_scope(self, current_scope, scope_of_value):
        if current_scope in self.scopes[scope_of_value]:
            return True
        if len(self.scopes[scope_of_value]) == 1:
            return False
        result = False
        for i in self.scopes[scope_of_value]:
            if i == scope_of_value:
                continue
            result = result or self.in_scope(current_scope, i)
        return result

    def in_scope_variable(self, address):
        # print(address)
        if len(self.symbol_table.get(self.find_symbol_by_address(address))) <= self.SCOPE:
            return True
        scope_of_variable = self.symbol_table.get(self.find_symbol_by_address(address))[self.SCOPE]
        # print(scope_of_variable)
        # print(self.current_scope)
        return self.in_scope(self.current_scope, scope_of_variable)

    def fault_scope(self, variable):
        # if self.ignore_scope_check:
        #     return False
        if variable == 'void':
            return False
        if str(variable)[0] == '@' or str(variable)[0] == '#' or variable >= self.START_OF_TEMP or \
                variable < self.START_OF_STORE_OF_VARIABLE:
            return False
        if len(self.symbol_table.get(self.find_symbol_by_address(variable))) < 2:
            return True
        else:
            return not self.in_scope_variable(variable)

    def set_fault_scope(self, address):
        self.have_error = True
        name_of_variable = self.find_symbol_by_address(address)
        self.error = '\"' + str(name_of_variable) + '\" is not defined!'

    def fault_type(self, add1, add2):
        # if str(add2) == '528' and str(add1) == '572':
        #     print()
        if self.is_void(add1) and not self.is_void(add2):
            if self.is_assign_function(add1, add2):
                return False
            return True
        if not self.is_void(add1) and self.is_void(add2):
            return True
        if self.is_void(add1) and self.is_void(add2):
            return False
        if str(add1)[0] == '#' or str(add1)[0] == '@' or str(add2)[0] == '#' or str(add2)[0] == '@' or \
                add1 >= self.START_OF_TEMP or add2 >= self.START_OF_TEMP:
            return False
        name1 = self.find_symbol_by_address(add1)
        name2 = self.find_symbol_by_address(add2)
        type1 = self.symbol_table.get(name1)[self.TYPE]
        type2 = self.symbol_table.get(name2)[self.TYPE]
        return type1 != type2

    def set_fault_type(self):
        self.have_error = True
        self.error = 'Type mismatch in operands'

    def is_void(self, address):
        if str(address) == 'void':
            return True
        if str(address)[0] == '@' or str(address)[0] == '#':
            return False
        if address >= self.START_OF_TEMP or address < self.START_OF_STORE_OF_VARIABLE:
            return False
        name_of_variable = self.find_symbol_by_address(address)
        # print(address)
        if self.symbol_table.get(name_of_variable)[self.TYPE] == 'void':
            return True
        return False

    def is_assign_function(self, add1, add2):
        if len(self.symbol_table.get(self.find_symbol_by_address(add1))) > 3:
            return True
        if len(self.symbol_table.get(self.find_symbol_by_address(add2))) > 3:
            return True
        return False

    def save(self):
        self.jp_intermediate_code(self.code_counter + 2, self.code_counter)
        self.plus_code_counter()
        self.plus_code_counter()

    def continue_of_while(self):
        index_of_while = self.index_of_while()
        if index_of_while is None:
            self.have_error = True
            self.error = 'No while found for continue!'
            return 'error'
        before_expression = self.ss_read(index_of_while - 1)
        self.jp_intermediate_code(before_expression, self.code_counter)
        self.plus_code_counter()

    def index_of_while(self):
        index_of_while = 0
        while index_of_while < len(self.semantic_stack) and self.ss_read(index_of_while) != 'while':
            index_of_while += 1
        if index_of_while == len(self.semantic_stack):
            return None
        return index_of_while

    def break_of_while(self):
        index_of_while = self.index_of_while()
        before_expression = self.ss_read(index_of_while - 1)
        self.jp_intermediate_code(before_expression + 1, self.code_counter)
        self.plus_code_counter()

    def push_while(self):
        self.push('while')

    def break_all(self):
        counter = 0
        while counter < len(self.semantic_stack) and self.ss_read(counter) != 'while' and \
                self.ss_read(counter) != 'switch':
            counter += 1
        if counter == len(self.semantic_stack):
            # print()
            self.have_error = True
            self.error = 'No while or switch found for break!'
        if self.ss_read(counter) == 'while':
            self.break_of_while()
        else:
            print()
            # TODO: set break of switch

    def show_error(self):
        print(self.error)

    def export_error(self):
        lexical_error = self.lexical_analyzer.all_error
        parse_error = self.parser.parser_error
        semantic_error = self.error
        out = ''
        out += 'lexical error:\n'
        for i in range(len(lexical_error)):
            # out += str(lexical_error[i])
            out += str(lexical_error[i][2]) + '. ' + str(lexical_error[i][0]) + ': ' + str(lexical_error[i][1])
            out += '\n'
        out += '\n\nparser error:\n'
        for i in range(len(parse_error)):
            out += parse_error[i]
            out += '\n'

        out += '\n\nsemantic error:\n'
        if self.have_error:
            out += str(self.line_of_error) + '. ' + self.error
        print(out)
        open('output_error.txt', 'w').write(out)

    def final_process(self):
        # main error
        # print('lexical error')
        # self.lexical_analyzer.show_error()
        # print('parser error')
        # self.parser.show_error()
        # print('semantic error')
        if self.have_error or len(self.lexical_analyzer.all_error) != 0 or len(self.parser.parser_error) != 0:
            # self.show_error()
            self.export_error()
            return
        keys = self.symbol_table.keys()
        if 'main' not in keys:
            self.error = 'main function not found'
            print(self.error)
            return
        elif self.symbol_table.get('main')[self.TYPE] != 'void' or \
                self.symbol_table.get('main')[self.START_OF_VARIABLE] != 'void' or \
                len(self.symbol_table.get('main')) != 5:
            self.error = 'main function not found'
            print(self.error)
            return
        #
        self.jp_intermediate_code(self.symbol_table.get('main')[self.START_OF_FUNCTION], 0)
        compiler.export()


compiler = Compiler()
# print(compiler.error)
compiler.final_process()
# compiler.lexical_analyzer.open_file('inp.txt')
# compiler.lexical_analyzer.process()
# print(compiler.parser.parser_error)
# print(compiler.hello_world())
# print(compiler.symbol_table)
# print(compiler.semantic_stack)
# print(compiler.PB)

