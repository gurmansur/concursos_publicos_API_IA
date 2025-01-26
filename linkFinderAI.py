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
    article_body = soup.find('div', itemprop='articleBody')
    if article_body:
        for p_tag in article_body.find_all('p'):
            for a_tag in p_tag.find_all('a', href=True):
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
    (0, 'edital'),
    (1, 'As inscrições serão realizadas'),
    (0, 'O Comando da Aeronáutica'),
    (0, 'IBAMA'),
    (1, 'Inscrições abertas'),
    (1, 'Inscrições disponíveis'),
    (1, 'Inscrições online'),
    (1, 'Inscrições para o concurso'),
    (1, 'Inscrições para o processo seletivo'),
    (1, 'Inscrições para a seleção'),
    (1, 'Inscrições para o vestibular'),
    (1, 'Inscrições para o exame'),
    (1, 'Inscrições para a prova'),
    (1, 'Inscrições para o curso'),
    (1, 'Inscrições para a capacitação'),
    (1, 'Inscrições para o treinamento'),
    (1, 'Inscrições para o evento'),
    (1, 'Inscrições para a palestra'),
    (1, 'Inscrições para o seminário'),
    (1, 'Inscrições para o workshop'),
    (1, 'Inscrições para a conferência'),
    (1, 'Inscrições para o simpósio'),
    (1, 'Inscrições para o congresso'),
    (1, 'Inscrições para o encontro'),
    (1, 'Inscrições para a reunião'),
    (1, 'Inscrições para a assembleia'),
    (1, 'Inscrições para a convenção'),
    (1, 'Inscrições para o fórum'),
    (1, 'Inscrições para o painel'),
    (1, 'Inscrições para a mesa-redonda'),
    (1, 'Inscrições para o debate'),
    (1, 'Inscrições para a discussão'),
    (1, 'Inscrições para a sessão'),
    (1, 'Inscrições para a audiência'),
    (1, 'Inscrições para a consulta'),
    (1, 'Inscrições para a entrevista'),
    (1, 'Inscrições para o cadastro'),
    (1, 'Inscrições para a matrícula'),
    (1, 'Inscrições para a adesão'),
    (1, 'Inscrições para a filiação'),
    (1, 'Inscrições para a inscrição'),
    (1, 'Inscrições para a participação'),
    (1, 'Inscrições para a candidatura'),
    (1, 'Inscrições para a aplicação'),
    (1, 'Inscrições para a submissão'),
    (1, 'Inscrições para a proposta'),
    (1, 'Inscrições para a oferta'),
    (1, 'Inscrições para a solicitação'),
    (1, 'Inscrições para a requisição'),
    (1, 'Inscrições para a demanda'),
    (1, 'Inscrições para a petição'),
    (1, 'Inscrições para a reivindicação'),
    (1, 'Inscrições para a reclamação'),
    (1, 'Inscrições para a queixa'),
    (1, 'Inscrições para a denúncia'),
    (1, 'Inscrições para a acusação'),
    (1, 'Inscrições para a defesa'),
    (1, 'Inscrições para a apelação'),
    (1, 'Inscrições para o recurso'),
    (1, 'Inscrições para a revisão'),
    (1, 'Inscrições para a retificação'),
    (1, 'Inscrições para a correção'),
    (1, 'Inscrições para a alteração'),
    (1, 'Inscrições para a modificação'),
    (1, 'Inscrições para a atualização'),
    (1, 'Inscrições para a renovação'),
    (1, 'Inscrições para a prorrogação'),
    (1, 'Inscrições para a extensão'),
    (1, 'Inscrições para a ampliação'),
    (1, 'Inscrições para a expansão'),
    (1, 'Inscrições para a diversificação'),
    (1, 'Inscrições para a especialização'),
    (1, 'Inscrições para a qualificação'),
    (1, 'Inscrições para a certificação'),
    (1, 'Inscrições para a habilitação'),
    (1, 'Inscrições para a autorização'),
    (1, 'Inscrições para a permissão'),
    (1, 'Inscrições para a concessão'),
    (1, 'Inscrições para a licença'),
    (1, 'Inscrições para a franquia'),
    (1, 'Inscrições para a patente'),
    (1, 'Inscrições para a marca registrada'),
    (1, 'Inscrições para o direito autoral'),
    (1, 'Inscrições para a propriedade intelectual'),
    (1, 'Inscrições para o registro'),
    (1, 'Inscrições para a inscrição no concurso'),
    (1, 'Inscrições para a inscrição no processo seletivo'),
    (1, 'Inscrições para a inscrição na seleção'),
    (1, 'Inscrições para a inscrição no vestibular'),
    (1, 'Inscrições para a inscrição no exame'),
    (1, 'Inscrições para a inscrição na prova'),
    (1, 'Inscrições para a inscrição no curso'),
    (1, 'Inscrições para a inscrição na capacitação'),
    (1, 'Inscrições para a inscrição no treinamento'),
    (1, 'Inscrições para a inscrição no evento'),
    (1, 'Inscrições para a inscrição na palestra'),
    (1, 'Inscrições para a inscrição no seminário'),
    (1, 'Inscrições para a inscrição no workshop'),
    (1, 'Inscrições para a inscrição na conferência'),
    (1, 'Inscrições para a inscrição no simpósio'),
    (1, 'Inscrições para a inscrição no congresso'),
    (1, 'Inscrições para a inscrição no encontro'),
    (1, 'Inscrições para a inscrição na reunião'),
    (1, 'Inscrições para a inscrição na assembleia'),
    (1, 'Inscrições para a inscrição na convenção'),
    (1, 'Inscrições para a inscrição no fórum'),
    (1, 'Inscrições para a inscrição no painel'),
    (1, 'Inscrições para a inscrição na mesa-redonda'),
    (1, 'Inscrições para a inscrição no debate'),
    (1, 'Inscrições para a inscrição na discussão'),
    (1, 'Inscrições para a inscrição na sessão'),
    (1, 'Inscrições para a inscrição na audiência'),
    (1, 'Inscrições para a inscrição na consulta'),
    (1, 'Inscrições para a inscrição na entrevista'),
    (1, 'Inscrições para a inscrição no cadastro'),
    (1, 'Inscrições para a inscrição na matrícula'),
    (1, 'Inscrições para a inscrição na adesão'),
    (1, 'Inscrições para a inscrição na filiação'),
    (1, 'Inscrições para a inscrição na inscrição'),
    (1, 'Inscrições para a inscrição na participação'),
    (1, 'Inscrições para a inscrição na candidatura'),
    (1, 'Inscrições para a inscrição na aplicação'),
    (1, 'Inscrições para a inscrição na submissão'),
    (1, 'Inscrições para a inscrição na proposta'),
    (1, 'Inscrições para a inscrição na oferta'),
    (1, 'Inscrições para a inscrição na solicitação'),
    (1, 'Inscrições para a inscrição na requisição'),
    (1, 'Inscrições para a inscrição na demanda'),
    (1, 'Inscrições para a inscrição na petição'),
    (1, 'Inscrições para a inscrição na reivindicação'),
    (1, 'Inscrições para a inscrição na reclamação'),
    (1, 'Inscrições para a inscrição na queixa'),
    (1, 'Inscrições para a inscrição na denúncia'),
    (1, 'Inscrições para a inscrição na acusação'),
    (1, 'Inscrições para a inscrição na defesa'),
    (1, 'Inscrições para a inscrição na apelação'),
    (1, 'Inscrições para a inscrição no recurso'),
    (1, 'Inscrições para a inscrição na revisão'),
    (1, 'Inscrições para a inscrição na retificação'),
    (1, 'Inscrições para a inscrição na correção'),
    (1, 'Inscrições para a inscrição na alteração'),
    (1, 'Inscrições para a inscrição na modificação'),
    (1, 'Inscrições para a inscrição na atualização'),
    (1, 'Inscrições para a inscrição na renovação'),
    (1, 'Inscrições para a inscrição na prorrogação'),
    (1, 'Inscrições para a inscrição na extensão'),
    (1, 'Inscrições para a inscrição na ampliação'),
    (1, 'Inscrições para a inscrição na expansão'),
    (1, 'Inscrições para a inscrição na diversificação'),
    (1, 'Inscrições para a inscrição na especialização'),
    (1, 'Inscrições para a inscrição na qualificação'),
    (1, 'Inscrições para a inscrição na certificação'),
    (1, 'Inscrições para a inscrição na habilitação'),
    (1, 'Inscrições para a inscrição na autorização'),
    (1, 'Inscrições para a inscrição na permissão'),
    (1, 'Inscrições para a inscrição na concessão'),
    (1, 'Inscrições para a inscrição na licença'),
    (1, 'Inscrições para a inscrição na franquia'),
    (1, 'Inscrições para a inscrição na patente'),
    (1, 'Inscrições para a inscrição na marca registrada'),
    (1, 'Inscrições para a inscrição no direito autoral'),
    (1, 'Inscrições para a inscrição na propriedade intelectual'),
    (1, 'Inscrições para o registro')
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

    links = [(link, text) for link, text in links if not link.startswith('/') and 'pciconcursos.com' not in link]

    if not links:
        return []

    relevant_links = predict_relevant_links(model, vectorizer, links)

    return relevant_links

if __name__ == "__main__":
    url = 'https://www.pciconcursos.com.br/noticias/aeronautica-anuncia-novo-processo-seletivo-para-o-curso-de-formacao-de-sargentos'
    print(process_url_links(url))