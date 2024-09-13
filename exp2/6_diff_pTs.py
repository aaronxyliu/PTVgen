# Calculate the number difference functions between adjacent versions and save to a csv file

import json
import pandas as pd
import sys
import os
import ultraimport
tree = ultraimport('__dir__/../utils/tree.py')
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('1000-pTs')
# conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('library Version pTrees')


def diff_pTs(libname):

    INPUT_TABLE = f'{libname}_version'

    G = tree.Gamma()
    try:
        res = conn.fetchall(f"SELECT `pTree`, `version`, `size` FROM `{INPUT_TABLE}`;")
    except:
        # logger.warning(f'Library {libname} doesn\'t have pTrees information stored in the database. Skipped.')
        return None

    # Read pTrees from dataset
    size_sum = 0
    func_num_sum = 0
    for entry in res:
        size_sum += int(entry[2])
        T = tree.LabeledTree(None, str(entry[1]))
        T.fromjson(json.loads(entry[0]))
        func_num_sum += T.func_num()
        G.addt(T)

    ver_sum = len(G.trees)
    logger.info(f'{libname} ({ver_sum} versions)')

    diff_ver_cnt = 0
    for i in range(ver_sum-1):
        diffnum = G.trees[i].diffFunc(G.trees[i+1])
        if diffnum > 0:
            logger.debug(f'{diffnum} diffs from {G.trees[i].name} to {G.trees[i+1].name}.')
            diff_ver_cnt += 1
    logger.info(f'{libname} has {diff_ver_cnt} ({round(diff_ver_cnt * 100 / ver_sum, 1)}%) versions with diff.')
    return [diff_ver_cnt, ver_sum, round(diff_ver_cnt / ver_sum, 2), round(size_sum / ver_sum, 1), round(func_num_sum / ver_sum, 1)]


def diffAll():
    # Iterate through all libraries with information under the static/libs_data folder
    libfiles_list = os.listdir('static/libs_data')
    libfiles_list.sort()

    log = []

    for fname in libfiles_list:
        libname = fname[:-5]
        res = diff_pTs(libname)
        if res:
            log.append([libname] + res)

    df = pd.DataFrame(log, columns =['Library', '# Diff Versions', '# Versions', '% Diff Versions', 'avg. Version Size', 'avg. #Func']) 
    df.to_csv(f'log/diff_pTs.csv', index=True)

if __name__ == '__main__':
    # Usage: > python3 6_diff_pTs.py <lib name>

    if len(sys.argv) > 1:
        diff_pTs(sys.argv[1])
    else:
        diffAll()
    logger.close()
    conn.close()