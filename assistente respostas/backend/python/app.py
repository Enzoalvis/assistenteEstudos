from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import os
import torch
from transformers import pipeline

# Configuração do Flask
app = Flask(__name__)
CORS(app, resources={r"/api/assistant": {"origins": "*"}})  # Controle de acesso

# Token de segurança para autenticação da API
SECRET_TOKEN = "17d6d044add2d7db205835a9e11753532e0cb5cc039f4633cb60847f0c432419"

# Carregando IA pré-treinada para responder perguntas
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# Matérias escolares suportadas
MATERIAS = [
    "matemática", "física", "química", "biologia", "história",
    "geografia", "português", "literatura", "filosofia", "sociologia",
    "inglês", "espanhol", "redação", "arte"
]

# Respostas pré-definidas para perguntas genéricas
RESPOSTAS_PADRAO = {
    "oi": "Olá! Como posso te ajudar hoje?",
    "quem é você": "Sou um assistente escolar programado para ajudar em várias matérias.",
    "obrigado": "De nada! Sempre que precisar, estarei aqui.",
    "tchau": "Até logo! Bons estudos!"
}

# Função de segurança para sanitizar entrada do usuário
def sanitizar_entrada(texto):
    # Remove caracteres suspeitos
    texto = re.sub(r"[^\w\s\?\!.,]", "", texto)
    # Limita o tamanho da entrada
    return texto[:300]  # Máximo de 300 caracteres

# Rota principal do assistente
@app.route('/api/assistant', methods=['POST'])
def assistant():
    # Verifica se o request tem o token de segurança
    token = request.headers.get("Authorization")
    if not token or token != f"Bearer {SECRET_TOKEN}":
        return jsonify({"error": "Acesso negado"}), 403

    # Recebe os dados da requisição
    data = request.get_json()
    user_input = data.get('input', '').strip().lower()

    # Sanitiza a entrada do usuário
    user_input = sanitizar_entrada(user_input)

    # Verifica se a entrada está vazia
    if not user_input:
        return jsonify({"response": "Por favor, digite uma pergunta válida."})

    # Verifica se é uma pergunta comum e responde de forma direta
    for chave, resposta in RESPOSTAS_PADRAO.items():
        if chave in user_input:
            return jsonify({"response": resposta})

    # Verifica se a pergunta envolve alguma matéria
    materia_detectada = next((m for m in MATERIAS if m in user_input), None)
    
    # Se for sobre uma matéria, a IA gera uma explicação + resposta
    if materia_detectada:
        contexto = f"Explique o conceito de {materia_detectada} de forma simples."
        resposta_ia = qa_pipeline({"question": user_input, "context": contexto})
        resposta_texto = resposta_ia['answer']

        return jsonify({
            "response": f"Aqui está uma explicação sobre {materia_detectada}: {resposta_texto}"
        })

    # Se a pergunta não estiver clara, peça mais detalhes
    return jsonify({"response": "Poderia reformular sua pergunta para que eu possa te ajudar melhor?"})

# Inicia o servidor Flask
if __name__ == '__main__':
    app.run(port=5000, debug=True)
