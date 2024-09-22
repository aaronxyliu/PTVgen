### Generate credit object trees

import json
import pandas as pd
import os
import sys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import text_to_be_present_in_element
from TreeCredit import CreditCalculator
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('1000-pTs')

LOG_FOLDER = 'log/gen_pTs'
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
    logger.info(f"Folder '{LOG_FOLDER}' created successfully.")

service = Service(executable_path="./bin/chromedriver")
driver = webdriver.Chrome()

MAX_DEPTH = 4
MAX_NODE = 1000

TRIM_DEPTH = MAX_DEPTH                                                                          
TRIM_NODE = MAX_NODE

BLACK_LIST = []     # Blacklist vertex name in the pTree


def generatePT(file_index, route):
    driver.get(f"http://127.0.0.1:6543/{route}/{file_index}")

    WebDriverWait(driver, timeout=10).until(text_to_be_present_in_element((By.ID, "js-load"), 'All libraries are loaded!'))

    error_div = driver.find_element(By.ID, 'js-errors')
    if error_div.text:
        # Failed to load the library
        logger.error(f'{file_index} >> {error_div.text}')
        return None, 0, 0, '', True
        

    driver.execute_script(f'createObjectTree({MAX_DEPTH}, {MAX_NODE}, true);')

    WebDriverWait(driver, timeout=20).until(text_to_be_present_in_element((By.ID, "obj-tree"), '{'))
    version = driver.find_element(By.ID, 'version').text
    tree_json = driver.find_element(By.ID, 'obj-tree').text
    tree = json.loads(tree_json)
    circle_num = int(driver.find_element(By.ID, 'circle-num').text)
    size = int(driver.find_element(By.ID, 'tree-size').text)
    # depth = int(driver.find_element(By.ID, 'tree-depth').text)

    # Remove Global Varabile in Blacklist
    del_index = []
    for i in range(len(tree['children'])):
        if tree['children'][i]['name'] in BLACK_LIST:
            del_index.append(i)
    offset = 0
    for index in del_index:
        del tree['children'][index - offset]
        offset += 1


    return tree, size, circle_num, version, False


def treeDiff(tree1, tree2):
    # Return tree2 - tree1
    if tree1 == None or tree2 == None:
        return None
    
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

def SameDict(d1, d2):
    for k, v in d1.items():
        if not k in d2:
            return False
        if d2[k] != v:
            return False
    return True

def elimRandom(tree1, tree2):
    # Eliminate random nodes - remove nodes that different in two trees.
    if tree1 == None or tree2 == None:
        return None
    ret_tree = {'name': 'window', 'dict': {}, 'children': []}
    elim_num = 0
    
    q1 = []
    q2 = []
    q3 = []
    q1.append(tree1)
    q2.append(tree2)
    q3.append(ret_tree)

    while len(q3): 
        node1 = q1.pop(0)
        node2 = q2.pop(0)
        node3 = q3.pop(0)

        for child_node1 in node1['children']:
            find_same = False
            for child_node2 in node2['children']:
                if child_node1['name'] == child_node2['name'] and SameDict(child_node1['dict'], child_node2['dict']):
                    # Identical nodes
                    find_same = True
                    q1.append(child_node1)
                    q2.append(child_node2)
                    new_node = {'name': child_node2['name'], 'dict': child_node1['dict'], 'children': []}
                    node3['children'].append(new_node)
                    q3.append(new_node)
                    break

            if not find_same:
                elim_num += 1
    
    return ret_tree, elim_num

def limitGlobalV(tree, vlist):
    ret_tree = {'name': 'window', 'dict': {}, 'children': []}
    for child in tree['children']:
        if child['name'] in vlist:
            ret_tree['children'].append(child)
    return ret_tree
    


def updateOne(libname, file_index, limit_globalV=[]):
    pt1, size1, circle_num1, version, fail1 = generatePT(file_index, f'deps/{libname}')
    pt2, size2, circle_num2, _, fail2 = generatePT(file_index, f'test/{libname}')
    pt3, size3, circle_num3, _, fail3 = generatePT(file_index, f'test/{libname}')
    if fail1 or fail2 or fail3:
        return ['N', 'Library loading error.']

    if pt1 and pt2 and pt3:
        pt_stable, random_num = elimRandom(pt2, pt3)
        if limit_globalV != None and len(limit_globalV) > 0:
            pt_stable = limitGlobalV(pt_stable, limit_globalV)
        pt = treeDiff(pt1, pt_stable)

        # Trim the pTree
        CC = CreditCalculator(TRIM_DEPTH, TRIM_NODE, MAX_DEPTH)
        size, depth = CC.algorithm1(pt)
        pt = CC.expand(pt)
        CC.minifyTreeSpace(pt)

        # Add pt to SepTreeTABLE dataTABLE
        globalV = []
        for subtree in pt['c']:
            globalV.append(subtree['n'])
        

        # Create table if not exist
        SEP_TREE_TABLE = f'{libname}_version'
        conn.create_if_not_exist(SEP_TREE_TABLE, '''
            `pTree` json DEFAULT NULL,
            `globalV_num` int DEFAULT NULL,
            `globalV` json DEFAULT NULL,
            `size` int DEFAULT NULL,
            `circle_num` int DEFAULT NULL,
            `depth` int DEFAULT NULL,
            `file_id` bigint unsigned NOT NULL,
            `random_num` int DEFAULT NULL,
            `version` varchar(100) DEFAULT NULL,
            UNIQUE KEY `id` (`file_id`)
        ''')

        # If entry already exists, delete first
        res = conn.fetchone(f"SELECT size FROM `{SEP_TREE_TABLE}` WHERE file_id = '{file_index}';")
        if res:  
            conn.execute(f"DELETE FROM `{SEP_TREE_TABLE}` WHERE file_id = '{file_index}';")

        # Create new entry in SEP_TREE_TABLE
        conn.insert(SEP_TREE_TABLE\
            , ('pTree', 'size', 'depth', 'globalV', 'globalV_num', 'circle_num', 'file_id', 'random_num', 'version') \
            , (json.dumps(pt), size, depth, json.dumps(globalV), len(globalV), circle_num2 - circle_num1, int(file_index), random_num, str(version)))

        logger.info(f'    {file_index} entry added to `{SEP_TREE_TABLE}`.')
        return ['Y', '']
    


def updateLibrary(libname, start_id = 0):
    if not f'{libname}.json' in os.listdir('static/libs_data'):
        logger.warning(f'library {libname} has no record in the static/libs_data directory.')
        return

    with open(f'static/libs_data/{libname}.json', 'r') as openfile:
        file_list = json.load(openfile)
    

    log = []    # Store log information during the process
    start = False
    for file_index in file_list:
        if int(file_index) >= start_id:
            start = True
        if not start:
            continue

        version = file_list[file_index]['version']

        logger.info(f'  {file_index} {libname} {version}')

        try:
            res = updateOne(libname, file_index)
            log.append([version] + res)
        except KeyboardInterrupt:
            pass
        except Exception as error:
            # handle the exception
            logger.error(error)
            log.append([version, 'N', 'Unknown fault.'])
        
    df = pd.DataFrame(log, columns =['Version', 'Success', 'Description']) 
    df.to_csv(f'log/gen_pTs/{libname}.csv', index=True)


def updateAll():
    # Iterate through all libraries with information under the static/libs_data folder
    libfiles_list = os.listdir('static/libs_data')

    # Remove library already appeared in the old directory
    old_libfiles_list = os.listdir('static/old_libs_data')
    libfiles_list = [item for item in libfiles_list if item not in set(old_libfiles_list)]
    
    libfiles_list.sort()

    # Remove history log files under the log/gen_pTs folder
    log_files = os.listdir('log/gen_pTs')
    for f in log_files:
        os.remove(f'log/gen_pTs/{f}')

    for fname in libfiles_list:
        libname = fname[:-5]
        updateLibrary(libname)

if __name__ == '__main__':
    # Usage: > python3 gen_pTs.py <lib name>

    if len(sys.argv) > 1:
        updateLibrary(sys.argv[1])
    else:
        updateAll()
    driver.close()
    conn.close()




