from sqlite3 import Cursor, connect, Row
from contextlib import closing
from html import escape

def execute_query(cursor: Cursor, stmt_str: str, parameter: tuple):
   
    if parameter is None:
        cursor.execute(stmt_str)
        data = cursor.fetchall()
    else:
        cursor.execute(stmt_str, parameter)
        data = cursor.fetchall()

    if not data:
        print("Database was queried but nothing was found")
        return ""
    
    return data

def build_query(parameter, year, advisor, semester):
    db_url = 'file:cpsc490.db?mode=ro'

    with connect(db_url, isolation_level=None, uri=True) as connection:
        connection.row_factory = Row

        with closing(connection.cursor()) as cursor:
            stmt_str = "SELECT DISTINCT projects.project_id, title, student, advisors_str \
                        FROM projects \
                        INNER JOIN projectsadvisors \
                            ON projects.project_id = projectsadvisors.project_id \
                        INNER JOIN advisors \
                            ON projectsadvisors.advisor_id = advisors.advisor_id \
                        NATURAL JOIN terms"
                        
            values = []
            filters = []

            if parameter != "":
                filters.append(" (student LIKE ? \
                                OR title LIKE ? OR advisors_str LIKE ?) ")

                values.append(parameter)
                values.append(parameter)
                values.append(parameter)

            if year.isdigit():
                filters.append(" year = ? ")
                values.append(year)
            
            if advisor.isdigit():
                filters.append("projects.project_id IN \
                                (SELECT project_id \
                                FROM projectsadvisors \
                                WHERE advisor_id = ?)")
                values.append(advisor)
            
            if semester != "":
                filters.append(" semester = ?")
                values.append(semester)

            stmt_str += (" WHERE " + " AND ".join(filters))
            stmt_str += "ORDER BY year DESC, semester DESC, title, student"

            return execute_query(cursor, stmt_str, tuple(values))

def load_all():
    db_url = 'file:cpsc490.db?mode=ro'

    with connect(db_url, isolation_level=None, uri=True) as connection:
        connection.row_factory = Row

        with closing(connection.cursor()) as cursor:
            stmt_str =  "SELECT DISTINCT projects.project_id, student, title, advisors_str, year, semester \
                        FROM projects \
                        INNER JOIN projectsadvisors \
                            ON projects.project_id = projectsadvisors.project_id \
                        INNER JOIN advisors \
                            ON projectsadvisors.advisor_id = advisors.advisor_id\
                        INNER JOIN terms \
                            ON projects.term_id = terms.term_id \
                        ORDER BY year DESC, semester DESC, title, student"
            
            response = execute_query(cursor, stmt_str, None)
            return response

def load_dropdowns():
    db_url = 'file:cpsc490.db?mode=ro'

    with connect(db_url, isolation_level=None, uri=True) as connection:
        connection.row_factory = Row

        with closing(connection.cursor()) as cursor:
            stmt_str =  "SELECT DISTINCT advisor, advisor_id FROM advisors ORDER BY advisor ASC"

            advisors = execute_query(cursor, stmt_str, None)

            stmt_str =  "SELECT DISTINCT year FROM terms ORDER BY year DESC"

            year = execute_query(cursor, stmt_str, None)

            stmt_str =  "SELECT DISTINCT semester FROM terms ORDER BY semester ASC"

            semester = execute_query(cursor, stmt_str, None)

            return advisors, year, semester

def handle_parameter(parameter, year, advisor, semester):

    if parameter.strip() != '':
        parameter = '%' + escape(parameter) + '%'

    return build_query(parameter, year, advisor, semester)
