### Web Library Version Detecting Experiment Set

### Requirement
Operating System: Linux or Mac  
Python 3

#### Preparation

0. (Optional) Create a Python virtual environment and activate it.
```shell
$ python3 -m venv .
$ source bin/activate
```

The command `deactivate` can be used if you want to quit current environment.
```shell
$ deactivate
```

1. Use the shell script to quickly install all required Python packages. (This script is only valid for Mac. For Linux users, please change "brew" to "apt" in the shell script)
```shell
$ chmod +x env.sh
$ ./env.sh
```

2. Download latest version Chrome and the matching version [Chromedriver](https://developer.chrome.com/docs/chromedriver). Put the Chromedriver under the `/bin` folder and name it "chromedriver".
3. Set up a local or remote ([PlanetScale](https://planetscale.com/) is free to use) database server. Then create two databases, named "Libraries" and "1000-pTs".
4. Create a `.env` file under the root folder to contain your Github token used for crawling, which can be obtained [here](https://github.com/settings/tokens). The connection information of the database created in step 2 should also be put here. The `.env` file format is as follows.
```
GITHUB_TOKEN=gtp_pxt68oJ3A8k6zaapxye9JIm2BEMUvt26xp21
DB_HOST=127.0.0.1
DB_USERNAME=root
DB_PASSWORD=12345678
```


#### Experiment Steps
1. Run `/crawler/1_get_libs_from_cdnjs.py` to crawl JS library information from [CDNJS](https://cdnjs.com).
2. Run `/crawler/2_get_version_files.py` to crawl JS lib version information from CDNJS, and the result will be stored into the `/static/libs_data` folder, which is used to host the local testing website.
3. (Optional) Run `/crawler/2.9_induce_deps.py` to induce dependency information for libraries. This will update the data stored in the `/static/libs_data` folder.
4. Run `app.py` to start the local testing website server. The website provides two basic routes: `test` and `deps`. The `test` routes will load the given library and dependencies, and the `deps` routes will only load all outer dependencies of this library. You need also assign the library name and version index in the url. Following shows an example.
```python
example url: 127.0.0.1:6543/test/jquery/12
# <6543>: port
# <test>: basic route
# <jquery>: library name, must match the file name in the "/static/libs_data" folder
# <12>: the 12th version
```
If you want to manually add library dependencies to the testing web page, url parameters are provided. Suppose that jQuery 3.7.1 and Underscore 1.13.6 is required, the following url can be used.

```url
http://127.0.0.1:6543/test/jquery/12?dep1=jquery/3.7.1/jquery.min.js&dep2=underscore.js/1.13.6/underscore-min.js'
```

The parameter content "jquery/3.7.1/jquery.min.js" will evaluate to the url "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js". So, make sure that the parameter content can be found on the CDNJS.

5. Run `/exp/3_gen_pTs.py` to aumatically generate pTree for all libraries. pTrees will be uploaded to the local database. Log information will be stored to `/log/gen_pTs` folder.
6. Run `/exp/4_mini_PTs.py` to minify the pTrees.
7. Run `/exp/5_freq_PTs.py` to find the maximum frequrent subtree for each library, and store all the data in a new table named `min_freq_subtree`. In the meantime, this program will also generate the file `/extension/libraries.json`, which is required for [our Chrome extension component](https://github.com/aaronxyliu/PTV).
8. If one library needs minimized pTree to identify the version, run `/extension/pt2json.py` to convert the pTree information from dataset into a json file. Then put this file into the `/data/versions/` folder of the PTV project. Don't forget to modify the `libraries.json` file to link this version file to the library.


#### File Structure
| Folder or File| Description|
|--|--|
| **crawler/**| Data collection scripts.|
| **data/** |   Collection results.|
| **exp/** |  Experiment scripts. |
| **log/** |   Experiment log.|
| **static/** |  Static resources used for the testing website. |
| **test/** |  Used for code functional testing. |
| **plot/** |  Scripts to draw paper plots. |
| **utils/** |  Useful utilities. |
| **app.py** |  Hosts a local server to load library, should be run before pTree generation. |
| **env.sh** |  Shell script to help build Python environment. |


#### Other

Library information is collected from the [cdnjs API](https://cdnjs.com/api).

Cooperation contacts aaronxyliu@gmail.com.
