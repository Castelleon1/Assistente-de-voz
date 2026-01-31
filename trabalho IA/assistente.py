from flask import Flask, Response, request, send_from_directory
from nltk import word_tokenize, corpus
from inicializador_modelo import *
from threading import Thread
from transcritor import *
import secrets
import pyaudio
import wave
import json
import os
from financas import *

LINGUAGEM = "portuguese"
FORMATO = pyaudio.paInt16
CANAIS = 1
AMOSTRAS = 1024
TAXA_AMOSTRAGEM = 16000
TEMPO_GRAVACAO = 5
CAMINHO_AUDIO_FALAS = "C:\\Users\\joaov\\OneDrive\\Área de Trabalho\\trabalho IA\\temp"
CONFIGURACOES = "C:\\Users\\joaov\\OneDrive\\Área de Trabalho\\trabalho IA\\config.json"

MODO_LINHA_DE_COMANDO = 1
MODO_WEB = 2
MODO_DE_FUNCIONAMENTO = MODO_LINHA_DE_COMANDO  # ou MODO_WEB

def iniciar(dispositivo):
    modelo_iniciado, processador, modelo = iniciar_modelo(MODELOS[0], dispositivo)
    
    gravador = pyaudio.PyAudio()
    palavras_de_parada = set(corpus.stopwords.words(LINGUAGEM))
    
    with open(CONFIGURACOES, "r", encoding="utf-8") as arquivo_config:
        configuracoes = json.load(arquivo_config)
        acoes = configuracoes["acoes"]
        
        arquivo_config.close()
    
    return modelo_iniciado, processador, modelo, gravador, palavras_de_parada, acoes

def iniciar_atuadores():
    atuadores = []
    if iniciar_financas():
        atuadores.append({
            "nome": "finanças",
            "atuacao": atuar_sobre_financas
        })
    return atuadores

def capturar_fala(gravador):
    gravacao = gravador.open(format=FORMATO, channels=CANAIS, rate=TAXA_AMOSTRAGEM, input=True, frames_per_buffer=AMOSTRAS)
    print("Fale o comando financeiro...")
    fala = []
    for _ in range(0, int(TAXA_AMOSTRAGEM / AMOSTRAS * TEMPO_GRAVACAO)):
        fala.append(gravacao.read(AMOSTRAS))
    gravacao.stop_stream()
    gravacao.close()
    print("Fala capturada.")
    return fala

def gravar_fala(gravador, fala):
    gravado, arquivo = False, f"{CAMINHO_AUDIO_FALAS}\\{secrets.token_hex(8)}.wav"
    try:
        wav = wave.open(arquivo, "wb")
        wav.setnchannels(CANAIS)
        wav.setsampwidth(gravador.get_sample_size(FORMATO))
        wav.setframerate(TAXA_AMOSTRAGEM)
        wav.writeframes(b"".join(fala))
        wav.close()
        gravado = True
    except Exception as e:
        print(f"Erro gravando fala: {str(e)}")
    return gravado, arquivo

def processar_transcricao(transcricao, palavras_de_parada):
    tokens = word_tokenize(transcricao)
    return [t for t in tokens if t not in palavras_de_parada]

def validar_comando(comando, acoes):
    if len(comando) >= 2:
        acao = comando[0]
        dispositivo = comando[1]
        for acao_prevista in acoes:
            if acao == acao_prevista["nome"]:
                for disp in acao_prevista["dispositivos"]:
                    if disp in dispositivo:
                        return True, acao, dispositivo
    return False, None, None

def atuar(acao, dispositivo, atuadores):
    for atuador in atuadores:
        print(f"Executando '{acao} {dispositivo}' via {atuador['nome']}")
        Thread(target=atuador["atuacao"], args=[acao, dispositivo]).start()

def ativar_linha_de_comando():
    while True:
        fala = capturar_fala(gravador)
        gravado, arquivo = gravar_fala(gravador, fala)
        if not gravado:
            print("Erro gravando fala.")
            continue
        fala = carregar_fala(arquivo)
        transcricao = transcrever_fala(dispositivo, fala, modelo, processador)
        os.remove(arquivo)
        comando = processar_transcricao(transcricao, palavras_de_parada)
        print(f"Comando reconhecido: {comando}")
        valido, acao, alvo = validar_comando(comando, acoes)
        if valido:
            atuar(acao, alvo, atuadores)
        else:
            print("Comando não reconhecido.")


servico = Flask("assistente_financeiro", static_folder="public")

@servico.post("/reconhecer_comando")
def reconhecer_comando():
    if "fala" not in request.files:
        return Response(status=400)
    fala = request.files["fala"]
    caminho_arquivo = f"{CAMINHO_AUDIO_FALAS}/{secrets.token_hex(8)}.wav"
    fala.save(caminho_arquivo)
    try:
        transcricao = transcrever_fala(servico.config["dispositivo"], carregar_fala(caminho_arquivo), servico.config["modelo"], servico.config["processador"])
        comando = processar_transcricao(transcricao, servico.config["palavras_de_parada"])
        valido, acao, alvo = validar_comando(comando, servico.config["acoes"])
        if valido:
            atuar(acao, alvo, servico.config["atuadores"])
        return Response(json.dumps({"transcricao": transcricao}), status=200)
    except:
        return Response(json.dumps({"transcricao": "Comando não reconhecido"}), status=200)
    finally:
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)

def ativar_web(dispositivo, modelo, processador, palavras_de_parada, acoes, atuadores):
    servico.config.update({
        "dispositivo": dispositivo,
        "modelo": modelo,
        "processador": processador,
        "palavras_de_parada": palavras_de_parada,
        "acoes": acoes,
        "atuadores": atuadores
    })
    servico.run(host="0.0.0.0", port=7001)

if __name__ == "__main__":
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    iniciado, processador, modelo, gravador, palavras_de_parada, acoes = iniciar(dispositivo)
    if iniciado:
        atuadores = iniciar_atuadores()
        if MODO_DE_FUNCIONAMENTO == MODO_LINHA_DE_COMANDO:
            ativar_linha_de_comando()
        else:
            ativar_web(dispositivo, modelo, processador, palavras_de_parada, acoes, atuadores)
    else:
        print("Erro de inicialização.")