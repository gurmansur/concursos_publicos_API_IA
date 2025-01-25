from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.utils import shuffle
from pandas import DataFrame
import os
from dotenv import load_dotenv

# Function to fetch and parse the webpage
def fetch_page(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

# Function to extract links and their text
def extract_links(soup, extract_parent_text=False):
    links = []
    print(soup)

    for a_tag in soup.find_all('a', href=True):
        link_text = a_tag.get_text()
        if extract_parent_text:
            parent_text = a_tag.find_parent().get_text() if a_tag.find_parent() else ''
            current_sentence = parent_text.split(link_text)[0].split('.')[-1].strip() + ' ' + link_text
            links.append((a_tag['href'], current_sentence.strip()))
        else:
            links.append((a_tag['href'], link_text))
    return links
    
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    api_key=api_key
);

# Example usage
def process_concursos_links(url):
    soup = fetch_page(url)
    links = extract_links(soup, extract_parent_text=True)

    # Filter out links pointing to https://concursosnobrasil.com/ or links that don't start with 'https://'
    links = [(link, text) for link, text in links if not link.startswith('/') and 'concursosnobrasil.com' not in link]

    if not links:
        return []

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente de IA."},
            {"role": "user", "content": "Algum desses links é utilizado para realizar a inscrição no concurso? Se sim, responda com apenas o link. Se não, responda com 'não'."},
            {"role": "user", "content": f"Aqui está a lista de links extraídos: {links}"},
        ],
        max_tokens=100,
        stop=["\n"],
    );

    return response.choices[0].message.content

def process_other_links(url):
    soup = fetch_page(url)
    
    links = soup.find_all('a', href=True)

    if not links:
        return []

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente de IA."},
            {"role": "user", "content": "Algum desses links é utilizado para realizar a inscrição no concurso? Se sim, responda com apenas o link. Se não, responda com 'não'."},
            {"role": "user", "content": f"Aqui está a lista de links extraídos: {links}"},
        ],
        max_tokens=100,
        stop=["\n"],
    );

    return response.choices[0].message.content

if __name__ == "__main__":
    url = 'https://concursosnobrasil.com/concursos/br/2025/01/24/concurso-do-ibama/'
    print(process_concursos_links(url))