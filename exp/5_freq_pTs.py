# Find the maximum frequrent subtree
import json
from functools import cmp_to_key
import sys
import os
import ultraimport
tree = ultraimport('__dir__/../utils/tree.py')
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('1000-pTs')


OUTPUT_TABLE = 'min_freq_subtree'

# Used for feature recommendation
PROP_NUMBER_LIMIT = 2
PROP_DEPTH_LIMIT = 2

output_json = []

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

def my_cmp(x, y):
    return -1 if x.subtree_size > y.subtree_size else 1

def freq_pTs(libname, mts):
    INPUT_TABLE = f'{libname}_version'
    G = tree.Gamma()

    try:
        res = conn.fetchall(f'''SELECT `pTree`, `version`, `size` FROM `{INPUT_TABLE}`;''')
    except:
        logger.warning(f'Library {libname} doesn\'t have pTrees information stored in the database. Skipped.')
        return None

    # Read pTrees from dataset
    for entry in res:
        version = str(entry[1])     
        if  entry[2] >= mts:  # Omit empty pTree
            T = tree.LabeledTree(None, version)
            T.fromjson(json.loads(entry[0]))
            G.addt(T)


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
        conn.insert(OUTPUT_TABLE,
            ['pTree', 'size', 'depth', 'libname', 'version range', 'feature'],
            (json.dumps(subtree.tojson()), subtree.size, subtree.depth, libname, subtree.name, json.dumps(feature))
        )
        logger.info(f'   Library {libname} ({subtree.name}) entry added to {OUTPUT_TABLE}.')

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
    # Create a new output table
    conn.create_new_table(OUTPUT_TABLE, '''
        `pTree` json DEFAULT NULL,
        `size` int DEFAULT NULL,
        `depth` int DEFAULT NULL,
        `libname` varchar(100) DEFAULT NULL,
        `version range` varchar(100) DEFAULT NULL,
        `feature` json DEFAULT NULL
    ''')
    logger.info(f'Create table {OUTPUT_TABLE} to store maximun frequent subtrees.')

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
    logger.close()
    conn.close()