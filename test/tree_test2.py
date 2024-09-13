# Test suite for the labeled tree algorithm

import ultraimport
tree = ultraimport('__dir__/../utils/tree.py')
Vertex = tree.Vertex
Gamma = tree.Gamma
LabeledTree = tree.LabeledTree


def create_vertices(n):
    v = []
    for i in range(n):
        v.append(Vertex(i, {'t': 6}))
    return v

def create_test_trees():
    G = Gamma()

    v = create_vertices(10)
    v[1].addc(v[2])
    v[2].addc(v[3])
    v[2].addc(v[4])
    v[2].addc(v[5])
    v[3].addc(v[6])
    v[3].addc(v[7])
    G.addt(LabeledTree(v[1], 'T0'))

    v = create_vertices(10)
    v[1].addc(v[2])
    v[2].addc(v[3])
    v[2].addc(v[4])
    v[2].addc(v[5])
    G.addt(LabeledTree(v[1], 'T1'))

    v = create_vertices(10)
    v[1].addc(v[2])
    v[2].addc(v[3])
    v[2].addc(v[4])
    v[2].addc(v[5])
    G.addt(LabeledTree(v[1], 'T2'))

    v = create_vertices(10)
    v[1].addc(v[2])
    v[1].addc(v[6])
    v[2].addc(v[3])
    v[2].addc(v[4])
    v[2].addc(v[5])
    G.addt(LabeledTree(v[1], 'T3'))

    return G




def test_suite1():
    # Test the different function calculation
    G = create_test_trees()
    print(G.trees[0].diffFunc(G.trees[1]))

    

if __name__ == '__main__':
    test_suite1()




