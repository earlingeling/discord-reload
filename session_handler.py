import requests
import os
import pickle

SESSION_FILE = 'session.pkl'

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'rb') as f:
            session = pickle.load(f)
    else:
        session = requests.Session()
    return session
 
def save_session(session):
    with open(SESSION_FILE, 'wb') as f:
        pickle.dump(session, f)