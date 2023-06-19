import sqlite3
import sys
from contextlib import closing

DATABASE_FILE = 'cpsc490.db'

def get_all_terms():
    '''
    Establishes a connection with the SQLite DB and retrieves
    all terms where senior projects have been submitted.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                query = "SELECT semester, year FROM terms ORDER BY year DESC"
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return []

def get_projects_by_term(semester, year):
    ''''
    Establishes a connection with the SQLite DB and retrieves
    all the project previews in a given semester and year.
    A project preview is composed of the student name, the title of
    the project, and the project advisor. Returns the results as a list
    of dictionaries that map the field to the value.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                query = "SELECT project_id, student, title \
                        FROM projects \
                        INNER JOIN terms \
                            ON projects.term_id = terms.term_id \
                        WHERE semester = ? AND year = ? ORDER BY title"
                cursor.execute(query, [semester, year])

                rows = cursor.fetchall()
                data = []
                for row in rows:
                    item = {
                        "id": row[0],
                        "student": row[1],
                        "title": row[2],
                        "advisor": [advisor[1] for advisor in get_project_advisors(row[0])]
                    }
                    data.append(item)

                return data
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return []

def get_projects():
    ''''
    Establishes a connection with the SQLite DB and retrieves
    all the project previews in a given semester and year.
    A project preview is composed of the student name, the title of
    the project, and the project advisor. Returns the results as a list
    of dictionaries that map the field to the value.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                query = "SELECT project_id, student, title \
                        FROM projects \
                        INNER JOIN terms \
                            ON projects.term_id = terms.term_id ORDER BY year DESC, semester DESC, title, student"
                cursor.execute(query)

                print(query)

                rows = cursor.fetchall()
                data = []
                for row in rows:
                    item = {
                        "id": row[0],
                        "student": row[1],
                        "title": row[2],
                        "advisor": [advisor[1] for advisor in get_project_advisors(row[0])]
                    }
                    data.append(item)

                return data
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return []

def get_advisors():
    ''''
    Establishes a connection with the SQLite DB and retrieves
    the list of all advisors.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                query = "SELECT * FROM advisors ORDER BY advisor"
                cursor.execute(query)

                rows = cursor.fetchall()
                data = []
                for row in rows:
                    item = {
                        "id": row[0],
                        "name": row[1],
                    }
                    data.append(item)

                return data
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return []

def get_project_details(project_id):
    ''''
    Establishes a connection with the SQLite DB and retrieves
    all the details for an individual project given the id.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                query = "SELECT student, title, abstract, \
                        homepage, semester, year, net_id \
                        FROM projects \
                        INNER JOIN terms \
                            ON projects.term_id = terms.term_id \
                        WHERE project_id = ?"
                cursor.execute(query, [project_id])

                row = cursor.fetchone()

                data = {
                    "student": row[0],
                    "title": row[1],
                    "abstract": row[2],
                    "homepage": row[3],
                    "semester": row[4],
                    "year": row[5],
                    "net_id": row[6],
                }

                advisors = get_project_advisors(project_id)

                if advisors:
                    data["advisor_info"] = [advisor for advisor in advisors]
                else:
                    data["advisor_info"] = None

                return data

    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return {}


def get_project_advisors(project_id):

    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:

                query = "SELECT advisors.advisor_id, advisor \
                        FROM advisors \
                        JOIN projectsadvisors \
                            ON projectsadvisors.advisor_id = advisors.advisor_id \
                        WHERE projectsadvisors.project_id = ? \
                        ORDER BY advisor"
                cursor.execute(query, [project_id])

                rows = cursor.fetchall()
                data = [item for item in rows]
                return data
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return []

def get_random_project():
    ''''
    Establishes a connection with the SQLite DB and retrieves
    a random project to be featured.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                query = "SELECT project_id, student, title \
                        FROM projects \
                        INNER JOIN terms \
                            ON projects.term_id = terms.term_id \
                        WHERE project_id IN (SELECT project_id FROM projects ORDER BY RANDOM() LIMIT 1)"
                cursor.execute(query)

                rows = cursor.fetchall()
                data = []
                for row in rows:
                    item = {
                        "id": row[0],
                        "student": row[1],
                        "title": row[2],
                        "advisor": [advisor[1] for advisor in get_project_advisors(row[0])]
                    }
                    data.append(item)

                return data
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return []

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

                query1 = "SELECT advisor FROM advisors WHERE advisor_id = ?"
                cursor.execute(query1, [advisor_id])
                name = cursor.fetchone()
                data.append({"advisor": name[0]})

                query2 = "SELECT projects.project_id, student, title, \
                        semester, year \
                        FROM projects \
                        JOIN projectsadvisors \
                            ON projects.project_id = projectsadvisors.project_id \
                        INNER JOIN terms \
                            ON projects.term_id = terms.term_id \
                        WHERE projectsadvisors.advisor_id = ? \
                        ORDER BY year DESC, semester DESC, title, student"
                cursor.execute(query2, [advisor_id])

                rows = cursor.fetchall()
                for row in rows:
                    item = {
                        "project_id": row[0],
                        "student": row[1],
                        "title": row[2],
                        "advisor": [advisor[1] for advisor in get_project_advisors(row[0])],
                        "semester": row[3],
                        "year": row[4]
                    }
                    data.append(item)
                return data
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return {}

def delete_project(project_id):
    '''
    Establishes a connection with the SQLite DB and deletes
    the particular project given the id.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                query = f"DELETE FROM projects WHERE project_id = ?"
                cursor.execute(query, [project_id])
                delete_project_advisors(cursor, project_id)
                conn.commit()
                return
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return

def find_term_id(cursor, semester, year):
    '''
    Helper function that checks if a term already exists in the DB.
    '''
    term_query = "SELECT term_id FROM terms WHERE semester = ? AND year = ?"
    cursor.execute(term_query, [semester, year])
    return cursor.fetchone()

def find_advisor_id(cursor, advisor):
    '''
    Helper function that checks if an advisor already exists in the DB.
    '''
    advisor_query = "SELECT advisor_id FROM advisors WHERE advisor = ?"
    cursor.execute(advisor_query, [advisor])
    return cursor.fetchone()

def insert_term(cursor, semester, year):
    '''
    Helper function that inserts a new term into the DB.
    '''

    # only insert if it doesn't exist already
    if not find_term_id(cursor, semester, year):
        insert_term_query = "INSERT INTO terms (semester, year) VALUES(?, ?)"
        cursor.execute(insert_term_query, [semester, year])

        # check that the new term was added successfully
        assert find_term_id(cursor, semester, year)
    else:
        print(f"{semester} {year} has already been added to the terms table!")

def insert_advisor(cursor, advisor_name):
    '''
    Helper function that inserts a new advisor into the DB.
    '''

    # only insert if it doesn't exist already
    if not find_advisor_id(cursor, advisor_name):
        insert_advisor_query = "INSERT INTO advisors (advisor) VALUES(?)"
        cursor.execute(insert_advisor_query, [advisor_name])

        # check that the new advisor was added successfully
        assert find_advisor_id(cursor, advisor_name)
    else:
        print(f"{advisor_name} has already been added to the advisors table!")

def insert_project_advisor(cursor, project_id, advisor_name):
    '''
    Helper function that inserts a new advisor for a project into the DB.
    '''

    advisor_id = find_advisor_id(cursor, advisor_name)
    if not advisor_id:
        print(f"{advisor_name} has not been added to the advisors table yet!")
    else:
        insert_project_advisor_query = "INSERT INTO projectsadvisors (project_id, advisor_id) VALUES(?, ?)"
        cursor.execute(insert_project_advisor_query, [project_id, advisor_id[0]])

def delete_project_advisors(cursor, project_id):
    '''
    Helper function that deletes all the advisors for a project in the DB.
    '''

    delete_query = "DELETE FROM projectsadvisors WHERE project_id = ?"
    cursor.execute(delete_query, [project_id])

def find_project_id(cursor, net_id, semester, year):
    '''
    Helper function that retrieves the project id associated
    with a particular NetID and term.
    '''
    term_id = find_term_id(cursor, semester, year)[0]
    project_query = "SELECT project_id FROM projects WHERE net_id = ? \
        AND term_id = ?"
    cursor.execute(project_query, [net_id, term_id])
    return cursor.fetchone()

def insert_project(cursor, data):
    '''
    Helper function that inserts a new project into the DB.
    '''
    student = data["student"]
    title = data["title"]
    abstract = data["abstract"]
    homepage = data["homepage"]
    advisors_data = data["advisor"].split(",")
    semester = data["semester"]
    year = data["year"]
    net_id = data["net_id"]

    found_project_data = find_project_id(cursor, net_id, semester, year)
    if not found_project_data:
        cleaned_advisor_list = [name.lstrip() for name in advisors_data]
        cleaned_advisor_list.sort()
        insert_project_query = "INSERT INTO projects (student, title, abstract, homepage, advisor_id, topic_id, term_id, net_id, advisors_str) \
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        term_id = find_term_id(cursor, semester, year)[0]
        cursor.execute(insert_project_query, [student, title, abstract, homepage, -1, -1, term_id, net_id, ", ".join(cleaned_advisor_list)])

        # check that the new project was added successfully
        assert find_project_id(cursor, net_id, semester, year)

        project_id = cursor.lastrowid

        # insert new advisor(s) if necessary
        for advisor_name in cleaned_advisor_list:
            insert_advisor(cursor, advisor_name)
            insert_project_advisor(cursor, project_id, advisor_name)

        return project_id
    else:
        print(f"A project with NetID {net_id} during the {semester} {year} term has already been added to the projects table!")
        return found_project_data[0]

def insert_new_project(data):
    '''
    Establishes a connection with the SQLite DB and inserts a
    new project along with a new term and advisor if necessary.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                # insert new term if necessary
                insert_term(cursor, data["semester"], data["year"])

                # insert new project
                project_id = insert_project(cursor, data)

                conn.commit()
                return project_id
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return

def update_project(cursor, data, project_id):
    '''
    Helper function that updates a particular project in the DB
    given the id.
    '''
    student = data["student"]
    title = data["title"]
    abstract = data["abstract"]
    homepage = data["homepage"]
    advisors_data = data["advisor"].split(",")
    semester = data["semester"]
    year = data["year"]

    # delete existing advisor(s)
    delete_project_advisors(cursor, project_id)

    # insert new advisor(s)
    cleaned_advisor_list = [name.lstrip() for name in advisors_data]
    cleaned_advisor_list.sort()

    for advisor_name in cleaned_advisor_list:
        insert_advisor(cursor, advisor_name)
        insert_project_advisor(cursor, project_id, advisor_name)

    term_id = find_term_id(cursor, semester, year)[0]
    update_project_query = "UPDATE projects SET student = ?, \
                            title = ?, abstract = ?, \
                            homepage = ?, term_id = ?, advisors_str = ? \
                            WHERE project_id = ?"
    
    cursor.execute(update_project_query, [student, title, abstract, homepage, term_id, ", ".join(cleaned_advisor_list), project_id])

def update_existing_project(project_id, data):
    '''
    Establishes a connection with the SQLite DB and updates
    all the details for an individual project given the id.
    This function inserts a new term and advisor into the DB
    if necessary.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                # insert new term if necessary
                insert_term(cursor, data["semester"], data["year"])

                # update project
                project_id = update_project(cursor, data, project_id)

                conn.commit()
                return project_id
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return

def find_favorite(net_id, project_id):
    '''
    Establishes a connection with the SQLite DB and checks
    if the given user has favorited the project with the given
    id.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                favorites_query = "SELECT project_id FROM favorites WHERE net_id = ?"
                cursor.execute(favorites_query, [net_id])
                favorited_projects = set()
                for row in cursor.fetchall():
                    favorited_projects.add(str(row[0]))

                if project_id in favorited_projects:
                    return True

                return False
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return

def insert_favorite(cursor, data):
    '''
    Helper function that inserts a new favorite for a given
    project id and NetID.
    '''
    net_id = data['net_id']
    project_id = data['project_id']
    
    if not find_favorite(net_id, project_id):
        insert_favorite_query = "INSERT INTO favorites (net_id, project_id) \
            VALUES(?, ?)"
        cursor.execute(insert_favorite_query, [net_id, project_id])

        favorites_query = "SELECT project_id FROM favorites WHERE net_id = ?"
        cursor.execute(favorites_query, [net_id])
        favorited_projects = set()
        for row in cursor.fetchall():
            favorited_projects.add(str(row[0]))

        assert (project_id in favorited_projects)
    else:
        print("This favorite has been added already!")

def insert_new_favorite(data):
    '''
    Establishes a connection with the SQLite DB and inserts
    a new favorite for a given project id and NetID.
    id.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                conn = sqlite3.connect(DATABASE_FILE) 
                cursor = conn.cursor()

                insert_favorite(cursor, data)

                conn.commit()
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return

def delete_favorite(net_id, project_id):
    '''
    Establishes a connection with the SQLite DB and deletes
    an existing favorite for a given project id and NetID.
    id.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                query = f"DELETE FROM favorites WHERE project_id = ? AND net_id = ?"
                cursor.execute(query, [project_id, net_id])
                conn.commit()
                return
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return


def get_favorites(net_id):
    '''
    Establishes a connection with the SQLite DB and retrieves
    all favorites for a given NetID.
    '''
    try:
        with closing(sqlite3.connect(DATABASE_FILE)) as conn:
            with closing(conn.cursor()) as cursor:
                query = "SELECT project_id \
                        FROM favorites \
                        WHERE net_id = ?"
                cursor.execute(query, [net_id])

                data = [project[0] for project in cursor.fetchall()]

                return data
    except sqlite3.OperationalError as err:
        print(err, file=sys.stderr)
        return []
