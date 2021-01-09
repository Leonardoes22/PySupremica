# https://stackoverflow.com/questions/11133339/parsing-a-complex-logical-expression-in-pyparsing-in-a-binary-tree-fashion
import pyparsing as pp

operator = pp.Regex(">=|<=|!=|>|<|==").setName("operator")

integer = pp.Regex(r"[+-]?\d+")
identifier = pp.Word(pp.alphas + "_", pp.alphanums + "_")

comparison_term = identifier | integer 
condition = pp.Group(comparison_term + operator + comparison_term)

expr = pp.operatorPrecedence(condition,[
                            ("&", 2, pp.opAssoc.LEFT, ),
                            ("|", 2, pp.opAssoc.LEFT, ),
                            ])


def parse_expression(exp):

    return expr.parseString(exp)[0]

def isInt(str):

    try:
        integer.parseString(str)
        return True
    except:
        return False



