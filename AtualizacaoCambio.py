from datetime import time
import requests
import urllib3
import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from datetime import date, timedelta, datetime
from services.login_logout_sap import LoginLogoutSap
from services.email_service import NotificadorEmail
from services.test_api import api_esta_online

load_dotenv()

SAP_URL  = os.getenv("SAP_URL")
SAP_DB   = os.getenv("SAP_DB")
SAP_USER = os.getenv("SAP_USER")
SAP_PASS = os.getenv("SAP_PASS")

MOEDAS   = ["USD", "EUR"]

urllib3.disable_warnings()

def data_util_mais_recente():
    """Retorna a data útil mais recente (pula fim de semana)."""
    hoje = date.today()
    if hoje.weekday() == 5:    # sábado → sexta
        return hoje - timedelta(days=1)
    elif hoje.weekday() == 6:  # domingo → sexta
        return hoje - timedelta(days=2)
    return hoje

def buscar_ptax_venda(moeda):
    """Busca a cotação de VENDA (PTAX fechamento) do Banco Central."""
    data_ref = data_util_mais_recente()
    data_str = data_ref.strftime("%m-%d-%Y")

    url = (
        f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
        f"CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)"
        f"?@moeda='{moeda}'&@dataCotacao='{data_str}'&$format=json"
    )
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()

    dados = resp.json().get("value", [])
    if not dados:
        raise Exception(
            f"PTAX de {moeda} ainda nao disponivel para {data_ref.strftime('%d/%m/%Y')}. "
            f"Tente novamente apos as 18h."
        )

    # Pega o ultimo boletim do dia (fechamento = PTAX oficial)
    taxa_venda = dados[-1]["cotacaoVenda"]
    print(f"  Taxa obtida : {moeda} = R$ {taxa_venda:.4f}  "
          f"(ref. {data_ref.strftime('%d/%m/%Y')} - PTAX Venda)")
    return moeda, taxa_venda

def atualizar_taxa_sap(cookies, moeda, taxa):
    """Envia a taxa de cambio para o SAP B1."""
    hoje_sap = date.today().strftime("%Y%m%d")
    resp = requests.post(
        f"{SAP_URL}/SBOBobService_SetCurrencyRate",
        json={
            "Currency": moeda,
            "Rate": str(taxa),
            "RateDate": hoje_sap
        },
        cookies=cookies,
        verify=False,
        timeout=15
    )
    if resp.status_code not in [200, 204]:
        raise Exception(f"Erro ao atualizar {moeda} no SAP: {resp.text}")
        
    print(f"  {moeda} atualizado no SAP B1 com sucesso!")

# ── Execucao principal ──────────────────────────────────────

hour = datetime.now().hour
login_logout_SAP = LoginLogoutSap()
email = NotificadorEmail()

if hour >= 15:
    separador = "=" * 50

    while not api_esta_online():
        email.enviar(
            destinatarios=["ti01@inconelinox.com.br"], 
            assunto="Automação: Atualizacao de Cambio", 
            corpo_html="<p>API do Banco Central está fora do ar. Tentaremos novamente mais tarde.</p>"
        )
        time.sleep(600)

    cookies = None
    dados = []
    erros   = []

    try:
        cookies = login_logout_SAP.login_sap()
        email.enviar(
            destinatarios=["ti01@inconelinox.com.br"], 
            assunto="Automação: Atualizacao de Cambio", 
            corpo_html="<p>Login Realizado pela automação de moedas no SAP</p>"
        )

        for moeda in MOEDAS:
            print(f"[ {moeda} ]")
            try:
                m,t = buscar_ptax_venda(moeda)
                dados.append((m,t))
                atualizar_taxa_sap(cookies, m, t)
            except Exception as e:
                msg = f"AVISO — {moeda}: {e}"
                email.enviar(
                    destinatarios=["ti01@inconelinox.com.br"], 
                    assunto="Automação: Atualizacao de Cambio", 
                    corpo_html=msg
                )
                erros.append(msg)

    except Exception as e:
        email.enviar(
            destinatarios=["ti01@inconelinox.com.br"], 
            assunto="Automação: Atualizacao de Cambio", 
            corpo_html=f"<p>Erro geral na atualizacao de cambio: {str(e)}</p>"
        )
        erros.append(str(e))

    finally:
        if cookies:
            login_logout_SAP.logout_sap(cookies)
            email.enviar(
                destinatarios=["ti01@inconelinox.com.br"], 
                assunto="Automação: Atualizacao de Cambio", 
                corpo_html="<p>Logout Realizado no SAP</p>"
            )

    print(separador)
    if erros:
        print("  Concluido com avisos:")
        for e in erros:
            print(f"    - {e}")
        email.enviar(
            destinatarios=["ti01@inconelinox.com.br"], 
            assunto="Automação: Atualizacao de Cambio - Concluido com Avisos", 
            corpo_html=f"""
                <p>Atualizacao de cambio finalizada com avisos:</p>
                """ + "".join(f"<p>{str(e)}</p>" for e in erros) + """
            """
        )
    else:
        email.enviar(
            destinatarios=["ti01@inconelinox.com.br"], 
            assunto="Automação: Atualizacao de Cambio - Concluido com Sucesso", 
            corpo_html=f"""
                <p>Atualizacao de cambio finalizada com sucesso.</p>
                <p>Taxa Dolar Atualizada: {dados[0]}</p>
                <p>Taxa Euro Atualizada: {dados[1]}</p>
            """
        )