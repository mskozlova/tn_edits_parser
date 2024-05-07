import re
import requests


TN_INIT_URL = "https://tech-nation-visa.smapply.io/prog/"
TN_LOGIN_URL = "https://tech-nation-visa.smapply.io/acc/l/"
TN_APP_URL = "https://tech-nation-visa.smapply.io/prog/app/ds/"


class Application:
    def __init__(self, name, reference_id, submitted_ts, last_edited_ts):
        self.name = name
        self.reference_id = reference_id
        self.submitted_ts = submitted_ts
        self.last_edited_ts = last_edited_ts


def create_session():
    session = requests.Session()
    response = session.get(TN_INIT_URL)
    response.raise_for_status()
    csrf_token = re.findall("name='csrfmiddlewaretoken' value='([a-zA-Z\d]+)'", response.text)[0]
    return session, csrf_token


def login(email, password, session, csrf_token):
    session.post(
        url=TN_LOGIN_URL,
        headers={
            "Referer": TN_LOGIN_URL,
        },
        data={
            "next": "/prog/",
            "email": email,
            "password": password,
            "csrfmiddlewaretoken": csrf_token,
        },
        allow_redirects=True
    )


def get_applications(session):
    page_number = 1
    applications = []
    
    while True:
        page = session.get(
            url=TN_APP_URL,
            data={"page": str(page_number)}
        )
        page.raise_for_status()
        applications.extend(page.json().get("results", []))
        
        if not page.json().get("has_next", False):
            break
        page_number += 1
    
    return applications


def get_last_application(email, password):
    session, csrf_token = create_session()
    login(email, password, session, csrf_token)
    applications = get_applications(session)
    
    if len(applications) == 0:
        return Application()
    
    last_application = sorted(applications, key=lambda a: a["submitted_date"])[-1]
    return Application(
        last_application.get("user", {}).get("name"),
        last_application.get("reference_id"),
        last_application.get("submitted_date"),
        last_application.get("last_edited"),
    )
