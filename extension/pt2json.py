# Convert mpT table for each version from database to json file
import argparse

import MySQLdb
import re
import json
import ultraimport
logger = ultraimport('__dir__/../utils/logger.py').getLogger()

def connect_to_localdb():
    connection = MySQLdb.connect(
        host= '127.0.0.1',
        user='root',
        passwd= '12345678',
        db= '1000-pTs',
        autocommit = True
    )
    return connection

connection = connect_to_localdb()
cursor = connection.cursor()

def convert(libname, index_set):
    INPUT_TABLE = f'{libname}_version_m'

    # Check wehther the table exist
    query = f'''SELECT pTree, version, file_id, Sm, version_list FROM `{INPUT_TABLE}`'''
    cursor.execute(query)
    res = cursor.fetchall()

    # Read pTrees from dataset
    output_json = {}

    all_index_valid = True if len(index_set) == 0 else False
    for entry in res:
        if all_index_valid or int(entry[2]) in index_set:
            output_json[str(entry[2])] = {
                'pTree': json.loads(entry[0]),
                'version': str(entry[1]),
                'Sm': json.loads(entry[3]),
                'version_list': json.loads(entry[4])
            }        

    clean_libname = f'{libname}'.replace('.', '').replace('-', '')
    save_file = f'extension/output/{clean_libname}.json'
    with open(save_file, 'w') as f:
       json.dump(output_json, f)
    
    logger.info(f'Version file saved to the location: {save_file}.')


if __name__ == '__main__':
    # Usage: > python3 extension/pt2json.py -l <libname> start_id~end_id

    parser = argparse.ArgumentParser(
                    prog='pt2json.py',
                    description='Convert minimized pTree table for each version from the database to a json file')
    parser.add_argument('range_strs', metavar='R', type=str, nargs='*', 
                    help='''A range string. Corresponeding to the 'file_id' field in the database.
                            A prefix 'm' means discarding the following range.
                            The symbol '~' means range from one value to another value.
                            For example, <1 2 4~7 m5> refers to the array [1, 2, 4, 6, 7].''')
    parser.add_argument('--library', '-l', metavar='<lib>',help='the library name (required)', required=True)
    args = parser.parse_args()

    index_set = set()
    for range_str in args.range_strs:
        if re.match('m?[0-9]+$', range_str):
            # single
            if range_str[0] == 'm':
                index_set.discard(int(range_str[1:]))
            else:
                index_set.add(int(range_str))
        elif re.match('m?[0-9]+~[0-9]+$', range_str):
            # mutiple
            loc = range_str.find('~')
            if range_str[0] == 'm':
                start = int(range_str[1: loc])
                end = int(range_str[loc+1: ])
                for i in range(start, end + 1):
                    index_set.discard(i)
            else:
                start = int(range_str[0: loc])
                end = int(range_str[loc+1: ])
                for i in range(start, end + 1):
                    index_set.add(i)
        else:
            print(f'Invalid argument: {range_str}')
            exit(0)
    convert(args.library, index_set)

    connection.close()