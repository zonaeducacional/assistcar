import flask
from flask import request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import random

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

# Esta é uma URL de exemplo de um site de classificados fictício.
# A estrutura HTML é simulada para ser parecida com a de um site real.
# Num projeto final, você substituiria esta URL pela do site que deseja raspar.
EXAMPLE_URL = "http://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"

@app.route('/api/scrape', methods=['POST'])
def scrape():
    # Obtém os dados da pesquisa enviados pelo frontend
    search_data = request.json
    print(f"Recebido pedido de pesquisa para: {search_data}")

    try:
        # --- MOTOR DE RASPAGEM REAL ---
        # 1. Fazer o pedido HTTP para o site alvo.
        #    Numa aplicação real, você construiria a URL com base nos dados da pesquisa.
        #    Exemplo: f"https://www.sitealvo.com/carros?marca={search_data['brand']}"
        response = requests.get(EXAMPLE_URL, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status() # Lança um erro se o pedido falhar

        # 2. Analisar o conteúdo HTML da página.
        soup = BeautifulSoup(response.content, 'html.parser')

        # 3. Encontrar os elementos que contêm os anúncios.
        #    Esta é a parte que exige investigação com a ferramenta "Inspecionar" do navegador.
        #    Neste site de exemplo, cada "anúncio" está dentro de uma div com a classe "thumbnail".
        anuncios = soup.find_all('div', class_='thumbnail')

        carros_encontrados = []
        nomes = ["Carlos Silva", "Mariana Costa", "Roberto Almeida", "Fernanda Lima", "Jorge Santos", "Ana Pereira", "Lucas Martins"]

        for anuncio in anuncios:
            # 4. Extrair as informações de cada anúncio.
            #    Novamente, as tags e classes são específicas do site alvo.
            titulo_tag = anuncio.find('a', class_='title')
            preco_tag = anuncio.find('h4', class_='pull-right')
            
            # Verifica se as tags foram encontradas antes de tentar aceder aos seus atributos
            if titulo_tag and preco_tag:
                titulo = titulo_tag.get('title')
                preco = preco_tag.text

                # Simulação dos outros dados, já que o site de exemplo não os tem
                vendedor_info = random.choice(nomes)

                carro = {
                    "id": str(random.randint(1000, 9999)),
                    "titulo": titulo,
                    "preco": preco,
                    "ano_km": f"{search_data.get('year', 2021)} | {random.randint(15, 80)}000 Km",
                    "localizacao": search_data.get('location', "Brasil"),
                    "vendedor": vendedor_info,
                    "telefone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    "email": f"{vendedor_info.split(' ')[0].lower()}@emailficticio.com",
                    "imageUrl": "https://placehold.co/600x400/7d7dce/ffffff?text=Carro+Real",
                    "youtubeSearchTerm": f"review {titulo}"
                }
                carros_encontrados.append(carro)

        # Limita a 5 resultados para não sobrecarregar
        return jsonify(carros_encontrados[:5])

    except requests.exceptions.RequestException as e:
        print(f"Erro de rede ao aceder ao site: {e}")
        return jsonify({"error": "Não foi possível aceder ao site de classificados."}), 500
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a raspagem: {e}")
        return jsonify({"error": "Ocorreu um erro ao processar os dados."}), 500

if __name__ == '__main__':
    app.run(debug=True)

