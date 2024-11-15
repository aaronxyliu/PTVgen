import ultraimport
import json
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('1000-pTs')

LIB_NAME = 'aframe'
TABLE_NAME = f'{LIB_NAME}_version'
GLOABL_NAME_WHITELIST = ['AFRAME']

def truncate_pTs():


    try:
        res = conn.selectAll(TABLE_NAME, ['pTree', 'version'])
    except:
        logger.warning(f'Library {LIB_NAME} doesn\'t have pTrees information stored in the database. Skipped.')
        return None

    for entry in res:
        pTree = json.loads(entry[0])
        version = entry[1]
        if 'c' in pTree:
            new_children = []
            for child in pTree['c']:
                if child['n'] in GLOABL_NAME_WHITELIST:
                    new_children.append(child)
            pTree['c'] = new_children
        conn.update(TABLE_NAME, ['pTree'], (json.dumps(pTree),), f"`version`='{version}'")
    logger.info(f'pTrees truncated for {LIB_NAME}.')

truncate_pTs()