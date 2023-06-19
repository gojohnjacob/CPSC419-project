from flask import Flask, request, make_response, render_template, redirect, session
from database import *
from search import handle_parameter, load_all, load_dropdowns
from flask_cas import CAS, login_required

#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='../client', static_folder='../client/static')
cas = CAS(app)
app.config['CAS_SERVER'] = 'https://secure6.its.yale.edu/cas/'
app.config['CAS_AFTER_LOGIN'] = 'https://127.0.0.1:17290/'
app.config['CAS_AFTER_LOGOUT'] = 'https://127.0.0.1:17290/'
app.secret_key = '\xf3z\xb6\x19E\xce\xb4\xb6\x9cvy7\xb0\xc3\xfc\xe7\x92\xb7\xf7\xc9\x00\xcc\xb7\x80'

ADMIN_USERS = set([])

#-----------------------------------------------------------------------

@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

#-----------------------------------------------------------------------

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@login_required
def index():
    data = get_random_project()
    html = render_template('index.html', data=data)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/faq', methods=['GET'])
@login_required
def faq():
    html = render_template('faq.html')
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/search', methods=['GET'])
@login_required
def search():
    data = load_all()

    advisors, year, semester = load_dropdowns()

    html = render_template('search.html', data=data, advisors = advisors, year = year, semester = semester)

    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/searchresults', methods=['GET'])
@login_required
def search_results():
    parameter = request.args.get('parameter')
    year = request.args.get('year')
    advisor = request.args.get('advisor')
    semester = request.args.get('semester')

    if (parameter is None or parameter.strip() == '')\
        and (year is None or year.strip() == '')\
            and (advisor is None or advisor.strip()) == ''\
                and (semester is None or semester.strip()) == '':

        data = load_all()

        html = render_template('searchresults.html', data = data)

        response = make_response(html)

        return response
    
    data = handle_parameter(parameter, year, advisor, semester)
    
    html = render_template('searchresults.html', data = data)
    
    response = make_response(html)
    
    return response

#-----------------------------------------------------------------------

@app.route('/projects/index', methods=['GET'])
@login_required
def projects_index():
    html = render_template('projects/index.html', terms=get_all_terms())
    response = make_response(html)

    return response
#-----------------------------------------------------------------------

@app.route('/projects', methods=['GET'])
@login_required
def projects_get():
    sem = request.args.get('sem')
    year = request.args.get('year')
    id = request.args.get('id')

    # display list of projects for a specific semester and year
    if sem and year:
        data = get_projects_by_term(sem, year)
        html = render_template('projects/list.html', data=data)
    # display individual project for a specific id
    elif id:
        project_data = get_project_details(id)
        is_liked = find_favorite(session['CAS_USERNAME'], id)
        is_authorized = (session['CAS_USERNAME'] in ADMIN_USERS) or (session['CAS_USERNAME'] == project_data['net_id'])
        html = render_template("projects/details.html", data=project_data, is_authorized=is_authorized, id=id, is_liked=is_liked)

    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/projects/add', methods=['GET'])
@login_required
def projects_add_form():
    html = render_template("projects/add.html")
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/projects', methods=['POST'])
@login_required
def projects_post():
    name = request.form['name']
    semester = request.form['semester']
    year = request.form['year']
    advisor = request.form['advisor']
    title = request.form['title']
    abstract = request.form['abstract']
    homepage = request.form['homepage']
    net_id = request.form['net_id']
    if net_id == "":
        net_id = session['CAS_USERNAME']

    data = {
        'student': name,
        'title': title,
        'abstract': abstract,
        'homepage': homepage,
        'advisor': advisor,
        'semester': semester,
        'year': year,
        'net_id': net_id,
    }

    project_id = insert_new_project(data)
    return redirect(f'/projects?id={project_id}')

#-----------------------------------------------------------------------

@app.route('/projects/edit', methods=['GET'])
@login_required
def projects_edit_form():
    id = request.args.get('id')
    project_data = get_project_details(id)
    is_authorized = (session['CAS_USERNAME'] in ADMIN_USERS) or (session['CAS_USERNAME'] == project_data['net_id'])
    all_advisors = []
    for advisor in project_data['advisor_info']:
        all_advisors.append(advisor[1])
    project_data['advisors'] = ", ".join(all_advisors)

    if not is_authorized:
        html = render_template("projects/no_authorization.html")
    else:
        html = render_template("projects/edit.html", data=project_data, id=id)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/projects/edit', methods=['POST'])
@login_required
def update_projects():
    id = request.args.get('id')
    name = request.form['name']
    semester = request.form['semester']
    year = request.form['year']
    advisor = request.form['advisor']
    title = request.form['title']
    abstract = request.form['abstract']
    homepage = request.form['homepage']

    data = {
        'student': name,
        'title': title,
        'abstract': abstract,
        'homepage': homepage,
        'advisor': advisor,
        'semester': semester,
        'year': year,
    }

    if request.form['action'] == "Update":
        update_existing_project(id, data)

    return redirect(f'/projects?id={id}')

#-----------------------------------------------------------------------

@app.route('/projects/delete', methods=['GET'])
@login_required
def delete_user_project():
    id = request.args.get('id')

    delete_project(id)
    return redirect('/projects/index')

#-----------------------------------------------------------------------

@app.route('/advisors', methods=['GET'])
@login_required
def advisor():
    id = request.args.get('id')

    if not id:
        html = render_template("advisors/list.html", data=get_advisors())
    else: 
        advisor_data = get_advisor_details(id)
        html = render_template("advisors/profile.html", data=advisor_data)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/api/favorite', methods=['POST', 'DELETE', 'GET'])
@login_required
def add_favorite():
    project_id = request.args.get('id')
    data = {'net_id': session['CAS_USERNAME'], 'project_id': project_id}

    if request.method == 'POST':
        insert_new_favorite(data)
    elif request.method == 'DELETE':
        delete_favorite(session['CAS_USERNAME'], project_id)
    elif request.method == 'GET':
        if find_favorite(session['CAS_USERNAME'], project_id):
            return {'status': True}
        return {'status': False}

    return ""

#-------------------------------------------------------------

@app.route('/favorites', methods=['GET'])
@login_required
def favorites():
    favorite_ids = get_favorites(session['CAS_USERNAME'])
    favorites = []

    for id in favorite_ids:
        project = get_project_details(id)
        project["id"] = id
        favorites.append(project)
    
    html = render_template("favorites.html", favs=favorites)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/favorites/drop', methods = ['GET'])
@login_required
def drop_favorite():
    project_id = request.args.get("projectid")

    delete_favorite(session['CAS_USERNAME'], project_id)
    return redirect('/favorites')
