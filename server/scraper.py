import requests
from bs4 import BeautifulSoup
from table_utils.insert_table_data import insert_new_project


# Spring 2008 and Fall 2007 have text format on abstract page
# Spring 2007 - Fall 2002 have only webpages listed
# Fall 2002 - Fall 1998 have text format on abstract page
# Spring 1998 and Fall 1997 only have abstracts listed

# keep track of the number of projects that have faulty data
# many projects simply are not listed with any data or don't have valid abstract pages

exception_count = 0


def get_semesters():
    """Scrapes the list of semesters and years, and the links to their pages, from the CPSC 490 website."""

    URL = "https://zoo.cs.yale.edu/classes/cs490/"

    page = requests.get(URL)
    page_html = page.text
    soup = BeautifulSoup(page_html, 'html.parser')

    # compile into list of dictionaries and return

    results = []

    for link in soup.find_all('a')[2:]:
        semester_info = link.get_text().strip().split()
        results.append({"semester": semester_info[0], "year": semester_info[1], "page": URL + link.get('href')})
    
    return results


def get_project_info(page):
    """Scrapes the project author, title, advisor and abstract from the input project webpage."""

    URL = page

    project_page = requests.get(URL)
    project_html = project_page.text
    project_soup = BeautifulSoup(project_html, 'html.parser')

    # return the results as a dictionary

    results = {}

    results["student"] = project_soup.li.contents[2].strip()
    results["title"] = project_soup.li.contents[3].contents[2].strip()
    results["advisor"] = project_soup.li.contents[3].contents[3].contents[2].strip()
    results["abstract"] = project_soup.body.contents[2].strip()

    return results


def get_old_project_info(page):
    """Parses the author, title, advisor, and abstract from the input project text description."""
    URL = page

    project_page = requests.get(URL)
    project_html = project_page.text

    string_parts = project_html.replace('\n', '\n ').split('\n')

    # use the same format as in get_project_info()

    results = {}

    results["student"] = ''.join(string_parts[0].split(':')[1:]).strip()
    results["title"] = ''.join(string_parts[1].split(':')[1:]).strip()
    results["advisor"] = ''.join(string_parts[2].split(':')[1:]).strip()
    results["abstract"] = ''.join(string_parts[4:]).replace('\n', ' ').replace('\r', ' ').replace('  ', ' ').strip()

    return results


def process_semester_page(page, semester, year, text_abstracts=False):
    """Initiates the scraping of all the projects listed on the given page with the given semester and year."""
    URL = page

    semester_page = requests.get(URL)
    semester_html = semester_page.text
    semester_soup = BeautifulSoup(semester_html, 'html.parser')

    projects = []
    global exception_count

    for line in semester_soup.find_all('li'):

        project = {}

        links = line.find_all('a', recursive = False)

        # check for web pages, since not all projects have them listed

        if len(links) == 2:
            project["homepage"] = URL.replace("index.html", links[1].get('href')).replace("Index.html", links[1].get('href'))
        else:
            project["homepage"] = None

        # if a page is not available or in an irregular format, count that in exception_count

        if (text_abstracts):
            try:
                project_data = get_old_project_info(URL.replace("Index.html", links[0].get('href')).replace("index.html", links[0].get('href')))
            except:
                exception_count += 1
                continue
        else:
            try:
                project_data = get_project_info(URL.replace("index.html", links[0].get('href')))
            except:
                exception_count += 1
                continue
        
        project.update(project_data)
        project["semester"] = semester
        project["year"] = int(year)
        projects.append(project)

    return projects


def process_old_semester_page(page, semester, year):
    """Scrapes the author, title, webpage, and advisor from the given page. Intended for pages that don't have abstracts listed."""

    URL = page

    semester_page = requests.get(URL)
    semester_html = semester_page.text
    semester_soup = BeautifulSoup(semester_html, 'html.parser')

    projects = []
    global exception_count

    for line in semester_soup.find_all('li'):

        project = {}

        # if a line is in an irregular format, count that in exception_count

        try: 
            link = line.find_all('a', recursive = False)[0]
            project["student"] = line.contents[0].replace(',', '').strip()
            project["title"] = link.contents[0].strip()
            project["advisor"] = line.contents[2].split(':')[1].replace('.', '').strip()
            project["abstract"] = None
            project["homepage"] = URL.replace("index.html", link.get('href'))
        except Exception as ex:
            exception_count += 1
            continue
        project["semester"] = semester
        project["year"] = int(year)
        projects.append(project)
    
    return projects


def parse_text(page):
    """A remake of get_old_project_info, using a different parsing method."""
    URL = page

    project_page = requests.get(URL)
    project_html = project_page.text

    string_parts = project_html.replace('\n', '\n ').split('\n')

    # use the same format as in get_project_info()

    results = {}

    results["student"] = ''.join(string_parts[0].split(':')[1:]).strip()

    if "Title:" in string_parts[1]:
        results["title"] = ''.join(string_parts[1].split(':')[1:]).strip()

    if "Advisor:" in string_parts[2]:
        results["advisor"] = ''.join(string_parts[2].split(':')[1:]).strip()
    else:
        results["title"].join(string_parts[2].split(':')[1:]).strip()
        results["advisor"] = ''.join(string_parts[3].split(':')[1:]).strip()
    
    results["abstract"] = ''.join(string_parts[4:]).replace('\n', ' ').replace('\r', ' ').replace('  ', ' ').strip()

    return results


if __name__ == "__main__":

    all_projects = []

    semesters = get_semesters()

    # use different parsing methods for different years

    for semester in semesters[:28]:
        projects = process_semester_page(semester["page"], semester["semester"], semester["year"])
        all_projects += projects
    
    for semester in semesters[28:30]:
        projects = process_semester_page(semester["page"], semester["semester"], semester["year"], text_abstracts = True)
        all_projects += projects
    
    for semester in semesters[30:40]:
        projects = process_old_semester_page(semester["page"], semester["semester"], semester["year"])
        all_projects += projects
    
    for semester in semesters[40:48]:
        projects = process_semester_page(semester["page"], semester["semester"], semester["year"], text_abstracts = True)
        all_projects += projects

    # print out success counts of the number of projects we know are not included

    print(len(all_projects))
    print("Not Included: " + str(exception_count))

    # insert into database

    for project in all_projects:
        insert_new_project(project)
    
    print("Success!")
