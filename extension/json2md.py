import os
import json
import MySQLdb
import datetime


connection = MySQLdb.connect(
    host= '127.0.0.1',
    user='root',
    passwd= '12345678',
    db= 'Libraries',
    autocommit = True
)
cursor = connection.cursor()
LIB_TABLE = 'libs_cdnjs'
OUT_FILE = 'extension/LIBLIST.md'

def byStar(elem):
    return elem["star"]

with open(f'extension/libraries.json', 'r') as openfile:
    libs = json.load(openfile)


v_cnt = 0
version_cnt = 0
table = []
for lib in libs:
    if_v = False
    if 'function' in lib or "versionfile" in lib:
        v_cnt += 1
        if_v = True

    libname = lib["libname"]
    cursor.execute(f"SELECT `url`, `star`, `description`, `#versions` FROM `{LIB_TABLE}` WHERE libname='{libname}';")
    res = cursor.fetchone()
    if res:
        table.append({
            "libname": libname,
            "url": res[0],
            "star":  res[1],
            "description": res[2],
            "?version": if_v,
            "v_num": res[3]
        })
        version_cnt += res[3]
    else:
        table.append({
            "libname": libname,
            "url": None,
            "star":  0,
            "description": '',
            "?version": if_v,
            "v_num": None
        })

print(f'{len(libs)} libraries and {version_cnt} versions found.')
    
table.sort(key=byStar, reverse=True)    

time_str = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")

template = f'''
## Collected Library List

In total, there are {len(libs)} libraries collected by the tool. Among them, {v_cnt} are equipped with fine-grained version features.

Data update time: {time_str}

| Library | GitHub Star | Version Detection? | # Versions | Description |
| ------- | ----------- | -------- | ---------- | ----------- |
'''

writefile = open(OUT_FILE, 'w')
writefile.write(template)
writefile.close()

writefile2 = open(OUT_FILE, 'a')
for entry in table:
    if entry['url']:
        libname_str = f"[{entry['libname']}]({entry['url']})"
    else:
        libname_str = entry['libname']

    if entry['?version']:
        v_str = 'Y'
    else:
        v_str = 'N'

    star = entry['star']
    if not star:
        star_str = ''
    elif star >= 1000:
        star_str = f"{round(star/1000, 1)} k"
    else:
        star_str = str(star)

    if entry['v_num']:
        vnum_str = str(entry['v_num'])
    else:
        vnum_str = ''

    library_line = f"| {libname_str} | {star_str} | {v_str} | {vnum_str} | {entry['description'] or ''} |\n"
    writefile2.write(library_line)

writefile2.close()
print(f'The markdown file generated at the path {OUT_FILE}.')
