import flask
from flask import request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import random

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

@app.route('/api/scrape', methods=['POST'])
def scrape():
    search_data = request.json
    print(f"Recebido pedido de pesquisa para: {search_data}")

    try:
        # --- PASSO 1: CONSTRUIR A URL DE PESQUISA ---
        # A URL base do Webmotors para carros usados em Salvador, BA.
        # Você pode adaptar esta URL para outras cidades ou estados.
        # Os parâmetros `marca` e `modelo` são adicionados dinamicamente.
        base_url = "https://www.webmotors.com.br/carros/usados/bahia/salvador"
        marca = search_data.get('brand', '').lower()
        modelo = search_data.get('model', '').lower()
        url_pesquisa = f"{base_url}/{marca}/{modelo}"
        
        print(f"A aceder à URL: {url_pesquisa}")

        response = requests.get(url_pesquisa, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # --- PASSO 2: ENCONTRAR OS ANÚNCIOS ---
        # Com base na sua investigação, cada anúncio está dentro de uma tag <a>
        # com a classe "vehicle-card-oem-desktop_Link__q4YEd".
        anuncios = soup.find_all('a', class_='vehicle-card-oem-desktop_Link__q4YEd')
        
        if not anuncios:
            print("Nenhum anúncio encontrado com os seletores fornecidos.")

        carros_encontrados = []
        
        for anuncio in anuncios:
            # --- PASSO 3: EXTRAIR OS DADOS DE CADA ANÚNCIO ---
            
            # TÍTULO (Confirmado pela sua investigação)
            titulo_tag = anuncio.find('p', class_='_web-title-medium_qtpsh__51')
            titulo = titulo_tag.text.strip() if titulo_tag else "Título não encontrado"

            # PREÇO (Precisa de ser investigado)
            # Use o "Inspecionar" para encontrar a tag e a classe do preço
            preco_tag = anuncio.find('strong', attrs={'data-testid': 'price-value'})
            preco = preco_tag.text.strip() if preco_tag else "Preço a consultar"

            # ANO/KM (Precisa de ser investigado)
            ano_km_tag = anuncio.find('div', class_='sc-f206734a-1') # Exemplo, a classe real pode ser outra
            ano_km = ano_km_tag.text.strip() if ano_km_tag else "Não informado"
            
            # LOCALIZAÇÃO (Precisa de ser investigado)
            local_tag = anuncio.find('span', class_='sc-f206734a-2') # Exemplo, a classe real pode ser outra
            localizacao = local_tag.text.strip() if local_tag else "Não informada"

            # IMAGEM (Precisa de ser investigado)
            # A imagem principal está geralmente numa tag <img>
            imagem_tag = anuncio.find('img')
            imageUrl = imagem_tag['src'] if imagem_tag and imagem_tag.has_attr('src') else "https://placehold.co/600x400/cccccc/ffffff?text=Imagem+N/D"

            # Vendedor (Estes dados geralmente estão na página de detalhe do anúncio,
            # o que exigiria um segundo passo de raspagem. Por agora, simulamos.)
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

    except requests.exceptions.RequestException as e:
        print(f"Erro de rede ao aceder ao site: {e}")
        return jsonify({"error": "Não foi possível aceder ao site de classificados."}), 500
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a raspagem: {e}")
        return jsonify({"error": f"Ocorreu um erro ao processar os dados: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)

