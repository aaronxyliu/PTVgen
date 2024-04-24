# Compare the result of different detectors on top 200 domains

import json
import ultraimport
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Web Experiment')

TABLE_NAME = 'Exp1'
res = conn.fetchall(f"SELECT `id`, `LDC`, `Wappalyzer`, `PTV` FROM `{TABLE_NAME}`;")


def Percent(a, b):
    return f'{round(100*a/b,2)}%'

def CountLibs(tool_index):
    lib_cnt = 0
    for entry in res:
        libs = json.loads(entry[tool_index])
        lib_cnt += len(libs)
        for lib_entry in libs:
            if lib_entry['libname'] == 'jquery':
                print(lib_entry['version'])
    return lib_cnt

def CalculatePopularity(tool_index):
    Pop_dict = {}    # Popularity dictionary: libname-count
    for entry in res:
        libs = json.loads(entry[tool_index])
        for lib in libs:
            libname = lib['libname']
            if libname in Pop_dict:
                Pop_dict[libname] += 1
            else:
                Pop_dict[libname] = 1
    Pop_dict = dict(sorted(Pop_dict.items(), key=lambda x:x[1], reverse=True))
    print(f'Find {len(Pop_dict)} libraries.')

    rank = 1
    for name, count in Pop_dict.items():
        print(f'No. {rank}  {count}  {name}')
        rank += 1

def Compare(tool_index1, tool_index2):

    cnt = [0] * 5
    # cnt[0]: consistent
    # cnt[1]: tool1 is more precise than tool2
    # cnt[2]: tool1 is less precise than tool2
    # cnt[3]: inconsistent
    # cnt[4]: otherwise

    for entry in res:
        id = entry[0]
        result1 = json.loads(entry[tool_index1])
        result2 = json.loads(entry[tool_index2])

        for lib_entry1 in result1:
            libname = lib_entry1['libname']
            category = 4
            for lib_entry2 in result2:
                if lib_entry2['libname'] == libname:
                    set1 = set(lib_entry1['version'])
                    set2 = set(lib_entry2['version'])
                    if set1 == set2:
                        category = min(category, 0)
                        break
                    elif len(set2) == 0:
                        category = min(category, 1)
                    elif len(set1) == 0:
                        category = min(category, 2)
                    elif set1.issubset(set2):
                        category = min(category, 1)
                    elif set1.issuperset(set2):
                        category = min(category, 2)
                    elif len(set1.intersection(set2)) == 0:
                        category = min(category, 3)
                    else:
                        category = min(category, 4)
            cnt[category] += 1

    cnt_all = sum(cnt)
    print(f'consistent: {cnt[0]} ({Percent(cnt[0], cnt_all)})')
    print(f'more precise: {cnt[1]} ({Percent(cnt[1], cnt_all)})')
    print(f'less precise: {cnt[2]} ({Percent(cnt[2], cnt_all)})')
    print(f'inconsistent: {cnt[3]} ({Percent(cnt[3], cnt_all)})')
    print(f'otherwise: {cnt[4]} ({Percent(cnt[4], cnt_all)})')

if __name__ == '__main__':
    CountLibs(3)
    # Compare(2,3)
    # print(f'Tool1 libs: {CountLibs(2)}')
    # print(f'Tool2 libs: {CountLibs(3)}')
