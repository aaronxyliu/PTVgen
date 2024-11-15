import MySQLdb
from dotenv import load_dotenv
load_dotenv()
import os

class ConnDatabase:
    def __init__(self, database_name: str):
        if os.getenv("DB_HOST") == None:
            print('Please add database information in the .env file.')
            exit()
        self.connection = MySQLdb.connect(
            host= os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            passwd= os.getenv("DB_PASSWORD"),
            db= database_name,
            autocommit = True
        )
        self.database_name = database_name
        self.cursor = self.connection.cursor()
    

    def close(self):
        self.connection.close()
    

    def create_if_not_exist(self, table_name: str, statement: str):
        self.execute(f'''CREATE TABLE IF NOT EXISTS `{table_name}` ({statement});''')
    

    def create_new_table(self, table_name: str, statement: str):
        # Drop table if exists
        self.drop(table_name)
        self.execute(f'''CREATE TABLE `{table_name}` ({statement});''')
    

    def drop(self, table_name: str):
        self.execute(f'DROP TABLE IF EXISTS `{table_name}`;')
    

    def entry_count(self, table_name: str) -> int:
        return self.fetchone(f'SELECT COUNT(*) FROM `{table_name}`;')[0]


    def show_tables(self) -> list:
        # Return all the table names in the current database
        table_name_list = []
        res = self.fetchall("Show tables;")
        for entry in res:
            table_name_list.append(entry[0])
        return table_name_list
    

    def show_columns(self, table_name: str) -> list:
        res = self.fetchall(f'''SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name}';''')
        column_name_list = []
        for entry in res:
            column_name_list.append(entry[0])
        return column_name_list
        
        
    def insert(self, table_name: str, fields: list, values: tuple):
        if len(fields) == 0:
            return
        if len(fields) != len(values):
            print('[Warning] The number of fields and values are not equal.')
            return
        
        fields_str = "`, `".join(fields)
        placeholder_str = ", ".join(["%s"] * len(fields))
        sql = f"INSERT INTO `{table_name}` (`{fields_str}`) VALUES ({placeholder_str});"
        self.cursor.execute(sql, values)
        self.connection.commit()
    
    def update(self, table_name: str, fields: list, values: tuple, condition:str):
        if len(fields) == 0:
            return
        if len(fields) != len(values):
            print('[Warning] The number of fields and values are not equal.')
            return
        fields = map(lambda s: f"`{s}`=%s", fields)
        fields_str = ", ".join(fields)
        sql = f"UPDATE `{table_name}` SET {fields_str} WHERE {condition};"
        self.cursor.execute(sql, values)
        self.connection.commit()
    
    def update_otherwise_insert(self, table_name: str, fields: list, values: tuple, condition_field:str, condition_value:any):
        condition = f"`{condition_field}`='{condition_value}'"
        self.cursor.execute(f'''SELECT COUNT(*) FROM `{table_name}` WHERE {condition};''')
        satisfied_no = self.cursor.fetchone()[0]
        if satisfied_no == 0: 
            self.insert(table_name, fields + [condition_field], values + (condition_value,))
        else:
            self.update(table_name, fields, values, condition)
    

    def selectOne(self, table_name: str, fields: list, condition: str = None) -> list:
        if len(fields) == 0:
            return []
        fields_str = "`, `".join(fields)
        if condition:
            self.cursor.execute(f"SELECT `{fields_str}` FROM `{table_name}` WHERE {condition};")
        else:
            self.cursor.execute(f"SELECT `{fields_str}` FROM `{table_name}`;")
        res = self.cursor.fetchone()
        return res
 

    def selectAll(self, table_name: str, fields: list, condition: str = None, limit: int = -1, sortBy: str = None, descending:bool = False) -> list:
        if len(fields) == 0:
            return []
        fields_str = "`, `".join(fields)
        statement = f"SELECT `{fields_str}` FROM `{table_name}`"
        if condition:
            statement = f"{statement} WHERE `{condition}`"
        if sortBy:
            statement = f"{statement} ORDER BY `{sortBy}`"
            if descending:
                statement = f"{statement} DESC"
        if limit > 0:
            statement = f"{statement} LIMIT {limit}"
        res = self.fetchall(statement)
        return res
    

    def fetchone(self, cmd: str) -> tuple:
        self.cursor.execute(cmd)
        return self.cursor.fetchone()
    

    def fetchall(self, cmd: str) -> list:
        self.cursor.execute(cmd)
        return self.cursor.fetchall()
    

    def execute(self, cmd: str) -> None:
        self.cursor.execute(cmd)
        return self.connection.commit()
    

    def combine_tables(self, new_table, old_tables: list) -> None:
        # Combine several tables with the same columns into a new table
        if len(old_tables) == 0:
            return
        fields = self.show_columns(old_tables[0])
        fields.remove('id')
        fields_str = "`, `".join(fields)

        # Create a new table with all columns except id
        self.drop(new_table)
        self.execute(f"CREATE TABLE `{new_table}` AS SELECT `{fields_str}` FROM {old_tables[0]} WHERE 1!=1;")

        select_statements = []
        for old_table in old_tables:
            select_statements.append(f"SELECT `{fields_str}` FROM `{old_table}`")
        union_statement = ' UNION '.join(select_statements)
        self.execute(f'''INSERT INTO `{new_table}` SELECT * FROM ({union_statement}) a;''')
        