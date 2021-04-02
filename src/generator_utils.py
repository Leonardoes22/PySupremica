class GenEnc:

    def __init__(self, M, N):
        self.M = M
        self.N = N

    ###
    # String Encodings
    ##

    def coordEnc(self, i, j):
        return(str(i)+""+str(j))

    def placingEnc(self, i, j):
        placingEnc = "a"
        return placingEnc+self.coordEnc(i,j)

    def inEnc(self, i, j):
        return "in" + self.coordEnc(i,j)

    def outEnc(self, i, j):
        return "out" + self.coordEnc(i,j)

    def heightEnc(self, i, j):
        heightEnc = "h"
        return heightEnc + self.coordEnc(i,j)

    def altEnc(self):
        return "_r2"

    ###
    # Util Functions
    ###


    def inGrid(self, i,j):

        if i*j == 0:
            return False
        elif i > self.M or j > self.N:
            return False
        else:
            return True

    def getNeighbors(self, i, j, ext=False):

        neighborhood = [(i,j+1),(i-1,j),(i,j-1),(i+1,j)] 
        if ext:
            neighborhood += [(i+1,j+1),(i-1,j-1),(i+1,j-1),(i-1,j+1)]

        neigh = []
        for n in neighborhood:
            if (self.inGrid(n[0],n[1])):
                neigh.append(n)
        return neigh


