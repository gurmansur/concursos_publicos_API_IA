from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Function to fetch and parse the webpage
def fetch_page(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

# Function to extract links and their text
def extract_links(soup):
    links = []
    article_body = soup.find('div', itemprop='articleBody')
    if article_body:
        for p_tag in article_body.find_all('p'):
            for a_tag in p_tag.find_all('a', href=True):
                link_text = a_tag.get_text()
                parent_text = a_tag.find_parent().get_text() if a_tag.find_parent() else ''
                current_sentence = parent_text.split(link_text)[0].split('.')[-1].strip() + ' ' + link_text
                links.append((a_tag['href'], current_sentence.strip()))
    return links
    
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    api_key=api_key
);

# Example usage
def process_concursos_links(url):
    soup = fetch_page(url)
    links = extract_links(soup)

    links = [(link, text) for link, text in links if not link.startswith('/') and 'pciconcursos.com' not in link]

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
    url = 'https://www.pciconcursos.com.br/noticias/aeronautica-anuncia-novo-processo-seletivo-para-o-curso-de-formacao-de-sargentos'
    print(process_concursos_links(url))