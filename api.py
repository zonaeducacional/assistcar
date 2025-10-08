import flask
from flask import request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import uuid

app = flask.Flask(__name__)
CORS(app) 

# Rota principal para a raspagem de dados
@app.route('/api/scrape', methods=['POST'])
def scrape():
    search_data = request.get_json()
    
    brand = search_data.get('brand', 'carro')
    model = search_data.get('model', '')
    location = search_data.get('location', 'brasil')
    
    print(f"Recebido pedido de busca para: {brand} {model} em {location}")

    # --- SIMULAÇÃO DA RASPAGEM ---
    # A lógica de raspagem real de um site específico entraria aqui.
    # Por agora, estamos a devolver dados fictícios para que a aplicação funcione.
    
    try:
        # A função que gera os dados fictícios foi movida para aqui
        mock_cars = generate_mock_data(search_data)
        
        # Simulando um pequeno atraso, como se estivéssemos a aceder a um site real
        import time
        time.sleep(1.5)

        print(f"Busca concluída. Encontrados {len(mock_cars)} carros.")
        return jsonify(mock_cars)

    except Exception as e:
        print(f"Ocorreu um erro durante a busca: {e}")
        return jsonify({"error": "Falha ao buscar os dados. Verifique o servidor."}), 500


# Função para gerar dados fictícios (mock data)
def generate_mock_data(search_data):
    mock_cars = []
    nomes = ["Carlos Silva", "Mariana Costa", "Roberto Almeida", "Fernanda Lima", "Jorge Santos"]
    for i in range(5):
        mock_cars.append({
            "id": str(uuid.uuid4()),
            "titulo": f"{search_data.get('brand', 'Marca')} {search_data.get('model', 'Modelo')} 2.0",
            "preco": f"R$ {(70000 + i * 3500):.2f}".replace('.',','),
            "ano_km": f"{search_data.get('year', 2021)} | {50000 - i * 4000} Km",
            "localizacao": search_data.get('location', "Qualquer Lugar"),
            "vendedor": nomes[i],
            "telefone": f"(71) 9{8800 + i*11}-{1000 + i*22}",
            "email": f"{nomes[i].split(' ')[0].lower()}@emailficticio.com",
            "imageUrl": f"https://placehold.co/600x400/7c7ee8/ffffff?text={search_data.get('brand', 'Carro')}+{i+1}",
            "youtubeSearchTerm": f"review {search_data.get('brand', 'Marca')} {search_data.get('model', 'Modelo')}"
        })
    return mock_cars


if __name__ == '__main__':
    app.run(debug=True, port=5000)

