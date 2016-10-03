class Parser:
    def __init__(self, expression):
        self.expression = expression
        self.index = 0

    def get_value(self):
        value = self.parse_expression()
        return value

    def get_next(self):
        return self.expression[self.index:self.index + 1]

    def has_next(self):
        return self.index < len(self.expression)

    def parse_expression(self):
        return self.parse_addition_subtraction()

    def parse_addition_subtraction(self):
        values = [self.parse_multiplication_division()]
        while True:
            char = self.get_next()
            if char == '+':
                self.index += 1
                values.append(self.parse_multiplication_division())
            elif char == '-':
                self.index += 1
                values.append(-1 * self.parse_multiplication_division())
            else:
                break
        return str(sum(values))

    def parse_multiplication_division(self):
        values = [self.parse_number()]
        while True:
            char = self.get_next()
            if char == '*':
                self.index += 1
                values.append(self.parse_number())
            elif char == '/':
                self.index += 1
                denominator = self.parse_number()
                values.append(1.0 / denominator)
            else:
                break
        value = 1.0
        for factor in values:
            value *= factor
        return int(value)

    def parse_number(self):
        strvalue = ''
        while self.has_next():
            char = self.get_next()
            if char in '0123456789':
                strvalue += char
            else:
                break
            self.index += 1
        return int(strvalue)
