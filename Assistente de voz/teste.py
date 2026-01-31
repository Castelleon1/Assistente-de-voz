from assistente import *
import unittest
import torch

GERAR_RELATORIO = "tests/audio/gerar_relatorio.wav"
REGISTRAR_DESPESA = "tests/audio/registrar_despesa.wav"
VERIFICAR_SALDO = "tests/audio/verificar_saldo.wav"
MOSTRAR_INVESTIMENTOS = "tests/audio/mostrar_investimentos.wav"

class TestesFinanceiro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
        cls.iniciado, cls.processador, cls.modelo, _, cls.palavras_de_parada, cls.acoes = iniciar(cls.dispositivo)
    
    def testar_modelo_iniciado(self):
        self.assertTrue(self.iniciado)
    
    def testar_gerar_relatorio(self):
        fala = carregar_fala(GERAR_RELATORIO)
        transcricao = transcrever_fala(self.dispositivo, fala, self.modelo, self.processador)
        comando = processar_transcricao(transcricao, self.palavras_de_parada)
        valido, acao, disp = validar_comando(comando, self.acoes)
        self.assertTrue(valido)
        self.assertEqual(acao, "gerar")
    
    def testar_registrar_despesa(self):
        fala = carregar_fala(REGISTRAR_DESPESA)
        transcricao = transcrever_fala(self.dispositivo, fala, self.modelo, self.processador)
        comando = processar_transcricao(transcricao, self.palavras_de_parada)
        valido, acao, disp = validar_comando(comando, self.acoes)
        self.assertTrue(valido)
        self.assertEqual(acao, "registrar")
    
    def testar_verificar_saldo(self):
        fala = carregar_fala(VERIFICAR_SALDO)
        transcricao = transcrever_fala(self.dispositivo, fala, self.modelo, self.processador)
        comando = processar_transcricao(transcricao, self.palavras_de_parada)
        valido, acao, disp = validar_comando(comando, self.acoes)
        self.assertTrue(valido)
        self.assertEqual(acao, "verificar")
    
    def testar_mostrar_investimentos(self):
        fala = carregar_fala(MOSTRAR_INVESTIMENTOS)
        transcricao = transcrever_fala(self.dispositivo, fala, self.modelo, self.processador)
        comando = processar_transcricao(transcricao, self.palavras_de_parada)
        valido, acao, disp = validar_comando(comando, self.acoes)
        self.assertTrue(valido)
        self.assertEqual(acao, "mostrar")

if __name__ == "__main__":
    unittest.main()