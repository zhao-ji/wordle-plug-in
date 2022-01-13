import sqlite3
from sqlite3 import Error

CREATE_TABLE = """
create table if not exists words (
    id integer primary key,
    word text not null unique,
    count integer not null
);
"""
INSERT_ROW = """
insert into words (word, count) values('{}', '{}');
"""


def create_database(db_name):
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        print("Sqlite3 version: {}".format(sqlite3.version))
    except Error as e:
        print(e)
    else:
        print("Database created successful!")
        conn.execute(CREATE_TABLE)
    finally:
        if conn:
            conn.close()


def import_data(db_name, file_name):
    conn = None
    try:
        conn = sqlite3.connect(db_name)
    except Error as e:
        print(e)
    else:
        with open(file_name) as f:
            for i in f:
                word = i.strip()
                print("Importing: {}...".format(i))
                conn.execute(INSERT_ROW.format(word, len(word)))
    finally:
        if conn:
            conn.commit()
            conn.close()
            print("Finished!")


if __name__ == "__main__":
    database_name = "google-words.db"
    data_file = "google-20k.txt"
    create_database(database_name)
    import_data(database_name, data_file)
