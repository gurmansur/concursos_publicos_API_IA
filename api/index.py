import requests
from bs4 import BeautifulSoup
from flask import Flask, abort, jsonify
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
from openai import OpenAI

app = Flask(__name__)
availableCategories = ['br', 'ac', 'al', 'am', 'ap', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mg',
                       'ms', 'mt', 'pa', 'pb', 'pe', 'pi', 'pr', 'rj', 'rn', 'ro', 'rr', 'rs', 'sc', 'se', 'sp', 'to']
baseURL = 'https://www.pciconcursos.com.br/concursos/'
errorMessage = ''

# Function to fetch and parse the webpage
def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

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

client = OpenAI(api_key=api_key)

# Example usage
def process_concursos_links(url):
    soup = fetch_page(url)
    if not soup:
        return None
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
        max_tokens=500,
        stop=["\n"],
    )

    return response.choices[0].message.content

def init_web_scraper(url, parser='html.parser'):
    soup = fetch_page(url)
    if not soup:
        print("Canceling scraping")
        return None
    return soup

def category_target(category):
    global errorMessage
    if len(category) != 2 or category not in availableCategories:
        errorMessage = "Invalid Category"
        return ""
    return baseURL + category

def get_category_item_status(item):
    return 'expected' if item.find('span', class_='label-previsto') else 'open'

@app.route('/')
def greetings():
    return 'Hello! The API is Alive'

@app.route('/api/concursos', methods=['GET'])
def concursos():
    concursos_available = []
    urls = [baseURL + 'nacional/', baseURL + 'sp/sao-paulo']

    def process_concurso(item):
        cd_div = item.find('div', class_='cd')
        vacancies_text = cd_div.text.split('vaga')[0].strip()
        vacancies = int(vacancies_text.split()[-1]) if vacancies_text.split()[-1].isdigit() else 1

        salary = 'N/A'
        profession = 'N/A'
        level = 'N/A'

        if 'R$' in cd_div.text:
            salary = 'R$ ' + cd_div.text.split('R$')[1].split('<br>')[0].strip()

        span_elements = cd_div.find_all('span')
        if span_elements:
            profession = span_elements[0].text.strip()
        if len(span_elements) > 1:
            level = span_elements[1].text.strip()

        salary = salary.replace(profession, '').strip()
        profession = profession.replace(level, '').strip()

        location = item.find('div', class_='cc').text.rstrip() if item.find('div', class_='cc') and item.find('div', class_='cc').text.strip() else 'Nacional'
        deadline_text = item.find('div', class_='ce').text.rstrip().replace('a', 'a ').strip()

        concurso = {
            'organization': item.find('a').text.rstrip(),
            'location': location,
            'vacancies': vacancies,
            'salary': salary,
            'profession': profession,
            'level': level,
            'link': item.find('a').get('href'),
            'status': get_category_item_status(item),
            'deadline': deadline_text
        }

        concurso['aiGeneratedLink'] = process_concursos_links(concurso['link'])
        if concurso['aiGeneratedLink'] == 'não':
            concurso['aiGeneratedLink'] = None
        return concurso

    def process_url(url):
        page_scraper = init_web_scraper(url)
        if not page_scraper:
            abort(jsonify(message=errorMessage, code=400))

        list_concursos_div = page_scraper.find('div', id='concursos')
        available_items_in_category = list_concursos_div.find_all('div', class_='na')

        with ThreadPoolExecutor(max_workers=10) as executor:
            return list(executor.map(process_concurso, available_items_in_category))

    for url in urls:
        concursos_available.extend(process_url(url))

    response = jsonify(concursos_available)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

if __name__ == "__main__":
    app.run()
