# Classes implemented according to the Version Detection paper
import time
import json

class Label:
    def __init__(self, _name):
        self.name = _name
        self.dict = {}


class Vertex:
    def __init__(self, name, label={}):
        assert(isinstance(label, dict))
        self.name = str(name)
        self.label = label
        self.children = []
    
    def addc(self, child):
        assert(isinstance(child, Vertex))
        self.children.append(child)

    def __eq__(self, x):
        if not x:
            return False
        assert(isinstance(x, Vertex))
        if self.name == x.name and self.label == x.label:
            return True
        else:
            return False 

class LabeledPath:
    def __init__(self, vertex_names, leaf_label):   # vertex_names - @List<str>
        self.vn = vertex_names[:]   # list copy
        self.label = leaf_label
    
    def __eq__(self, x):
        assert(isinstance(x, LabeledPath))
        if self.vn == x.vn and self.label == x.label:
            return True
        else:
            return False 

class LabeledTree:
    def __init__(self, root=None, name=''):
        self.root = root    # @Vertex
        self.name = name
    
    def __str__(self):
        return json.dumps(self.tojson(), indent=2)

    def get_metas(self):
        self.fpaths = []
        self.rpaths = []
        self.depth = 0
        self.size = 0
        if self.root:
            self.root.par = None
            self.root.depth = 0
            self.__get_metas__(self.root, 0, [self.root.name])

    def tojson(self):
        return self.__LT2Json__(self.root)
    
    def __LT2Json__(self, root, par_v=None):
        '''
        Convert the labeled tree back to JSON object

        Parameters:
            root - the root of the labeled tree
            par_v - parent vertex in JSON object type

        Output:
            root of the new tree in JSON object type
        '''
        if not root:
            return None
        assert(isinstance(root, Vertex))
        v_obj = {
            'n': root.name,
            'd': root.label,
            'c':[]
        }
        if par_v:
            par_v['c'].append(v_obj)
        for child in root.children:
            self.__LT2Json__(child, v_obj)
        return v_obj
    
    def fromjson(self, json_object: object) -> None:
        self.root = self.__Json2LT__(json_object)
    
    def __Json2LT__(self, root, par_v=None):
        '''
        Convert JSON object to the labeled tree data structure defined in tree.py

        Parameters:
            root - the root of the JSON tree
            par_v - parent vertex in "Vertex" type

        Output:
            root of the new tree in "Vertex"
        '''
        if not root:
            return None
        v = Vertex(root['n'], root['d'])
        if par_v:
            par_v.addc(v)
        for child in root['c']:
            self.__Json2LT__(child, v)
        return v

    
    def __eq__(self, x):
        assert(isinstance(x, LabeledTree))
        if not self.root or not x.root:
            print('Tree is missing.')
            return False
        q1 = []
        q2 = []
        q1.append(self.root)
        q2.append(x.root)
        if self.root != x.root:
            return False

        while len(q1):
            v1 = q1.pop(0)
            v2 = q2.pop(0)
            mask = [1] * len(v2.children)
            for c1 in v1.children:
                found_same_vertex = False
                for c2_i in range(len(v2.children)):
                    c2 = v2.children[c2_i]
                    if c1 == c2:
                        # print(f'x: {c1.name}')
                        mask[c2_i] = 0
                        found_same_vertex = True
                        q1.append(c1)
                        q2.append(c2)
                        break
                if not found_same_vertex:
                    return False
                
            for c2_i in range(len(v2.children)):
                if mask[c2_i] == 0:
                    continue
                c2 = v2.children[c2_i]
                found_same_vertex = False
                for c1 in v1.children:
                    if c1 == c2:
                        # print(f'y: {c1.name}')
                        mask[c2_i] = 0
                        found_same_vertex = True
                        q1.append(c1)
                        q2.append(c2)
                        break
                if not found_same_vertex:
                    return False
        return True

    def __sub__(self, treeB):
        """
        Generate the difference of current tree from treeB. (self - treeB)
        NOT FINISHED !!

        Parameters:
            treeB - another tree

        Returns:
            newtree - the subtraction result
        """
        # Return self - other
        if treeB == None:
            return self
        assert(isinstance(treeB, LabeledTree))
        if self.root == None or treeB.root == None:
            return self
        
        newtree = LabeledTree(Vertex(self.root.name))
        q1 = [self.root]
        q2 = [treeB.root]
        q3 = [newtree.root]
        while len(q2):
            v1 = q1.pop(0)
            v2 = q2.pop(0)
            v3 = q3.pop(0)
            for c2 in v2.children: 
                find_same_child = False
                for c1 in v1.children:
                    if c1 == c2:
                        find_same_child = True
                        new_v = Vertex(c1.name)
                        v3.addc(new_v)
                        q1.append(c1)
                        q2.append(c2)
                        q3.append(new_v)
                        newtree_size += 1
                        break
        return newtree
        
        
        diff_tree = {'name': 'window', 'dict': {}, 'children': []}
        q1 = []
        q2 = []
        q3 = []
        q1.append(tree1)
        q2.append(tree2)
        q3.append([])

        while len(q2): 
            node1 = q1.pop(0)
            node2 = q2.pop(0)
            path = q3.pop(0)

            for child_node2 in node2['children']:
                find_same_child = False

                for child_node1 in node1['children']:
                    if child_node1['name'] == child_node2['name']:
                        find_same_child = True
                        q1.append(child_node1)
                        q2.append(child_node2)
                        q3.append(path[:])
                        q3[len(q3) - 1].append(child_node1['name'])
                        break

                if not find_same_child:
                    child_node2['path'] = path[:]
                    diff_tree['children'].append(child_node2)
        
        return diff_tree
    
    def diffFunc(self, treeB: object) -> int:
        """
        Calculate the number of functions in self tree but not in tree B.

        Parameters:
            treeB - another tree

        Returns:
            diffnum - number of different functions
        """
        assert(isinstance(treeB, LabeledTree))
        if self.root == None:
            return 0
        if self.root != treeB.root:
            return self.__calFunc__(self.root, None)
        diffnum = 0
        q1 = [self.root]
        q2 = [treeB.root]
        while len(q1):
            v1 = q1.pop(0)
            v2 = q2.pop(0)
            for c1 in v1.children: 
                find_same_child = False
                for c2 in v2.children:
                    if c1 == c2:
                        q1.append(c1)
                        q2.append(c2)
                        find_same_child = True
                if not find_same_child:
                    diffnum += self.__calFunc__(c1, None)
        return diffnum
    
    def func_num(self, _logger) -> int:
        # Returen the function vertex number
        return self.__calFunc__(self.root, _logger)

    def __calFunc__(self, root: object, _logger: object) -> int:
        """
        Calculate the number of functions int the tree starting from root.

        Parameters:
            root - root of the tree
            logger - (optional) used to log out function paths

        Returns:
            funcnum - number of functions
        """
        assert(isinstance(root, Vertex))

        vertex_addr_dict = []

        funcnum = 0
        q = [root]
        q2 = [[root.name]]
        while len(q):
            v = q.pop(0)

            # Prevent vertices pointing to the same address
            repeat_vertex = False
            for old_v in vertex_addr_dict:
                if v == old_v:
                    repeat_vertex = True
                    break
            if repeat_vertex:
                continue
            vertex_addr_dict.append(v)

            path = q2.pop(0)
            if 't' in v.label and v.label["t"] == 6:
                funcnum += 1
                if _logger:
                    _logger.info(path)

            # Sort the children based on their names
            sorted_children = sorted(v.children, key=lambda x:x.name, reverse=False)
            for c in sorted_children:
                q.append(c)
                q2.append(path + [c.name])
        return funcnum



    def __get_metas__(self, par, d, p):
        """
        Generate meta informations for the tree, including tree size, full paths, 
        root paths, vertex depths, tree depth and vertices' parents.

        Parameters:
            par - parent vertex
            d - the depth of par
            p - the path of par (vertex name list)

        Returns:
            self.fpaths - full path set
            self.rpaths - root path set
            self.depth - tree depth
            self.size - vertex number of the tree
            <Vertex>.depth - the depth of each vertex
            <Vertex>.par - the parent of each vertex
            <Vertex>.subtree_size - the size of the subtree rooted from each vertex
        """
        if not par:
            return
        
        rpath = LabeledPath(p, par.label)
        self.rpaths.append(rpath)
        self.size += 1
        par.subtree_size = 1
        if len(par.children) == 0:
            # par is a leaf vertex, record this path
            fpath = LabeledPath(p, par.label)
            self.fpaths.append(fpath)
        else:
            if d + 1 > self.depth:
                self.depth = d + 1
            for c in par.children:
                c.depth = d + 1
                c.par = par
                par.subtree_size += self.__get_metas__(c, d + 1, p + [c.name])
        return par.subtree_size
        
    def min_cover_set(self, usize):
        """
        Find the minimum cover sets.

        Parameters:
            usize - the size of Gamma

        Returns:
            I - the indexes of sets in the collection that cover the universe
        """
        C = set()
        I = set()
        Omega_range = set(range(len(self.Omega)))
        while len(C) < usize - len(self.S):
            max_cover_size = -1
            max_i = -1
            for i in Omega_range - I:
                cover_size = len(C | self.Omega[i])
                if cover_size > max_cover_size:
                    max_cover_size = cover_size
                    max_i = i
            I.add(max_i)
            C |= self.Omega[max_i]
        return I

    def generate_minified_tree(self, I):
        """
        Generate the minified tree based on I.

        Parameters:
            I - index set returned from min_cover_set()

        Returns:
            mroot - the root of the minified tree
        """
        mroot = None
        for i in I:
            p = self.fpaths[i]
            assert(len(p.vn) >= 1)
            if not mroot:
                if len(p.vn) == 1:
                    mroot = Vertex(p.vn[0], p.label)
                else:
                    mroot = Vertex(p.vn[0])
            else:
                assert(mroot.name == p.vn[0])

            v = mroot
            for j in range(1, len(p.vn)):
                v_next = None
                for c in v.children:
                    if c.name == p.vn[j]:
                        v_next = c
                        break
                if not v_next:
                    if j == len(p.vn) - 1:
                        v_next = Vertex(p.vn[j], p.label)
                    else:
                        v_next = Vertex(p.vn[j])
                    v.children.append(v_next)

                v = v_next
        return mroot
    
    def intersect(self, treeB):
        """
        Generate the intersection of current tree and treeB. (Only consider vertex name identical)

        Parameters:
            treeB - another tree

        Returns:
            newtree - the intersection of two trees
            newtree_size - the size of newtree
        """
        assert(isinstance(treeB, LabeledTree))
        if self.root.name != treeB.root.name:
            # Return an empty tree
            return LabeledTree(), 0
        
        newtree = LabeledTree(Vertex(self.root.name))
        newtree_size = 1
        q1 = [self.root]
        q2 = [treeB.root]
        q3 = [newtree.root]
        while len(q1):
            v1 = q1.pop(0)
            v2 = q2.pop(0)
            v3 = q3.pop(0)
            for c1 in v1.children: 
                for c2 in v2.children:
                    if c1.name == c2.name:
                        new_v = Vertex(c1.name)
                        v3.addc(new_v)
                        q1.append(c1)
                        q2.append(c2)
                        q3.append(new_v)
                        newtree_size += 1
                        break
        return newtree, newtree_size

class Gamma:
    def __init__(self):
        self.trees = []    # @List<LabeledTree>

    def __str__(self) -> str:
        print_content = ''
        for i in range(len(self.trees)):
            print_content += self.trees[i].name + ':\n'
            print_content += self.trees[i].__str__() + '\n'
        return print_content
    
    def addt(self, t):
        assert(isinstance(t, LabeledTree))
        self.trees.append(t)
    
    def get_trees_metas(self):
        for t in self.trees:
            t.get_metas()
    
    def get_mtrees_metas(self):
        for t in self.mtrees:
            t.get_metas()

    def get_equivalence(self):
        """
        Generate the equivalence class for every tree in Gamma.
        Reference: Thesis: Sorting and Selection with Equality Comparisons. (2015) Theorem 1.

        Required:
            self.trees
            <LabeledTree>.fpaths

        Update:
            self.trees
        """
        T1 = time.time()
        r = 0
        eq = []    # eq[i] = {1, 3, 5} means 1, 3, 5 belong to a equivalence class
        n = len(self.trees)
        for i in range(n):
            eq.append({i})
        max_eq_size = 1
        neq = [set()] * n
        U = set(range(n))
        while True:
            r += 1
            for i in range(n):
                # Find the next j if any, starting from i + 1, wrapped around after n if necessary, such that j /∈ eq(i) ∪ neq(i).
                jRange = U - (eq[i] | neq[i])
                for j in jRange:
                    if self.trees[i] == self.trees[j]:
                        xRange = eq[i] | eq[j]
                        for x in xRange:
                            eq[x] = eq[i] | eq[j]
                            neq[x] = neq[i] | neq[j]
                            if len(eq[x]) > max_eq_size:
                                max_eq_size = len(eq[x])
                    else:
                        for x in eq[i]:
                            neq[x] = neq[x] | eq[j]
                        for y in eq[j]:
                            neq[y] = neq[y] | eq[i]
            if max_eq_size >= (n - 1) / r:
                break

        new_trees = []
        while len(U):
            i = U.pop()
            U -= eq[i]
            eq_list = sorted(list(eq[i]))
            new_name = ''
            sec_start = -1
            eq_name_list = []    # Equivalence Class Tree Names List

            for j in range(len(eq_list)):
                eq_name_list.append(self.trees[eq_list[j]].name)
                if sec_start == -1: 
                    # start a new section
                    sec_start = eq_list[j]
                    if j == 0:
                        new_name += self.trees[eq_list[j]].name
                    else:
                        new_name += ', ' + self.trees[eq_list[j]].name
                if j == len(eq_list) - 1 or eq_list[j+1] - eq_list[j] > 1:
                    # end the section
                    if eq_list[j] - sec_start == 1:
                        new_name += ', ' + self.trees[eq_list[j]].name
                    elif eq_list[j] - sec_start > 1:
                        new_name += ' ~ ' + self.trees[eq_list[j]].name
                    sec_start = -1

            self.trees[i].name = new_name
            self.trees[i].eq_name_list = eq_name_list

            new_trees.append(self.trees[i])
        self.trees = new_trees

        T2 = time.time()
        return [T2 - T1]


    def path_in_tree(self, fpath, tree):
        """
        Check whether fpath is a root path in tree. 

        Parameters:
            fpath - full path
            tree - <LabeledTree> 

        Return:
            True or False
        """
        
        assert(isinstance(fpath, LabeledPath))
        assert(isinstance(tree, LabeledTree))
        path_len = len(fpath.vn)
        assert(path_len > 0)

        v = tree.root
        if fpath.vn[0] != v.name:
            return False
        
        for i in range(1, path_len):
            found_child = False
            for c in v.children:
                if c.name == fpath.vn[i]:
                    v = c
                    found_child = True
                    break
            if not found_child:
                return False
            
        if v.label != fpath.label:
                return False
        return True




    def tree_size_reduction(self):
        """
        Tree size reduction. 

        Parameters:
            None

        Returns:
            <LabeledTree>.Omega - the path coloring collection for each tree
            <LabeledTree>.S - the supertree set of each tree
            time log - an array of time records for each stage in the algorithm
        """
        self.mtrees = []
        time_log = [0] * 4
        timestamp = [0] * 5
        for t in self.trees:
            # Generate the coloring set gamma for each path in t.
            timestamp[0] = time.time()
            t.Omega = []
            for i in range(len(t.fpaths)):
                p = t.fpaths[i]
                omega = set()  # the coloring set of p
                for j in range(len(self.trees)):
                    if self.path_in_tree(p, self.trees[j]):
                    # if p in self.trees[j].rpaths:
                        omega.add(j)
                t.Omega.append(omega)
            timestamp[1] = time.time()
            
            # Generate the supertree set of t.
            U = set(range(len(self.trees))) # Full set
            t.S = U.copy()
            for omega in t.Omega:
                t.S &= omega
            
            for i in range(len(t.Omega)):
                t.Omega[i] = U - t.Omega[i]
            timestamp[2] = time.time()

            # Find the minimum cover sets of the coloring collection
            I = t.min_cover_set(len(U))
            timestamp[3] = time.time()

            # Generate minified tree
            mtree = LabeledTree(t.generate_minified_tree(I), t.name)
            self.mtrees.append(mtree)
            timestamp[4] = time.time()
        
            # Record the time spent on each stage
            for i in range(len(time_log)):
                time_log[i] += timestamp[i + 1] - timestamp[i]
        
        return time_log
    
        
    def strict_supertree_set_minify(self):
        """
        Strict supertree set minify. 

        Required:
            <LabeledTree>.S - supertree set of each tree

        Returns:
            <LabeledTree>.Sm - minified strict supertree set of each tree
        """
        T1 = time.time()
        # Generate the equavalence class of each tree
        for i in range(len(self.trees)):
            t = self.trees[i]
        
            S_st = t.S - {i}
            t.Sm = set()
            while len(S_st):
                max_S = -1
                max_k = -1
                for k in S_st:
                    if len(self.trees[k].S) > max_S:
                        max_S = len(self.trees[k].S)
                        max_k = k
                S_st -= self.trees[max_k].S
                t.Sm.add(max_k)

        T2 = time.time()
        return [T2 - T1]
    
    def freq_subtree_mining(self, mts):
        """
        Calculate minimum frequent subtree set. 
        CAUTION: the size of all trees in self.trees should be no smaller than mts

        Required:
            mts - minimum tree size

        Returns:
            <LabeledTree>.Sm - minified strict supertree set of each tree
        """
        n = len(self.trees)
        if n == 0:
            return None
    
        freq_subtree_set = Gamma()
        
        # Calculate auxiliary array A[1..n]
        A = [0] * n
        for i in range(n):
            A[i] = n - 1
            newT = self.trees[i]
            for j in range(i+1, n):
                newT, newT_size = newT.intersect(self.trees[j])
                if newT_size < mts:
                    A[i] = j - 1
                    break

            # End the algorithm if the intersection of all trees meet our requirement
            if A[0] == n - 1:
                if n >= 2:
                    newT.name = f'{self.trees[0].name} ~ {self.trees[n-1].name}'
                freq_subtree_set.addt(newT)
                return freq_subtree_set

            
        B = [0] * (n + 1)   # Store the result of subproblem
        C = [0] * n     # Record the optimal selection for each subproblem
        LARGE_VAL = 1000000
        min_j = -1
        for i in range(n - 1, -1 ,-1):
            for j in range(i + 1, A[i] + 2):    
                # Find the smallest B[j]
                if B[j] < LARGE_VAL:
                    min_j = j
            assert(min_j > 0)
            B[i] = B[min_j] + 1
            C[i] = min_j

        # Generate the minimum frequent subtree set
        current = 0
        while current < n: 
            next = C[current]
            newT = self.trees[current]
            assert(next - current >= 1)
            
            for i in range(current + 1, next):
                newT, _ = newT.intersect(self.trees[i])
            if next - current > 1:
                newT.name = f'{self.trees[current].name} ~ {self.trees[next-1].name}'

            freq_subtree_set.addt(newT)
            current = next

        return freq_subtree_set

    

    def max_freq_subtree(self):
        """
        [Deprecated]
        Generate the maximum frequent subtree in Gamma.

        Required:
            self.trees

        Return:
            freqT - the maximum frequent subtree
        """

        n = len(self.trees)
        if n < 1:
            return None
        
        queues = [[]] * n
        for i in range(n):
            if  self.trees[i].root == None:
                return None
            queues[i].append(self.trees[i].root)
        
        freqT = LabeledTree(Vertex('window'), 'max freq subtree')
        queue_f = [freqT.root]

        while len(queues[0]):
            ptr_f = queue_f.pop(0)
            ptrs = [None] * n
            for i in range(n):
                ptrs[i] = queues[i].pop(0)

            for c in ptrs[0].children:
                # print(c.name)
                clist = self.__child_with_given_name(c.name, ptrs[1:])
                # print(clist)
                if None in clist:
                    # if one vertex doesn't have a child with the name same as the first tree's child
                    continue

                queues[0].append(c)
                for i in range(1, n):
                    queues[i].append(clist[i - 1])
                new_vertex = Vertex(c.name)
                queue_f.append(new_vertex)
                ptr_f.addc(new_vertex)

        return freqT



    def __child_with_given_name(self, name, vertex_list):
        """
        [Deprecated]
        Find the child of each vertex with the given name. If no such child, return None.

        Required:
            name <string>
            vertex_list = [v1, v2, ..., vn]

        Return:
            child_list = [ptr1, ptr2, ..., ptrn]
        """
        n = len(vertex_list)
        child_list = [None] * n
        for i in range(n):
            v = vertex_list[i]
            assert(v != None)
            for c in v.children:
                if c.name == name:
                    child_list[i] = c
                    break
        return child_list