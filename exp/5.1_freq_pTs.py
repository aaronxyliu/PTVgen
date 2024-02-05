# Find the maximum frequrent subtree
import json
from database_conn import connect_to_localdb
from functools import cmp_to_key
import sys
import os
import ultraimport
tree = ultraimport('__dir__/../utils/tree.py')

connection = connect_to_localdb('1000-pTs')
cursor = connection.cursor()

OUTPUT_TABLE = 'min_freq_subtree'

# Used for feature recommendation
PROP_NUMBER_LIMIT = 2
PROP_DEPTH_LIMIT = 2

output_json = []


def Json2LT(root, par_v=None):
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
    v = tree.Vertex(root['n'], root['d'])
    if par_v:
        par_v.addc(v)
    for child in root['c']:
        Json2LT(child, v)
    return v


def LT2Json(root, par_v=None):
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
    assert(isinstance(root, tree.Vertex))
    v_obj = {
        'n': root.name,
        'd': root.label,
        'c':[]
    }
    if par_v:
        par_v['c'].append(v_obj)
    for child in root.children:
        LT2Json(child, v_obj)
    return v_obj


def my_cmp(x, y):
    return -1 if x.subtree_size > y.subtree_size else 1

def recommend_properties_itr(vertex, number, depth, p_list):
    # Depth-first tree traversal
    children = vertex.children
    if len(children) == 0 or vertex.depth >= depth:
        # Leaf vertex
        if len(p_list) >= number:
            return
        path = []
        while vertex != None:
            path.insert(0, vertex.name) # Insert in the front of list
            vertex = vertex.par
        p_list.append(path[1:]) # Don't contain the root – 'window'
    else:
        children.sort(key=cmp_to_key(my_cmp))   # Sort from large subtree size to small
        for child in children:
            recommend_properties_itr(child, number, depth, p_list)

def recommend_properties(ptree, number, depth):
    """
    Recommend several properties to represent the pTree. 
    The properties will be selected according to the subtree size ranking.

    Parameters:
        ptree - a LabeledTree instance
        number - recommend number of properties
        p - recommend depth of properties

    Returns:
        p_list - a list of properties, i.e., [["core", "version"],["core", "add"]].
    """
    p_list = [] 
    ptree.get_metas()
    recommend_properties_itr(ptree.root, number, depth, p_list)
    return p_list



def freq_pTs(libname, mts):
    INPUT_TABLE = f'{libname}_version'


    # Check wehther the table exist
    # query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{INPUT_TABLE}'"
    # cursor.execute(query)
    # if cursor.fetchone()[0] != 1:
    #     print(f'Library {libname} doesn\'t have pTrees information stored in the database. Skipped.')
    #     return None

    G = tree.Gamma()

    try:
        cursor.execute(f"SELECT `pTree`, `version`, `size` FROM `{INPUT_TABLE}`;")
        res = cursor.fetchall()
    except:
        print(f'Library {libname} doesn\'t have pTrees information stored in the database. Skipped.')
        return None

    # Read pTrees from dataset
    for entry in res:
        version = str(entry[1])
        
        if  entry[2] >= mts:  # Omit empty pTree
            pTree = Json2LT(json.loads(entry[0]))
            G.addt(tree.LabeledTree(pTree, version))


    if len(G.trees) == 0:
        with open(f'log/freq_failed_libs.log', "a") as logfile:
            logfile.write(f'{libname}\n')
        return

    # Generate the minimum frequent subtree
    min_freq_subtrees = G.freq_subtree_mining(mts)

    # Save to dataset
    features = []
    for subtree in min_freq_subtrees.trees:
        feature = recommend_properties(subtree, PROP_NUMBER_LIMIT, PROP_DEPTH_LIMIT)
        features.append(feature)
        sql = f'''INSERT INTO `{OUTPUT_TABLE}` 
            (pTree, size, depth, libname, `version range`, `feature`) 
            VALUES (%s, %s, %s, %s, %s, %s);'''
        val = (json.dumps(LT2Json(subtree.root)), subtree.size, subtree.depth, libname, subtree.name, json.dumps(feature))
        cursor.execute(sql, val)
        connection.commit()
        print(f'   Library {libname} ({subtree.name}) entry added to {OUTPUT_TABLE}.')
        # print(str(feature_properties).replace('\'','"'))
        # print('')

    # Ouput to file
    clean_libname = libname.replace('.', '').replace('-', '')
    lib_item = {
        "libname": libname,
        "url": f"https://cdnjs.com/libraries/{libname}",
        "function": f"test_{clean_libname}",
        "versionfile": f"{clean_libname}.json"
    }
    for i in range(len(features)):
        lib_item[f'feature{i+1}'] = features[i]
    output_json.append(lib_item)

    
    
    


def freqAll(mts):
    # Drop table if exists
    cursor.execute(f'DROP TABLE IF EXISTS `{OUTPUT_TABLE}`;')
    connection.commit()

    # Create a new output table
    cursor.execute(f'''CREATE TABLE `{OUTPUT_TABLE}` (
        `pTree` json DEFAULT NULL,
        `size` int DEFAULT NULL,
        `depth` int DEFAULT NULL,
        `libname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
        `version range` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
        `feature` json DEFAULT NULL
        );''')
    connection.commit()
    print(f'Create table {OUTPUT_TABLE} to store maximun frequent subtrees.')

    # Clear log file
    with open(f'log/freq_failed_libs.log', "w") as logfile:
            logfile.write('')

    # Iterate through all libraries with information under the static/libs_data folder
    libfiles_list = os.listdir('static/libs_data')
    libfiles_list.sort()

    for fname in libfiles_list:
        libname = fname[:-5]
        freq_pTs(libname, mts)
    
    with open(f'extension/libraries.json', 'w') as f:
       json.dump(output_json, f, indent=4)
        

if __name__ == '__main__':
    # Usage: > python3 freq_pTs.py <lib name> <mts> 
    # Minimum tree size is set as 4 by default

    if len(sys.argv) == 2:
        freq_pTs(sys.argv[1], 4)
    elif len(sys.argv) == 3:
        freq_pTs(sys.argv[1], sys.argv[2])
    else:
        freqAll(4)
    connection.close()