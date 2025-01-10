import requests
import os
import pickle

SESSION_FILE = 'session.pkl'

PROXY_ENABLED = True

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'rb') as f:
            session = pickle.load(f)
    else:
        session = requests.Session()
        if PROXY_ENABLED:
            session.proxies = {
                "http": "http://zgnmu:6dqszqur@185.135.11.34:6084",
                "https": "http://zgnmu:6dqszqur@185.135.11.34:6084",
            }
    return session
 
def save_session(session):
    with open(SESSION_FILE, 'wb') as f:
        pickle.dump(session, f)