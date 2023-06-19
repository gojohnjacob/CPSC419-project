import sqlite3
import sys
from contextlib import closing

DATABASE_FILE = '../cpsc490.db'

def delete_db_row(advisor_id):
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                query = f"DELETE FROM advisors WHERE advisor_id = ?"
                cursor.execute(query, [int(advisor_id)])
                conn.commit()
                return
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return

def get_advisor_details(advisor_id):
    ''''
    Establishes a connection with the SQLite DB and retrieves
    a list of all past advisees of a given advisor and their
    project info.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                data = []

                query2 = "SELECT project_id, student, title, abstract, homepage, \
                        semester, year \
                        FROM projects \
                        INNER JOIN terms \
                            ON projects.term_id = terms.term_id \
                        WHERE advisor_id = ? \
                        ORDER BY year DESC, semester DESC"
                cursor.execute(query2, [advisor_id])

                rows = cursor.fetchall()
                for row in rows:
                    item = {
                        "project_id": row[0],
                        "student": row[1],
                        "title": row[2],
                        "abstract": row[3],
                        "homepage": row[4],
                        "semester": row[5],
                        "year": row[6]
                    }
                    data.append(item)
                return data
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return {}

# if __name__ == "__main__":
    # delete_db_row("187")
    # delete_db_row("188")
    # delete_db_row("189")
    # delete_db_row("190")
    # print(get_advisor_details("8"))