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

def pageRequest(url: str):
    try:
        return requests.get(url)
    except requests.HTTPError:
        print("An http error has ocurred, process has exited")
        return None
    except:
        print("An error has ocurred, process has exited")
        return None


def initWebScraper(url: str, parser: str = 'html.parser'):
    webResponse = pageRequest(url)

    if(webResponse == None):
        print("Canceling scrapping")
        return None

    return BeautifulSoup(webResponse.content, parser)


def categoryTarget(category: str) -> str:
    global errorMessage 
    if ((len(category) != 2) or (category not in availableCategories)):
        errorMessage = "Invalid Category"
        return ""
    
    return baseURL + category


def getCategoryItemStatus(item) -> str:
    try:
        item.find('span', class_='label-previsto').text
    except:
        return 'open'

    return 'expected'

@app.route('/')
def Greetings():
    return 'Hello! The API is Alive'


@app.route('/api/concursos', methods=['GET'])
def Concursos():
    concursosAvailable = []
    urls = [baseURL + 'nacional/', baseURL + 'sp/sao-paulo']

    def process_url(url):
        pageScraper = initWebScraper(url)
        if pageScraper is None:
            print("Developer: This is a security issue, do not propagate None result")
            abort(jsonify(message=errorMessage, code=400))

        listConcursosDiv = pageScraper.find('div', id='concursos')
        availableItemsInCategory = listConcursosDiv.find_all('div', class_='na')

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
            if len(span_elements) > 0:
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
            'status': getCategoryItemStatus(item),
            'deadline': deadline_text
            }

            concurso['aiGeneratedLink'] = process_concursos_links(concurso['link'])
            if concurso['aiGeneratedLink'] == 'não':
                concurso['aiGeneratedLink'] = None
            return concurso

        with ThreadPoolExecutor() as executor:
            return list(executor.map(process_concurso, availableItemsInCategory))

    for url in urls:
        concursosAvailable.extend(process_url(url))

    response = jsonify(concursosAvailable)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response
        

if __name__ == "__main__":
    app.run()