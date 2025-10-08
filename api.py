import flask
from flask import request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import random
import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

@app.route('/api/scrape', methods=['POST'])
def scrape():
    search_data = request.json
    print(f"Recebido pedido de pesquisa para: {search_data}")

    # --- Configuração do Selenium para o Render ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # O Render irá instalar o Chrome através de um Buildpack.
    # Esta linha aponta o Selenium para a localização correta do Chrome.
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    # Esta linha aponta para o chromedriver que o Buildpack também instala.
    service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        base_url = "https://www.webmotors.com.br/carros/usados/bahia/salvador"
        marca = search_data.get('brand', '').lower()
        modelo = search_data.get('model', '').lower()
        url_pesquisa = f"{base_url}/{marca}/{modelo}"
        
        print(f"A aceder à URL com o Selenium no Render: {url_pesquisa}")

        driver.get(url_pesquisa)
        time.sleep(5) 
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        anuncios = soup.find_all('a', class_='vehicle-card-oem-desktop_Link__q4YEd')
        
        if not anuncios:
            print("Nenhum anúncio encontrado.")

        carros_encontrados = []
        for anuncio in anuncios:
            titulo_tag = anuncio.find('p', class_='_web-title-medium_qtpsh__51')
            titulo = titulo_tag.text.strip() if titulo_tag else "Título não encontrado"

            preco_tag = anuncio.find('strong', attrs={'data-testid': 'price-value'})
            preco = preco_tag.text.strip() if preco_tag else "Preço a consultar"

            info_tags = anuncio.find_all('span', class_='sc-f206734a-2')
            ano_km = ' | '.join(tag.text.strip() for tag in info_tags) if info_tags else "Não informado"
            
            localizacao = "Salvador, BA"

            imagem_tag = anuncio.find('img')
            imageUrl = imagem_tag['src'] if imagem_tag and 'src' in imagem_tag.attrs else "https://placehold.co/600x400/cccccc/ffffff?text=Imagem+N/D"

            nomes = ["Carlos Silva", "Mariana Costa", "Roberto Almeida"]
            vendedor_info = random.choice(nomes)

            carro = {
                "id": str(random.randint(1000, 9999)),
                "titulo": titulo, "preco": preco, "ano_km": ano_km, "localizacao": localizacao,
                "vendedor": vendedor_info,
                "telefone": f"(71) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                "email": f"{vendedor_info.split(' ')[0].lower()}@emailficticio.com",
                "imageUrl": imageUrl, "youtubeSearchTerm": f"review {titulo}"
            }
            carros_encontrados.append(carro)

        return jsonify(carros_encontrados)

    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a raspagem: {e}")
        return jsonify({"error": f"Ocorreu um erro ao processar os dados: {e}"}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)

