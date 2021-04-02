# https://stackoverflow.com/questions/11133339/parsing-a-complex-logical-expression-in-pyparsing-in-a-binary-tree-fashion
import pyparsing as pp

operator = pp.Regex(">=|<=|!=|>|<|==").setName("operator")
actionOperator = pp.Regex("\+|-")
actionAssigner = pp.Regex("=|\+=|-=")

integer = pp.Regex(r"[+-]?\d+")
identifier = pp.Word(pp.alphas + "_.", pp.alphanums + "_.")
comparison_term = identifier | integer 


actionOperation = pp.Group(comparison_term + actionOperator + comparison_term)

attribution = pp.Group(identifier + actionAssigner + (actionOperation|comparison_term))
condition = pp.Group((actionOperation|comparison_term) + operator + (actionOperation|comparison_term))

guardExp = pp.operatorPrecedence(condition,[
                            ("&", 2, pp.opAssoc.LEFT, ),
                            ("|", 2, pp.opAssoc.LEFT, )
                            ])

actionExp = pp.operatorPrecedence(attribution, [(";",2,pp.opAssoc.LEFT, )])



def parse_guard(exp):

    post_guard = guardExp.parseString(exp)[0]

    while(len(post_guard) > 3):

        fusion = pp.ParseResults(post_guard[0:3])
        post_guard = pp.ParseResults(post_guard[3:])
        post_guard.insert(0,fusion)

    return post_guard

def parse_action(exp):
    return actionExp.parseString(exp)[0]

def isInt(str):

    try:
        integer.parseString(str)
        return True
    except:
        return False




'''

def printTree(tree, it=0):

    for e in tree:

        if isinstance(e,str):
            print(it*" . "+ e)
        else:
            printTree(e,it=it+1)


tree = parse_guard("(x==1 & y==2)&(x==2 & y==1)|(x==0 & y==0)|(x==0 & y==0)")

printTree(tree)
print(len(tree[0][0][0][0][0][0]))


test = "((y == 1 &  x == 1)  & ((-1 <= h11 - h21)  &  (h11 - h21 <= 1))) | ((y == 1 &  x == 2)  & ((-1 <= h12 - h22)  &  (h12 - h22 <= 1)))"
test2 = "(y == 1 &  x == 1)"
test3 = "((y == 0 & x == 0) & (0 == h11)) |  ((y == 1 & x == 2) & (h12 == h11)) | ((y == 2 & x == 1) & (h21 == h11))"
test4 = "-1 <= h21"

tree = parse_guard(test4)


#printTree(tree)
#print(tree)
'''