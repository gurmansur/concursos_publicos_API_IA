'''
    ConcursosNoBrasil web scrapper and API
'''

import requests
from bs4 import BeautifulSoup
from flask import Flask, abort, jsonify
import linkFinderAI
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from flask import send_file
import io

app = Flask(__name__)
availableCategories = ['br', 'ac', 'al', 'am', 'ap', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mg',
                       'ms', 'mt', 'pa', 'pb', 'pe', 'pi', 'pr', 'rj', 'rn', 'ro', 'rr', 'rs', 'sc', 'se', 'sp', 'to']
baseURL = 'https://concursosnobrasil.com/concursos/'
errorMessage = ''

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


@app.route('/concursos/<categorySelect>', methods=['GET'])
def Concursos(categorySelect):
    concursosAvailable = []
    pageScraper = initWebScraper(categoryTarget(categorySelect))

    if(pageScraper == None):
        print("Developer: This is a security issue, do not propagate None result")
        abort(jsonify(message=errorMessage, code=400))

    listConcursosTable = pageScraper.find('table')
    if listConcursosTable is None:
        abort(jsonify(message="No concursos found", code=404))
    
    tableBody = listConcursosTable.find('tbody')
    if tableBody is None:
        abort(jsonify(message="No concursos found in the table", code=404))
    
    availableItemsInCategory = tableBody.find_all('tr')
    
    def process_concurso(item):
        concurso = {
            'organization': item.find('a').text.rstrip(),
            'workPlacesAvailable': item.find_all('td')[1].text.rstrip(),
            'link': item.find('a').get('href'),
            'status': getCategoryItemStatus(item)
        }
        concurso['aiGeneratedLink'] = linkFinderAI.process_url_links(concurso['link'])
        return concurso

    with ThreadPoolExecutor() as executor:
        concursosAvailable = list(executor.map(process_concurso, availableItemsInCategory))

    return jsonify(concursosAvailable)

if __name__ == "__main__":
    app.run()