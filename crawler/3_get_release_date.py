import os
from urllib.request import Request, urlopen
from dotenv import load_dotenv
load_dotenv()
import json
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases')
import sys

LIB_TABLE = 'libs_cdnjs'

BY_TAG_FLAG = True       # Crawl by the github tag page takes more time



def readurl(url:str) -> object:
    # Github API rate limit: 5000/hr
    # Token generation: https://github.com/settings/tokens
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

    req = Request(url)
    req.add_header('Authorization', f'token {GITHUB_TOKEN}')
    res = None
    try:
        res = json.loads(urlopen(req).read())
    except KeyboardInterrupt:
        pass
    except:
        logger.warning(f"{url} is an invalid url. Or github token is outdated.")
    return res

def crawlByRelease(libname, github_direct=None):
    if not github_direct:
        res = conn.fetchone(f"SELECT `github` FROM `{LIB_TABLE}` WHERE libname='{libname}';")
        if not res:
            logger.warning(f'{libname} is not found in the table {LIB_TABLE}. Skip.')
            return
        github_url = res[0]
        if not github_url:
            logger.warning(f'{libname} has an empty github url. Skip.')
            return
        github_direct = github_url[11:]

    conn2.create_new_table(libname, '''
        `id` int unsigned NOT NULL AUTO_INCREMENT,
        `tag_name` varchar(500) DEFAULT NULL,
        `name` varchar(500) DEFAULT NULL,
        `publish_date` date DEFAULT NULL,
        `url` varchar(500) DEFAULT NULL,
        PRIMARY KEY (`id`)
    ''')

    release_no = 0
    page_no = 1
    while(True):

        release_url = f'https://api.github.com/repos/{github_direct}/releases?page={page_no}'
        logger.info(f'Reading the data from {release_url} ...')
        release_info_list = readurl(release_url)

        if release_info_list and isinstance(release_info_list, list) and len(release_info_list) > 0:
            for release_info in release_info_list:
                if release_info:
                    conn2.insert(libname\
                                , ['tag_name', 'name', 'publish_date', 'url']\
                                , (release_info['tag_name'], release_info['name'], release_info['published_at'][:10],release_info['url']))
                    release_no += 1
        else:
            break

        page_no += 1
    
    logger.info(f'{libname} finished. Release number: {release_no}.')
    return release_no

def crawlByTag(libname, github_direct=None):
    if not github_direct:
        res = conn.fetchone(f"SELECT `github` FROM `{LIB_TABLE}` WHERE libname='{libname}';")
        if not res:
            logger.warning(f'{libname} is not found in the table {LIB_TABLE}. Skip.')
            return
        github_url = res[0]
        if not github_url:
            logger.warning(f'{libname} has an empty github url. Skip.')
            return
        github_direct = github_url[11:]

    conn2.create_new_table(libname, '''
        `id` int unsigned NOT NULL AUTO_INCREMENT,
        `tag_name` varchar(500) DEFAULT NULL,
        `name` varchar(500) DEFAULT NULL,
        `publish_date` date DEFAULT NULL,
        `url` varchar(500) DEFAULT NULL,
        PRIMARY KEY (`id`)
    ''')

    page_no = 1
    tag_no = 0
    while(True):

        tag_url = f'https://api.github.com/repos/{github_direct}/tags?page={page_no}'
        logger.info(f'Reading the data from {tag_url} ...')

        tag_info_list = readurl(tag_url)

        if tag_info_list and isinstance(tag_info_list, list) and len(tag_info_list) > 0:
            for tag_info in tag_info_list:
                commit_url = None
                try:
                    commit_url = tag_info['commit']['url']
                except:
                    logger.warning('Github API miss element.')
                    continue

                commit_info = readurl(commit_url)
                if commit_info:
                    date = ''
                    try:
                        date = commit_info['commit']['author']['date']
                    except:
                        logger.warning('Github API miss element 2.')
                        continue
                    conn2.insert(libname\
                                , ['tag_name', 'name', 'publish_date', 'url']\
                                , (tag_info['name'], '', date[:10],commit_url))
                    tag_no += 1
                
        else:
            break

        page_no += 1
    
    logger.info(f'{libname} finished. Tag number: {tag_no}.')
    return tag_no

def crawlAll():

    existing_tables = conn2.show_tables()

    with open(f'extension/libraries.json', 'r') as openfile:
        libs = json.load(openfile)

    for i in range(len(libs)):
        lib = libs[i]
        libname = lib["libname"]
        if libname not in existing_tables:
            logger.info(f"({i} / {len(libs)}) {libname}")
            release_no = crawlByRelease(libname)
            if release_no == 0:
                # No release information
                tag_no = crawlByTag(libname)
                if tag_no == 0:
                    conn2.drop(libname)


if __name__ == '__main__':
    # Usage: > python3 crawler/3_get_release_date.py <lib name> <github direct>
    # Example: > python3 crawler/3_get_release_date.py next vercel/next.js
    #          > python3 crawler/3_get_release_date.py vue2 vuejs/vue
    #          > python3 crawler/3_get_release_date.py vue3 vuejs/core
    #          > python3 crawler/3_get_release_date.py boomerangjs akamai/boomerang
    #          > python3 crawler/3_get_release_date.py svelte simeydotme/svelte-range-slider-pips
    if len(sys.argv) == 1:
        crawlAll()
    elif len(sys.argv) == 2:
        if BY_TAG_FLAG:
            crawlByTag(sys.argv[1])
        else:
            crawlByRelease(sys.argv[1])
    else:
        if BY_TAG_FLAG:
            crawlByTag(sys.argv[1], sys.argv[2])
        else:
            crawlByRelease(sys.argv[1], sys.argv[2])
        
    conn.close()

