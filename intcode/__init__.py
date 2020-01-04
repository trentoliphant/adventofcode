class intcode:
    def __init__(self, program, input=[], cur_pos=0, rel_base=0, id=0, verbose=False):
        self.memory = program[:]
        self.size = len(program)
        self.cur_input_pos = 0
        if isinstance(input, int):
            input = [input]
        self.input = input
        self.cur_pos = cur_pos
        self.relative_base = rel_base
        self.verbose = verbose
        self.id = id
        self.waiting_for_input = False
        self.output = []
        self.logs = []
    
    def _check_mem(self, pos):
        if pos >= self.size:
            self.log(F'Not enough memory - requested {pos}, existing {self.size}', 2)
            self.memory.extend([0] * (pos - self.size + 1))
            self.size = len(self.memory)
            self.log(F'Increased memory to {self.size}', 2)
    
    def _read_mem(self, pointer, mode):
        if mode == 1:
            self.log(F'Immediate mode returning value: {pointer}', 3)
            return pointer
        if mode == 2:
            pointer = pointer + self.relative_base
            self.log(F'Relative mode moving pointer to {pointer}', 3)
        self._check_mem(pointer)
        to_return = self.memory[pointer]
        self.log(F'Returning value {to_return} from position {pointer}', 2)
        return to_return
    
    def _write_mem(self, pointer, mode, value):
        if mode == 2:
            pointer = pointer + self.relative_base
            self.log(F'Relative mode moving pointer to {pointer}', 3)
        self._check_mem(pointer)
        self.memory[pointer] = value
        self.log(F'Writing value {value} to position {pointer}', 2)

        
    def _get_code_and_modes(self, code):
        scode = F'{code:05}'
        return int(scode[-2:]), int(scode[-3]), int(scode[-4]), int(scode[-5])
    
    def run_opcode(self, code, modes):
        if code == 1:
            self.opcode1(modes)
        if code == 2:
            self.opcode2(modes)
        if code == 3:
            self.opcode3(modes)
        if code == 4:
            self.opcode4(modes)
        if code == 5:
            self.opcode5(modes)
        if code == 6:
            self.opcode6(modes)
        if code == 7:
            self.opcode7(modes)
        if code == 8:
            self.opcode8(modes)
        if code == 9:
            self.opcode9(modes)
    
    def opcode1(self, modes):
        mode_a, mode_b, mode_c = modes
        a, b, c = self.memory[self.cur_pos + 1: self.cur_pos + 4]
        self.log(F'Parameters: {a}, {b}, {c}', 1)
        val_a = self._read_mem(a, mode_a)
        val_b = self._read_mem(b, mode_b)
        self._write_mem(c, mode_c, val_a + val_b)
        self.log(F'Wrote {val_a} + {val_b} = {val_a + val_b} to {c}, mode {mode_c}', 2)
        self.cur_pos += 4

    def opcode2(self, modes):
        mode_a, mode_b, mode_c = modes
        a, b, c = self.memory[self.cur_pos + 1: self.cur_pos + 4]
        self.log(F'Parameters: {a}, {b}, {c}', 1)
        val_a = self._read_mem(a, mode_a)
        val_b = self._read_mem(b, mode_b)
        self._write_mem(c, mode_c, val_a * val_b)
        self.log(F'Wrote {val_a} * {val_b} = {val_a * val_b} to {c}, mode {mode_c}', 2)
        self.cur_pos += 4
        
    def opcode3(self, modes):
        mode = modes[0]
        if self.cur_input_pos >= len(self.input):
            self.waiting_for_input = True
            self.log(F'Waiting for input, cur_pos: {self.cur_pos}',1)
            return
        param = self.memory[self.cur_pos + 1]
        cur_input = self.input[self.cur_input_pos]
        self._write_mem(param, mode, cur_input)
        self.log(F'Wrote {cur_input} to {param}, mode {mode}', 2)
        self.cur_input_pos += 1
        self.cur_pos += 2
    
    def opcode4(self, modes):
        mode = modes[0]
        val = self.memory[self.cur_pos + 1]
        self.log(F'Parameter: {val}', 1)
        to_output = self._read_mem(val, mode)
        self.log(F'Writing {to_output} from {val} mode {mode} to output', 2)
        self.output.append(self._read_mem(val, mode))
        self.log(F'New_output: {self.output}', 2)
        self.cur_pos += 2

    def opcode5(self, modes):
        mode_a, mode_b = modes[:2]
        a, b = self.memory[self.cur_pos + 1: self.cur_pos + 3]
        self.log(F'Parameters: {a}, {b}', 1)
        if self._read_mem(a, mode_a) != 0:
            self.cur_pos = self._read_mem(b, mode_b)
            self.log(F'Jumping to position {self.cur_pos}', 2)
        else:
            self.cur_pos += 3
    
    def opcode6(self, modes):
        mode_a, mode_b = modes[:2]
        a, b = self.memory[self.cur_pos + 1: self.cur_pos + 3]
        self.log(F'Parameters: {a}, {b}', 2)
        if self._read_mem(a, mode_a) == 0:
            self.cur_pos = self._read_mem(b, mode_b)
            self.log(F'Jumping to position {self.cur_pos}', 2)
        else:
            self.cur_pos += 3
        
    def opcode7(self, modes):
        mode_a, mode_b, mode_c = modes
        a, b, c = self.memory[self.cur_pos + 1: self.cur_pos + 4]
        val_to_write = 0
        self.log(F'Parameters: {a}, {b}, {c}', 1)
        val_a = self._read_mem(a, mode_a)
        val_b = self._read_mem(b, mode_b)
        self.log(F'Value to check: {val_a} < {val_b}?', 2)
        if val_a < val_b:
            val_to_write = 1
        self._write_mem(c, mode_c, val_to_write)
        self.log(F'Wrote {val_to_write} to {c}, mode {mode_c}', 2)
        self.cur_pos += 4
    
    def opcode8(self, modes):
        mode_a, mode_b, mode_c = modes
        a, b, c = self.memory[self.cur_pos + 1: self.cur_pos + 4]
        val_to_write = 0
        self.log(F'Parameters: {a}, {b}, {c}', 1)
        val_a = self._read_mem(a, mode_a)
        val_b = self._read_mem(b, mode_b)
        self.log(F'Value to check: {val_a} == {val_b}?', 2)
        if val_a == val_b:
            val_to_write = 1
        self._write_mem(c, mode_c, val_to_write)
        self.log(F'Wrote {val_to_write} to {c}, mode {mode_c}', 2)
        self.cur_pos += 4
        
    def opcode9(self, modes):
        mode = modes[0]
        param = self.memory[self.cur_pos+1]
        self.log(F'Paramater: {param}', 1)
        val = self._read_mem(param, mode)
        self.relative_base += val
        self.log(F'Setting relative base to {self.relative_base}', 2)
        self.cur_pos += 2
        
    def run(self):
        cur_opcode = 0
        while not self.waiting_for_input and cur_opcode !=99:
            codes = self._get_code_and_modes(self.memory[self.cur_pos])
            cur_opcode = codes[0]
            modes = codes[1:]
            self.log('=====================', 3)
            self.log(F'cur_pos: {self.cur_pos}, opcode: {codes}', 1)
            self.run_opcode(cur_opcode, modes)
        self.log(self.output, 1)
        if cur_opcode == 99:
            return cur_opcode

    def step(self):
        codes = self._get_code_and_modes(self.memory[self.cur_pos])
        self.log('=======================', 3)
        self.log(F'cur_pos: {self.cur_pos}, opcode: {codes}', 1)
        self.run_opcode(codes[0], codes[1:])
    
    def log(self, log_string, level=0):
        self.logs.append(log_string)
        if self.verbose >= level:
            print(log_string)
        
    def add_input(self, input):
        if isinstance(input, list):
            self.input.extend(input)
        elif isinstance(input, int):
            self.input.append(input)
        else:
            raise ValueError('Input must be an int or list')
        self.log(F'Added {input} to input buffer, able to restart', 1)
        self.waiting_for_input = False
        
    def flush_output(self):
        self.output = []