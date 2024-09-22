### Induce dependencies for libraries

from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import text_to_be_present_in_element
import json
import os
import sys
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()


service = Service(executable_path="./bin/chromedriver")
driver = webdriver.Chrome()

DEPS = ['jquery/2.2.4/jquery.min.js', 'jquery/3.7.1/jquery.min.js', 'core-js/3.35.1/minified.js', 'underscore.js/1.13.6/underscore-min.js']
CDN_PREFIX = 'https://cdnjs.cloudflare.com/ajax/libs/'


def updateOne(libname, file_index, file_list):
    version = file_list[file_index]['version']
    # print(version)

    if 'success' in file_list[file_index] and file_list[file_index]['success'] == True:
        return True

    driver.get(f"http://127.0.0.1:6543/test/{libname}/{file_index}")

    try:
        WebDriverWait(driver, timeout=10).until(text_to_be_present_in_element((By.ID, "js-load"), 'All libraries are loaded!'))
    except KeyboardInterrupt:
        pass
    except: 
        logger.error('Web page error.')
        file_list[file_index]['success'] = False
        return True     # Continue iterating subsequent versions

    error_div = driver.find_element(By.ID, 'js-errors')
    if not error_div.text:
        file_list[file_index]['success'] = True
        logger.custom('NO DEP NEEDED', '')
        return True
    
    
    
    for dep in DEPS:
        driver.get(f"http://127.0.0.1:6543/test/{libname}/{file_index}?dep1={dep}")
        try:
            WebDriverWait(driver, timeout=10).until(text_to_be_present_in_element((By.ID, "js-load"), 'All libraries are loaded!'))
        except KeyboardInterrupt:
            pass
        except: 
            logger.error('Web page error.')
            file_list[file_index]['success'] = False
            return True     # Continue iterating subsequent versions
        error_div = driver.find_element(By.ID, 'js-errors')
        if not error_div.text:
            logger.custom('DEP FOUND', f'{libname}: {version} - {dep}')
            file_list[file_index]['out_deps'].append(f'{CDN_PREFIX}{dep}')  # Add dep to the file
            file_list[file_index]['success'] = True
            return True

    file_list[file_index]['success'] = False 
    logger.warning(f'  [Dep Not Found] {libname}: {version}')
    return False
        
    


def updateLibrary(libname, start_id=0):
    if not f'{libname}.json' in os.listdir('static/libs_data'):
        logger.error(f'library {libname} has no record in the static/libs_data directory.')
        return
    

    with open(f'static/libs_data/{libname}.json', 'r') as openfile:
        file_list = json.load(openfile)
    
    start = False
    for file_index in file_list:
        if int(file_index) >= start_id:
            start = True
        if not start:
            continue

        res = updateOne(libname, file_index, file_list)
        # if not res:
        #     # Don't continue if dep induce failed
        #     break
    
    with open(f'static/libs_data/{libname}.json', "w") as outfile:
        outfile.write(json.dumps(file_list))

def byFolderOrder(elem):
    return elem.lower()

def updateAll(startlib=None):
    # Iterate through all libraries with information under the static/libs_data folder
    libfiles_list = os.listdir('static/libs_data')
    libfiles_list.sort(key=byFolderOrder)

    cnt = 0
    start = True
    if startlib:
        start = False
    for fname in libfiles_list:
        libname = fname[:-5]
        if startlib and libname == startlib:
            start = True
        if not start:
            continue
        logger.debug(f'Start examing {cnt}: {libname}')
        updateLibrary(libname)
        cnt += 1

if __name__ == '__main__':
    # Usage: > python3 gen_pTs.py <lib name>
    if len(sys.argv) > 1:
        updateLibrary(sys.argv[1])
    else:
        updateAll()
    driver.close()
    logger.close()




