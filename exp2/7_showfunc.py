# Display all the functions in a pTree

import json
import sys
import ultraimport
tree = ultraimport('__dir__/../utils/tree.py')
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
# conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('1000-pTs')
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('library Version pTrees')


def display_func(libname):

    INPUT_TABLE = f'{libname}_version'

    try:
        res = conn.fetchall(f"SELECT `pTree`, `version`, `size` FROM `{INPUT_TABLE}`;")
    except:
        # logger.warning(f'Library {libname} doesn\'t have pTrees information stored in the database. Skipped.')
        return None

    # Read pTree from dataset
    entry = res[len(res) - 1]
    logger.debug(f'Display all the functions in {libname} ({entry[1]}). Containing {entry[2]} vertices in total.')

    T = tree.LabeledTree(None, str(entry[1]))
    T.fromjson(json.loads(entry[0]))
    func_num = T.func_num(logger)
    logger.debug(f'{func_num} functions found.')


def diffAll():
    # Iterate through all libraries with information under the static/libs_data folder
    pass

if __name__ == '__main__':
    # Usage: > python3 7_showfunc.py <lib name>

    if len(sys.argv) > 1:
        display_func(sys.argv[1])
    else:
        diffAll()
    logger.close()
    conn.close()