import sqlite3

def find_term_id(cursor, semester, year):
    term_query = "SELECT term_id FROM terms WHERE semester = ? AND year = ?"
    cursor.execute(term_query, [semester, year])
    return cursor.fetchone()

def find_advisor_id(cursor, advisor):
    advisor_query = "SELECT advisor_id FROM advisors WHERE advisor = ?"
    cursor.execute(advisor_query, [advisor])
    return cursor.fetchone()

def insert_term(cursor, data):
    semester = data["semester"]
    year = data["year"]

    # only insert if it doesn't exist already
    if not find_term_id(cursor, semester, year):
        insert_term_query = "INSERT INTO terms (semester, year) VALUES(?, ?)"
        cursor.execute(insert_term_query, [semester, year])

        # check that the new term was added successfully
        assert find_term_id(cursor, semester, year)
    else:
        print("This term has been added already!")

def insert_advisor(cursor, data):
    advisor = data["advisor"]

    # only insert if it doesn't exist already
    if not find_advisor_id(cursor, advisor):
        insert_advisor_query = "INSERT INTO advisors (advisor) VALUES(?)"
        cursor.execute(insert_advisor_query, [advisor])

        # check that the new advisor was added successfully
        assert find_advisor_id(cursor, advisor)
        return 1
    else:
        # print("This advisor has been added already!")
        return 0

def find_project_id(cursor, student, semester, year):
    term_id = find_term_id(cursor, semester, year)[0]
    project_query = "SELECT project_id FROM projects WHERE student = ? \
        AND term_id = ?"
    cursor.execute(project_query, [student, term_id])
    return cursor.fetchone()

def insert_project(cursor, data):
    student = data["student"]
    title = data["title"]
    abstract = data["abstract"]
    homepage = data["homepage"]
    advisor = data["advisor"]
    semester = data["semester"]
    year = data["year"]

    if not find_project_id(cursor, student, semester, year):
        insert_project_query = "INSERT INTO projects (student, title, abstract, homepage, advisor_id, topic_id, term_id) \
            VALUES(?, ?, ?, ?, ?, ?, ?)"
        advisor_id = find_advisor_id(cursor, advisor)[0]
        term_id = find_term_id(cursor, semester, year)[0]
        cursor.execute(insert_project_query, [student, title, abstract, homepage, advisor_id, -1, term_id])

        # check that the new project was added successfully
        assert find_project_id(cursor, student, semester, year)
    else:
        print("A project with this student and semester has been added already!")

def insert_new_project(data):
    conn = sqlite3.connect('../cpsc490.db') 
    cursor = conn.cursor()

    # TO-DO: add support for topics table

    # insert new term if necessary
    insert_term(cursor, data)

    # # insert new advisor if necessary
    insert_advisor(cursor, data)

    # insert new project if necessary
    insert_project(cursor, data)
    conn.commit()

def delete_project(cursor, id):
    delete_project_query = "DELETE FROM projects WHERE project_id = ?"
    cursor.execute(delete_project_query, [id])

if __name__ == '__main__':
    abstract = "The expanding research into first-order logic capabilities in Natural Language Processing models is essential for the machines’ ability to understand human-created texts and to generate reasonably natural-sounding statements. First-order logic enables machines to understand references to groups of objects, references to people, and all other pro-form words in sentences. Despite the importance of first-order logic, there are surprisingly few resources available to train and evaluate models on this essential task. This research creates a dataset of first-order logic-based short “stories” along with classification and generation problems based on the texts. The dataset entries all isolate a first-order logic task of aggregation, subsumption, or unification. Each entry to the dataset includes both a classification question and a generation question based on the “story” to allow for flexibility in its use. The newly created dataset fills a need for a way to train and evaluate NLP models on first-order logic, something which was not found in previous background research. To demonstrate the dataset, it was tested in three popular NLP logic models, two of which answered the classification questions and one of which answered the generation questions. The models all performed overall poorly on all tasks, with the highest accuracy score in any category around 50%. Additionally, the research shows that all three models struggled most with the aggregation task, indicating where more focus needs to be placed in future training. This research will hopefully give a direction for further research into first-order logic and a means to train and evaluate future models."

    data = {
        "student": "Rachel Blumenthal",
        "title": "First-Order Logic-Based Dataset for Question-Answering and Classification Evaluation",
        "abstract": abstract,
        "homepage": "https://zoo.cs.yale.edu/classes/cs490/21-22a/blumenthal.rachel.rcb63/",
        "advisor": "Dragomir Radev",
        "semester": "Fall",
        "year": "2021"
    }
    insert_new_project(data)
