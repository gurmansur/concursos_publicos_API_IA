import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.utils import shuffle
from pandas import DataFrame

# Function to fetch and parse the webpage
def fetch_page(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

# Function to extract links and their text
def extract_links(soup):
    links = []
    for a_tag in soup.find_all('a', href=True):
        link_text = a_tag.get_text()
        parent_text = a_tag.find_parent().get_text() if a_tag.find_parent() else ''
        current_sentence = parent_text.split(link_text)[0].split('.')[-1].strip() + ' ' + link_text
        links.append((a_tag['href'], current_sentence.strip()))
    return links

# Function to train the model
def train_model(df):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df['text'])
    y = df['label']
    
    model = LogisticRegression()
    model.fit(X, y)
    
    return model, vectorizer

# Function to predict relevant links
def predict_relevant_links(model, vectorizer, links):
    X = vectorizer.transform([text for _, text in links])
    predictions = model.predict(X)
    return [(link, text) for (link, text), pred in zip(links, predictions) if pred == 1]

# Example training data: (label, text)
training_data = [
    (1, 'Realizar Inscrição'),
    (1, 'Candidatos'),
    (1, 'Candidato'),
    (1, 'Candidate-se'),
    (1, 'Participar'),
    (0, 'Inicio'),
    (1, 'Saiba mais'),
    (0, 'Nos contate'),
    (1, 'Inscreva-se agora'),
    (0, 'Sobre nós'),
    (0, 'Política de privacidade'),
    (1, 'Cadastre-se aqui'),
    (0, 'Termos de uso'),
    (1, 'Clique para se inscrever'),
    (0, 'Ajuda'),
    (1, 'Veja mais detalhes'),
    (0, 'Mapa do site'),
    (1, 'Inscrição'),
    (0, 'Fale conosco'),
    (1, 'Inscreva-se'),
    (0, 'Perguntas frequentes'),
    (1, 'Inscreva-se já'),
    (0, 'Trabalhe conosco'),
    (0, 'Sobre a empresa'),
    (1, 'Inscreva-se no site'),
    (0, 'Contato'),
    (1, 'Clique aqui para se inscrever'),
    (0, 'Suporte'),
    (1, 'Inscreva-se no link'),
    (0, 'Missão'),
    (1, 'Participe clicando aqui'),
    (0, 'Central de ajuda'),
    (1, 'Inscreva-se no formulário'),
    (0, 'Valores'),
    (1, 'Clique aqui para saber mais'),
    (0, 'Central de atendimento'),
    (1, 'Inscreva-se já mesmo'),
    (0, 'Visão'),
    (1, 'Clique aqui para se inscrever agora'),
    (0, 'Fale com o suporte'),
    (1, 'Inscreva-se no site oficial'),
    (0, 'História'),
    (1, 'Inscreva-se no link abaixo'),
    (0, 'Sobre a marca'),
    (0, 'Fale com o suporte técnico'),
    (1, 'Inscreva-se no formulário de inscrição'),
    (0, 'Sobre o produto'),
    (0, 'Fale com o SAC'),
    (0, 'Sobre o serviço'),
    (1, 'Participe clicando no link'),
    (0, 'Fale com o atendimento ao cliente'),
    (1, 'Clique aqui para se inscrever no site'),
    (0, 'Sobre o projeto'),
    (0, 'Fale com o suporte ao cliente'),
    (1, 'A solicitação para participar da seleção deverá ser realizada pelo site do Cebraspe.'),
    (1, 'Aos interessados em realizar a inscrição MPU, será necessário se direcionar ao site'),
    (1, 'realizadas'),
    (1, 'inscrições'),
    (1, 'Os interessados deverão se conduzir até o site'),
    (0, 'edital')
]

# Convert training data to DataFrame
def create_dataframe(training_data):
    df = DataFrame(training_data, columns=['label', 'text'])
    return df

# Create DataFrame from training data
df_training_data = create_dataframe(training_data)

# Shuffle the DataFrame
df_training_data = shuffle(df_training_data)

# Train the model once and reuse it
model, vectorizer = train_model(df_training_data)

print('Model trained successfully!')

# Example usage
def process_url_links(url):
    soup = fetch_page(url)
    links = extract_links(soup)

    # Filter out links pointing to https://concursosnobrasil.com/ or links that don't start with 'https://'
    links = [(link, text) for link, text in links if not link.startswith('/') and 'concursosnobrasil.com' not in link]

    if not links:
        return []

    relevant_links = predict_relevant_links(model, vectorizer, links)

    return relevant_links

if __name__ == "__main__":
    url = 'https://concursosnobrasil.com/concursos/2024/12/09/concurso-icmbio-edital/'
    print(process_url_links(url))