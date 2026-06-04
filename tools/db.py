import sqlite3


class Database:
    def __init__(self, database: str, query: bool = False):
        self.database = database
        self.query = query

    @staticmethod
    def dict_factory(cur, row):
        fields = [column[0] for column in cur.description]
        return {key: value for key, value in zip(fields, row)}

    def fetchall(self, table: str, columns: list[str], where: str = None, distinct: bool = False):
        columns_joined = ", ".join(columns)
        where_ = f"WHERE {where}" if where else ''
        distinct_ = "DISTINCT" if distinct else ''

        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.row_factory = self.dict_factory
            query = f"SELECT {distinct_} {columns_joined} FROM {table} {where_}"

            if self.query:
                print("QUERY:", query.strip())

            cursor.execute(query)
            return cursor.fetchall()

    def insert(self, table: str, values: list):
        keys = values[0].keys()
        columns = ", ".join(keys)
        placeholders = ", ".join([f":{key}" for key in keys])

        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            stmt = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            if self.query:
                print("QUERY:", stmt.strip())

            cursor.executemany(stmt, values)
            conn.commit()

    def update(self, table: str, values: list[dict], columns_update: list, unique: str = None):
        placeholders = ", ".join([f"{key} = :{key}" for key in columns_update])
        where_ = f"WHERE {unique} = :{unique}" if unique else ''

        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            stmt = f"UPDATE {table} SET {placeholders} {where_}"

            if self.query:
                print("QUERY:", stmt.strip())

            cursor.executemany(stmt, values)
            conn.commit()

    def execute(self, query, dictitems=None):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.row_factory = self.dict_factory
            if dictitems:
                cursor.execute(query, dictitems)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def create_table(self, table, columns_types):
        columns = []
        for column_name, value in columns_types.items():
            if "id" != column_name:
                column_type = 'TEXT'
                if int == value:
                    column_type = 'INTEGER'
                columns.append(f'\"{column_name}\"  {column_type}')
        columns = ','.join(columns)
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.executescript(f"""
                CREATE TABLE IF NOT EXISTS "{table}" (
                    "id"	INTEGER NOT NULL,
                    {columns},
                    PRIMARY KEY("id" AUTOINCREMENT)
                );
            """)
            conn.commit()