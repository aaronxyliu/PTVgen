# Minify pTree size for each version

import json
import pandas as pd
import time
import sys
import os
import ultraimport
tree = ultraimport('__dir__/../utils/tree.py')
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('1000-pTs')
# conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('library Version pTrees')


def minify_pTs(libname):

    INPUT_TABLE = f'{libname}_version'
    OUTPUT_TABLE = f'{libname}_version_m'
    logger.info(libname)

    G = tree.Gamma()
    try:
        res = conn.fetchall(f"SELECT `pTree`, `version` FROM `{INPUT_TABLE}`;")
    except:
        logger.warning(f'Library {libname} doesn\'t have pTrees information stored in the database. Skipped.')
        return None

    # Read pTrees from dataset
    for entry in res:
        T = tree.LabeledTree(None, entry[1])   
        T.fromjson(json.loads(entry[0]))
        G.addt(T)
    
    if len(G.trees) == 0:
        return None

    T1 = time.time()    # Timer starts

    # Minification
    t1 = G.get_equivalence()
    G.get_trees_metas()

    logger.info('Get equivalence finished.')

    t2 = G.tree_size_reduction()
    G.get_mtrees_metas()

    logger.info('Tree size reduction finished.')

    # logger.info_S(G)

    t3 = G.strict_supertree_set_minify()
    T2 = time.time()    # Timer ends

    logger.info('Strict supertree set minification finished.')

    conn.create_new_table(OUTPUT_TABLE, '''
        `pTree` json DEFAULT NULL,
        `size` int DEFAULT NULL,
        `depth` int DEFAULT NULL,
        `version` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
        `file_id` int DEFAULT NULL,
        `Sm` json DEFAULT NULL,
        `version_list` json DEFAULT NULL
    ''')

    logger.info(f'Create table {OUTPUT_TABLE} to store minified pTrees.')

    # Save minified pTrees to dataset
    for i in range(len(G.trees)):
        assert(len(G.trees) == len(G.mtrees))
        mTree = G.mtrees[i]
        version = G.mtrees[i].name
        Sm = G.trees[i].Sm
        version_list = G.trees[i].eq_name_list

        conn.insert(OUTPUT_TABLE,
            ['pTree', 'size', 'depth', 'version', 'file_id', 'Sm', 'version_list'],
            (json.dumps(mTree.tojson()), G.mtrees[i].size, G.mtrees[i].depth, version, i, json.dumps(list(Sm)), json.dumps(version_list))
        )
        logger.info(f'   Version {version} entry added to {OUTPUT_TABLE}.')
    
    logger.info(f'Tree minification completed. Time spent: {(T2 - T1)} seconds.')
    return t1 + t2 + t3 + [T2 - T1]


def minifyAll():
    # Iterate through all libraries with information under the static/libs_data folder
    libfiles_list = os.listdir('static/libs_data')
    libfiles_list.sort()

    log = []
    # start = False

    for fname in libfiles_list:
        libname = fname[:-5]
        # if libname == 'jimp':
        #     start = True
        # if not start:
        #     continue
        res = minify_pTs(libname)
        if res:
            log.append([libname] + res)

    df = pd.DataFrame(log, columns =['Library', 'Equivalence', 'Path Record', 'Supertree Set', 'Min Cover Set', 'Get mT', 'Get Sm', 'Total']) 
    df.to_csv(f'log/mini_pTs.csv', index=True)

if __name__ == '__main__':
    # Usage: > python3 exp/4.mini_pTs.py <lib name>

    if len(sys.argv) > 1:
        minify_pTs(sys.argv[1])
    else:
        minifyAll()
    logger.close()
    conn.close()