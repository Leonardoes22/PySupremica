# https://stackoverflow.com/questions/11133339/parsing-a-complex-logical-expression-in-pyparsing-in-a-binary-tree-fashion
import pyparsing as pp

operator = pp.Regex(">=|<=|!=|>|<|==").setName("operator")

integer = pp.Regex(r"[+-]?\d+")
identifier = pp.Word(pp.alphas + "_.", pp.alphanums + "_.")

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



test = "((y == 1 &  x == 1)  & ((-1 <= h11 - h21)  &  (h11 - h21 <= 1))) | ((y == 1 &  x == 2)  & ((-1 <= h12 - h22)  &  (h12 - h22 <= 1)))"
test2 = "(y == 1 &  x == 1)"
test3 = "((y == 0 & x == 0) & (0 == h11)) |  ((y == 1 & x == 2) & (h12 == h11)) | ((y == 2 & x == 1) & (h21 == h11))"
test4 = "(y == 0 & (h11 - h21))"

tree = parse_expression(test4)


def printTree(tree, it=0):

    for e in tree:

        if isinstance(e,str):
            print(it*" . "+ e)
        else:
            printTree(e,it=it+1)



        


printTree(tree)
print(tree)
