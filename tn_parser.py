import re
import time
import traceback

import requests
from requests.adapters import HTTPAdapter, Retry

from logs import logger
from pwd_cipher import AESCipher

TN_INIT_URL = "https://tech-nation-visa.smapply.io/prog/"
TN_LOGIN_URL = "https://tech-nation-visa.smapply.io/acc/l/"
TN_APP_URL = "https://tech-nation-visa.smapply.io/prog/app/ds/"

TIMEOUT_S = 2
N_RETRIES = 3
SLEEP_BETWEEN_REQUESTS_S = 0.5


class WrongCredentials(Exception):
    pass


class Application:
    def __init__(self, name, reference_id, submitted_ts, last_edited_ts):
        self.name = name
        self.reference_id = reference_id
        self.submitted_ts = submitted_ts
        self.last_edited_ts = last_edited_ts
        

def retry(func):
    def wrap(*args, **kwargs):
        error = None
        for i in range(N_RETRIES):
            logger.debug(
                f"Running {func.__name__}, attempt {i + 1}",
                extra={"Args": args, "Kwargs": kwargs})
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Failed {func.__name__}, attempt {i + 1}",
                    extra={
                        "error": e,
                        "traceback": traceback.format_exc(),
                        "Args": args,
                        "Kwargs": kwargs,
                    }
                )
                error = e
                if i == N_RETRIES - 1:
                    break
                time.sleep(SLEEP_BETWEEN_REQUESTS_S * 2 ** i)
        raise error
    return wrap


@retry
def get(session, **kwargs):
    response = session.get(**kwargs)
    response.raise_for_status()
    return response


@retry
def post(session, **kwargs):
    response = session.post(**kwargs)
    response.raise_for_status()
    return response


def create_session():
    session = requests.Session()

    response = get(session, url=TN_INIT_URL, timeout=TIMEOUT_S)
    csrf_token = re.findall(
        "name='csrfmiddlewaretoken' value='([a-zA-Z\d]+)'", response.text
    )[0]
    return session, csrf_token


def login(email, password, session, csrf_token):
    return post(
        session,
        url=TN_LOGIN_URL,
        headers={
            "Referer": TN_LOGIN_URL,
        },
        data={
            "email": email,
            "password": AESCipher().decrypt(password),
            "csrfmiddlewaretoken": csrf_token,
        },
        allow_redirects=True,
        timeout=TIMEOUT_S,
    )


def get_applications(session):
    page_number = 1
    applications = []

    while True:
        page = get(
            session,
            url=TN_APP_URL, data={"page": str(page_number)}, timeout=TIMEOUT_S
        )
        applications.extend(page.json().get("results", []))
        if not page.json().get("has_next", False):
            break
        page_number += 1

    return applications


def get_last_application(email, password):
    logger.debug(f"Getting last application {email} - creating session")
    session, csrf_token = create_session()
    time.sleep(SLEEP_BETWEEN_REQUESTS_S)

    logger.debug(f"Getting last application {email} - logging in")
    login_page = login(email, password, session, csrf_token)
    time.sleep(SLEEP_BETWEEN_REQUESTS_S)

    logger.debug(f"Getting last application {email} - getting all apllications")
    applications = get_applications(session)

    logger.debug(
        f"Getting last application {email} - results: {login_page.content}, {applications}"
    )

    submitted_applications = []
    for application in applications:
        if application.get("is_submitted", False):
            submitted_applications.append(application)

    if len(submitted_applications) == 0:
        return Application()

    last_application = sorted(
        submitted_applications, key=lambda a: a["submitted_date"]
    )[-1]
    return Application(
        last_application.get("user", {}).get("name"),
        last_application.get("reference_id"),
        last_application.get("submitted_date"),
        last_application.get("last_edited"),
    )


def check_password(email, password):
    logger.debug(f"Checking password {email} - creating session")
    session, csrf_token = create_session()
    time.sleep(SLEEP_BETWEEN_REQUESTS_S)

    logger.debug(f"Checking password {email}, {password} - logging in")
    login(email, password, session, csrf_token)
    time.sleep(SLEEP_BETWEEN_REQUESTS_S)

    logger.debug(f"Checking password {email} - getting home page")
    home_page = get(session, url=TN_INIT_URL)

    logger.debug(f"Checking password {email}. Home page url: {home_page.url}")
    return home_page.url == TN_INIT_URL
