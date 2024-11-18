import os
from dotenv import load_dotenv
import imaplib
import email
from bs4 import BeautifulSoup


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


def fetch_messages():
    mail = connect_to_mail()
    _, search_data = mail.search(None,'(BODY "unsubscribe")')
    data = search_data[0].split()

    links = []
    print('Links found:')

    for num in data:
        _, data = mail.fetch(num, '(RFC822)')
        msg  = email.message_from_bytes(data[0][1])

        if msg.is_multipart():
           for part in msg.walk():
               if part.get_content_type() == 'text/html':
                   html_content = part.get_payload(decode=True).decode()
                   links.extend(extract_links_from_html(html_content))
                #    print(f'HTML Content: {html_content}')
        else:
           content_type = msg.get_content_type()
           content = msg.get_payload(decode=True).decode()

           if content_type == 'text/html':
               links.extend(extract_links_from_html(content))
            #    print(f'Content: {content}')


    mail.logout()
    return links

links = fetch_messages()

print('\n'.join(links))