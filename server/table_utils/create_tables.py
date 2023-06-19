import sqlite3
import os

from insert_table_data import insert_advisor, find_advisor_id

cwd = os.path.split(os.getcwd())[1]

if cwd == "server":
    conn = sqlite3.connect('cpsc490.db')
elif cwd == "table_utils":
    conn = sqlite3.connect('../cpsc490.db')

cursor = conn.cursor()

# -----------------------------------------------------------------------
# Create Projects Table
# cursor.execute(
#     '''
#     CREATE TABLE IF NOT EXISTS projects
#     (
#         [project_id] INTEGER PRIMARY KEY,
#         [student] TEXT,
#         [title] TEXT,
#         [abstract] TEXT,
#         [homepage] TEXT,
#         [advisor_id] INTEGER,
#         [topic_id] INTEGER,
#         [term_id] INTEGER
#     )
#     '''
# )

# -----------------------------------------------------------------------
# Create Terms Table
# cursor.execute(
#     '''
#     CREATE TABLE IF NOT EXISTS terms
#     (
#         [term_id] INTEGER PRIMARY KEY,
#         [semester] TEXT,
#         [year] TEXT
#     )
#     '''
# )

# -----------------------------------------------------------------------
# Create Advisors Table
# cursor.execute(
#     '''
#     CREATE TABLE IF NOT EXISTS advisors
#     (
#         [advisor_id] INTEGER PRIMARY KEY,
#         [advisor] TEXT
#     )
#     '''
# )

# -----------------------------------------------------------------------
# Create Topics Table
# cursor.execute(
#     '''
#     CREATE TABLE IF NOT EXISTS topics
#     (
#         [topic_id] INTEGER PRIMARY KEY,
#         [topic] TEXT
#     )
#     '''
# )

# -----------------------------------------------------------------------
# Add net_id to Projects Table
# cursor.execute(
#     '''
#     ALTER TABLE projects ADD COLUMN net_id TEXT
#     '''
# )

# -----------------------------------------------------------------------
# Create Favorites Table
# cursor.execute(
#     '''
#     CREATE TABLE IF NOT EXISTS favorites
#     (
#         [favorite_id] INTEGER PRIMARY KEY,
#         [net_id] TEXT, 
#         [project_id] INTEGER
#     )
#     '''
# )

# -----------------------------------------------------------------------
# Create Projects-Advisors Table
# cursor.execute(
#     '''
#     CREATE TABLE IF NOT EXISTS projectsadvisors
#     (
#         [projectsadvisors_id] INTEGER PRIMARY KEY,
#         [project_id] INTEGER, 
#         [advisor_id] INTEGER
#     )
#     '''
# )

# -----------------------------------------------------------------------
# Populate Projects-Advisors Table
# update_advisor_query = "UPDATE advisors SET advisor = ? WHERE advisor_id = ?"
# cursor.execute(update_advisor_query, ["Avi Silberschatz, Robert Soulé", "194"])
# cursor.execute(update_advisor_query, ["Sekhar Tatikonda, Daniel Spielman", "221"])
# cursor.execute(update_advisor_query, ["Frederick Warner, Vladimir Rokhlin", "203"])

# cursor.execute("SELECT project_id, advisors.advisor_id, advisor FROM projects \
#                 INNER JOIN advisors \
#                 ON projects.advisor_id = advisors.advisor_id"
# )

# rows = cursor.fetchall()
# for row in rows:
#     project_id = row[0]
#     advisor_id = row[1]
#     advisor = row[2]
#     insert_query = "INSERT INTO projectsadvisors (project_id, advisor_id) VALUES(?, ?)"
#     delete_query = "DELETE FROM advisors WHERE advisor_id = ?"
#     if ',' in advisor:
#         advisor_list = advisor.split(",")
#         for name in advisor_list:
#             cleaned_name = name.lstrip()
#             result = insert_advisor(cursor, {"advisor": cleaned_name})
#             if result:
#                 print(f"new advisor added: {cleaned_name}!")
#             cursor.execute(insert_query, [project_id, find_advisor_id(cursor, cleaned_name)[0]])
#         cursor.execute(delete_query, [advisor_id])
#     else:
#         cursor.execute(insert_query, [project_id, advisor_id])

# cursor.execute("SELECT advisor FROM advisors ORDER BY advisor")
# rows = cursor.fetchall()
# for row in rows:
#     print(row[0])

# conn.commit()

# -----------------------------------------------------------------------
# Add advisors_str to Projects Table
# cursor.execute(
#     '''
#     ALTER TABLE projects ADD COLUMN advisors_str TEXT
#     '''
# )

# -----------------------------------------------------------------------
# Populate advisors_str in Projects Table
# update_advisors_str_query = "UPDATE projects SET advisors_str = ? WHERE project_id = ?"
# query = "SELECT projects.project_id, group_concat(advisor, ', ') AS advisor_group \
#                         FROM projects \
#                         INNER JOIN projectsadvisors \
#                             ON projects.project_id = projectsadvisors.project_id \
#                         INNER JOIN advisors \
#                             ON projectsadvisors.advisor_id = advisors.advisor_id \
#                         GROUP BY projects.project_id, student, title"
# cursor.execute(query)
# rows = cursor.fetchall()
# for row in rows:
#     project_id = row[0]
#     advisors_str = row[1]
#     cursor.execute(update_advisors_str_query, [advisors_str, project_id])

# conn.commit()
