from time import sleep

def iniciar_financas():
    print("[FINANÇAS] Sistema financeiro inicializado.")
    return True

def atuar_sobre_financas(acao, dispositivo):
    if acao == "gerar" and "relatório" in dispositivo:
        print("[FINANÇAS] Gerando relatório financeiro...")
        sleep(1)
        print("Despesas: R$ 1.250,00 | Receitas: R$ 3.000,00 | Saldo: R$ 1.750,00")
    
    elif acao == "registrar" and "despesa" in dispositivo:
        print("[FINANÇAS] Registrando nova despesa...")
        sleep(1)
        print("Despesa registrada com sucesso!")
    
    elif acao == "verificar" and "saldo" in dispositivo:
        print("[FINANÇAS] Verificando saldo disponível...")
        sleep(1)
        print("Saldo atual: R$ 1.750,00")
    
    elif acao == "mostrar" and "investimentos" in dispositivo:
        print("[FINANÇAS] Exibindo status dos investimentos...")
        sleep(1)
        print("Ações: 30%, Tesouro Direto: +30%, Criptomoedas: 5%, Fundos imobiliário: 35%")
    
    else:
        print("[FINANÇAS] Ação não reconhecida ou incompatível.")