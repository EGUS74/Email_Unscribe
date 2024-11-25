import os
from dotenv import load_dotenv
import imaplib
import email
from bs4 import BeautifulSoup
import requests


load_dotenv()

username = os.getenv('EMAIL')
password = os.getenv('PASSWORD')

def connect_to_mail():
    mail = imaplib.IMAP4_SSL('imap.mail.yahoo.com')
    mail.login(username, password)
    mail.select('inbox')
    return mail

def extract_links_from_html(html_content):
    spoup = BeautifulSoup(html_content, 'html.parser')
    links = [link['href'] for link in spoup.find_all('a', href=True) if "unsubscribe" in link['href'].lower()]
    return links

def click_link(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            print(f'Clicked on link: {link}')
        else:
            print(f'Failed to click on link: {link} (Status code: {response.status_code})')
    except Exception as e:
        print(f'Failed to click on link: {link} (Error: {e})')

def fetch_messages():
    mail = connect_to_mail()
    _, search_data = mail.search(None, '(BODY "unsubscribe")')
    data = search_data[0].split()

    links = []
    print('Links found:')

    for num in data:
        _, data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/html':
                    try:
                        html_content = part.get_payload(decode=True).decode('utf-8', errors='replace')
                        links.extend(extract_links_from_html(html_content))
                    except Exception as e:
                        print(f"Error decoding part: {e}")
        else:
            content_type = msg.get_content_type()
            try:
                content = msg.get_payload(decode=True).decode('utf-8', errors='replace')
                if content_type == 'text/html':
                    links.extend(extract_links_from_html(content))
            except Exception as e:
                print(f"Error decoding message: {e}")

    mail.logout()
    return links

def save_links_to_file(links):
    with open('unsubscribe_links.txt', 'w') as file:
        file.write('\n'.join(links))
        print('Links saved to unsubscribe_links.txt')

links = fetch_messages()

# print('\n'.join(links))

for link in links:
    click_link(link)    


save_links_to_file(links)