# Crawl all libraries and their Github star number from Cdnjs
# Remember to set the CRAWER_LIMIT and the Github token

from urllib.request import Request, urlopen
import json
import time
import os
from dotenv import load_dotenv
load_dotenv()
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')

# Github API rate limit: 5000/hr
# Token generation: https://github.com/settings/tokens
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
logger.info(f'The Github token is: {GITHUB_TOKEN}')

OUTPUT_TABLE = 'libs_cdnjs'
CRAWL_LIMIT = 5000
CRAWL_INTERVAL = 0.5    # sleep seconds between iterations

def get_star(lib_info):
    try:
        raw_url = lib_info['repository']['url']
    except:
        logger.warning(f'{libname} doesn\'t have repository information.')
        return 0, ''

    # Get star from Github API
    ptr = raw_url.find('github.com')
    if ptr == -1:
        logger.warning('Not a github domain.')
        return 0, ''

    # Remove ".git" suffix
    if raw_url[-4:] == '.git':
        raw_url = raw_url[:-4]
    if raw_url[-1] == '/':
        raw_url = raw_url[:-1]

    github_api_url = f'https://api.github.com/repos/{raw_url[ptr+11:]}'
    github_url = f'github.com/{raw_url[ptr+11:]}'
    
    req = Request(github_api_url)
    req.add_header('Authorization', f'token {GITHUB_TOKEN}')
    try:
        repo_info = json.loads(urlopen(req).read())
    except KeyboardInterrupt:
        pass
    except:
        logger.warning(f"{github_api_url} is an invalid url. Or github token is outdated.")
        return 0, github_url
    
    if repo_info['stargazers_count']:
        star = repo_info['stargazers_count']
        return int(star), github_url
    else:
        logger.warning('Failed to find the stargazers field.')
        return 0, github_url


if __name__ == '__main__':
    # Create databse table
    conn.create_if_not_exist(OUTPUT_TABLE, '''
        `libname` varchar(100) DEFAULT NULL,
        `url` varchar(500) DEFAULT NULL,
        `cdnjs` varchar(100) DEFAULT NULL,
        `star` int DEFAULT NULL,
        `description` varchar(10000) DEFAULT NULL,
        `#versions` int DEFAULT NULL,
        `latest version` varchar(100) DEFAULT NULL,
        `github` varchar(500) DEFAULT NULL
    ''')
    res = urlopen(f'https://api.cdnjs.com/libraries')
    lib_list = json.loads(res.read())['results']
    lib_num = len(lib_list)
    cnt = 0

    for lib_entry in lib_list:
        cnt += 1
        if cnt > CRAWL_LIMIT:
            break
        libname = lib_entry['name']
        cdnjs = f'https://cdnjs.com/libraries/{libname}'
        res = urlopen(f'https://api.cdnjs.com/libraries/{libname}')
        lib_info = json.loads(res.read())
        url = lib_info['homepage'] if 'homepage' in lib_info else None
        dscp = lib_info['description'] if 'description' in lib_info else None
        version_list = lib_info['versions']
        version_num = 0
        latest_version = None
        if version_list and len(version_list) > 1:
            version_num = len(lib_info['versions'])
            latest_version = lib_info['versions'][-1]
        star, github_url = get_star(lib_info)    
        conn.insert(OUTPUT_TABLE\
                    , ['libname', 'url', 'cdnjs', 'github', 'star', 'description', '#versions', 'latest version']\
                    , (libname, url, cdnjs, github_url, star, dscp, version_num, latest_version))
        logger.info(f'{libname} finished. ({cnt} / {lib_num})')
        time.sleep(CRAWL_INTERVAL)


    conn.close()
    logger.close()
