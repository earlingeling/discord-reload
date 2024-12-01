import os
from config import *
import requests
from bs4 import BeautifulSoup
import logging
import certifi
from session_handler import load_session, save_session
from logger_config import logger
import json

service_link = os.getenv("SERVICE_LINK")
status_page_link = os.getenv("STATUS_PAGE_LINK")
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

logger = logging.getLogger(__name__)

def fetch_csrf_token(session):
    if not service_link:
        logger.error("Service link not set.")
        raise Exception("Service link not set")

    headers = {
        'User-Agent': user_agent,
    }

    response = session.get(service_link, headers=headers, verify=certifi.where())

    if response.status_code != 200:
        message = f"HTTP code for {service_link} is NOT 200 - it is {response.status_code}. Incorrect URL?"
        logger.error(message)
        raise Exception(message)

    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_meta = soup.find('meta', {'name': 'csrf-token'})

    if not csrf_meta:
        message = f"CSRF token not found in {service_link}"
        logger.error(message)
        raise Exception(message)

    csrf_token = csrf_meta['content']
    logger.info(f"CSRF token fetched: {csrf_token}")

    return csrf_token

def login(session):
    if not (username and password):
        logger.error("Username or password not set.")
        raise Exception("Username or password not set")

    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        '_token': fetch_csrf_token(session),
        'username': username,
        'password': password,
    }

    response = session.post(service_link, data=payload, headers=headers, verify=certifi.where())

    if response.status_code != 200 or "You have entered invalid credentials" in response.text:
        message = f"Wrong panel credentials. HTTP code: {response.status_code}"
        logger.error(message)
        raise Exception(message)
    
    if "Too many login attempts" in response.text:
        message = f"Too many login attempts. HTTP code: {response.status_code}"
        logger.error(message)
        raise Exception(message)
    
    if '<div class="notification hide" data-title="Errors occurred" data-type="error">' in response.text:
        message = f"Unknown error occurred. HTTP code: {response.status_code}"
        logger.error(message)
        raise Exception(message)
    
    if response.status_code != 200 and ("Connections" not in response.text or "Connection Map" not in response.text):
            raise Exception("Failed to login, but csrf worked??")

    logger.info("Login successful")
    save_session(session)

def fetch_stats(session):
    status_page_link = service_link + "/dashboard/stats"

    if not status_page_link:
        logger.error("Stats page link not set.")
        raise Exception("Stats page link not set")

    headers = {
        'User-Agent': user_agent,
    }

    response = session.get(status_page_link, headers=headers, verify=certifi.where())

    if response.status_code != 200:
        message = f"Failed to fetch status page with status code {response.status_code}"
        logger.error(message)
        raise Exception(message)

    logger.info("Status fetched successfully")
    return json.loads(response.text)

def get_servers(session):
    headers = {
        'User-Agent': user_agent,
    }

    response = session.get(service_link, headers=headers, verify=certifi.where())

    if response.status_code != 200:
        logger.error(f"Failed to fetch servers with status code {response.status_code}")
        raise Exception(f"Failed to fetch servers with status code {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    servers = []

    # Find all h4 elements with the specified class
    h4_elements = soup.find_all('h4', class_='card-title text-uppercase mb-0')

    for h4 in h4_elements:
        # Extract the server name
        name = h4.get_text(strip=True).split('-')[0].strip()

        # Find the corresponding button element
        button = h4.find_next('button', {'data-url': True})
        if button:
            # Extract the server ID from the data-url attribute
            data_url = button['data-url']
            server_id = data_url.split('/')[-2]

            # Append the server name and ID to the list
            servers.append({'name': name, 'id': server_id})

    return servers

def get_combined_stats(session):
    # Fetch server stats
    stats = fetch_stats(session)
    servers = get_servers(session)

    # Create a dictionary to map server IDs to names
    server_name_map = {server['id']: server['name'] for server in servers}

    combined_stats = []

    for server_stat in stats['servers']:
        server_id = str(server_stat['server_id'])
        if server_id in server_name_map:
            combined_stats.append({
                'name': server_name_map[server_id],
                'id': server_id,
                'open_connections': server_stat['open_connections'],
                'total_streams': server_stat['total_streams'],
                'total_running_streams': server_stat['total_running_streams'],
                'down_streams': server_stat['down_streams'],
                'uptime': server_stat['uptime']
            })

    return combined_stats

def reload_server(session, id):
    headers = {
        'User-Agent': user_agent,
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Csrf-Token': fetch_csrf_token(session),
    }

    response = session.post(f"{service_link}/server-manager/reload/{id}/0", headers=headers, verify=certifi.where())

    if response.status_code != 200:
        print(response.text)
        logger.error(f"Failed to reload server with status code {response.status_code}")
        raise Exception(f"Failed to reload server with status code {response.status_code}")
    
    response_data = response.json()

    if response_data.get("type") == "success" and "fast reloaded" in response_data.get("message", ""):
        logger.info(f"Server with ID {id} reloaded successfully: {response_data['message']}")
        return f"Server with ID {id} reloaded successfully: {response_data['message']}"
    else:
        logger.error(f"Failed to reload server with ID {id}: {response_data}")
        return f"Failed to reload server with ID {id}: {response_data}"


