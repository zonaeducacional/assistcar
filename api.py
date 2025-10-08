import flask
from flask import request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import random
import time

# Importa as ferramentas do Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

@app.route('/api/scrape', methods=['POST'])
def scrape():
    search_data = request.json
    print(f"Recebido pedido de pesquisa para: {search_data}")

    # --- Configuração do Selenium (O "Pesquisador Paciente") ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa o Chrome sem abrir uma janela visual
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Instala e gere o driver do Chrome automaticamente
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        base_url = "https://www.webmotors.com.br/carros/usados/bahia/salvador"
        marca = search_data.get('brand', '').lower()
        modelo = search_data.get('model', '').lower()
        url_pesquisa = f"{base_url}/{marca}/{modelo}"
        
        print(f"A aceder à URL com o Selenium: {url_pesquisa}")

        # O Selenium abre o navegador e vai para a página
        driver.get(url_pesquisa)
        
        # Espera pacientemente 5 segundos para que o JavaScript carregue os anúncios
        time.sleep(5) 
        
        # Agora que tudo carregou, pegamos o HTML completo
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # O resto do código é o mesmo, pois agora ele tem o HTML completo para analisar
        anuncios = soup.find_all('a', class_='vehicle-card-oem-desktop_Link__q4YEd')
        
        if not anuncios:
            print("Nenhum anúncio encontrado. O site pode ter alterado a sua estrutura ou bloqueado o acesso.")

        carros_encontrados = []
        for anuncio in anuncios:
            titulo_tag = anuncio.find('p', class_='_web-title-medium_qtpsh__51')
            titulo = titulo_tag.text.strip() if titulo_tag else "Título não encontrado"

            preco_tag = anuncio.find('strong', attrs={'data-testid': 'price-value'})
            preco = preco_tag.text.strip() if preco_tag else "Preço a consultar"

            # A estrutura do Webmotors agrupa ano e km num único elemento
            info_tags = anuncio.find_all('span', class_='sc-f206734a-2')
            ano_km = "Não informado"
            if len(info_tags) > 0:
                ano_km = ' | '.join(tag.text.strip() for tag in info_tags)
            
            localizacao = "Salvador, BA" # A localização está na URL, podemos assumi-la

            imagem_tag = anuncio.find('img')
            imageUrl = imagem_tag['src'] if imagem_tag and 'src' in imagem_tag.attrs else "https://placehold.co/600x400/cccccc/ffffff?text=Imagem+N/D"

            nomes = ["Carlos Silva", "Mariana Costa", "Roberto Almeida"]
            vendedor_info = random.choice(nomes)

            carro = {
                "id": str(random.randint(1000, 9999)),
                "titulo": titulo,
                "preco": preco,
                "ano_km": ano_km,
                "localizacao": localizacao,
                "vendedor": vendedor_info,
                "telefone": f"(71) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                "email": f"{vendedor_info.split(' ')[0].lower()}@emailficticio.com",
                "imageUrl": imageUrl,
                "youtubeSearchTerm": f"review {titulo}"
            }
            carros_encontrados.append(carro)

        return jsonify(carros_encontrados)

    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a raspagem: {e}")
        return jsonify({"error": f"Ocorreu um erro ao processar os dados: {e}"}), 500
    finally:
        # Garante que o navegador é fechado no final, mesmo que ocorra um erro
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)

