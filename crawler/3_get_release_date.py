import os
from urllib.request import Request, urlopen
from dotenv import load_dotenv
load_dotenv()
import json
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Libraries')
conn2 = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases')

LIB_TABLE = 'libs_cdnjs'

# Github API rate limit: 5000/hr
# Token generation: https://github.com/settings/tokens
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")



with open(f'extension/libraries.json', 'r') as openfile:
    libs = json.load(openfile)

for lib in libs:
    libname = lib["libname"]
    res = conn.fetchone(f"SELECT `github` FROM `{LIB_TABLE}` WHERE libname='{libname}';")
    if not res:
        continue
    github_url = res[0]
    if not github_url:
        logger.warning(f'{libname} is not found in dataset or its github url is emtpy.')
        continue

    conn2.create_new_table(libname, '''
        `id` int unsigned NOT NULL AUTO_INCREMENT,
        `tag_name` varchar(500) DEFAULT NULL,
        `name` varchar(500) DEFAULT NULL,
        `publish_date` date DEFAULT NULL,
        `url` varchar(500) DEFAULT NULL,
        PRIMARY KEY (`id`)
    ''')

    print(github_url)

    page_no = 1
    while(True):

        release_url = f'https://api.github.com/repos/{github_url[11:]}/releases?page={page_no}'
        
        req = Request(release_url)
        req.add_header('Authorization', f'token {GITHUB_TOKEN}')
        try:
            release_info_list = json.loads(urlopen(req).read())
        except KeyboardInterrupt:
            pass
        except:
            logger.warning(f"{release_url} is an invalid url. Or github token is outdated.")
            break

        if release_info_list and isinstance(release_info_list, list) and len(release_info_list) > 0:
            for release_info in release_info_list:
                if release_info:
                    conn2.insert(libname\
                                , ['tag_name', 'name', 'publish_date', 'url']\
                                , (release_info['tag_name'], release_info['name'], release_info['published_at'][:10],release_info['url']))
        else:
            break

        page_no += 1

conn.close()