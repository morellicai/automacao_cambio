import os
from datetime import date, datetime, time, timedelta

import requests
import urllib3
from dotenv import load_dotenv

from services.busca_ptax_venda import BuscaPtaxVenda
from services.email_service import NotificadorEmail
from services.login_logout_sap import AtualizaTaxa, LoginLogoutSap
from services.test_api import api_esta_online

load_dotenv()

SAP_URL = os.getenv("SAP_URL")
SAP_DB = os.getenv("SAP_DB")
SAP_USER = os.getenv("SAP_USER")
SAP_PASS = os.getenv("SAP_PASS")

MOEDAS = ["USD", "EUR"]

urllib3.disable_warnings()


def data_util_mais_recente():
    """Retorna a data útil mais recente (pula fim de semana)."""
    hoje = date.today()
    if hoje.weekday() == 5:  # sábado → sexta
        return hoje - timedelta(days=1)
    elif hoje.weekday() == 6:  # domingo → sexta
        return hoje - timedelta(days=2)
    return hoje


# ── Execucao principal ──────────────────────────────────────

hour = datetime.now().hour
login_logout_SAP = LoginLogoutSap()
email = NotificadorEmail()
atualiza_taxa = AtualizaTaxa()
busca_ptax_venda = BuscaPtaxVenda()

if hour >= 15:
    separador = "=" * 50

    while not api_esta_online():
        email.enviar(
            destinatarios=["ti01@inconelinox.com.br"],
            assunto="Automação: Atualizacao de Cambio",
            corpo_html="<p>API do Banco Central está fora do ar. Tentaremos novamente mais tarde.</p>",
        )
        time.sleep(600)

    cookies = None
    dados = []
    erros = []

    try:
        cookies = login_logout_SAP.login_sap()
        email.enviar(
            destinatarios=["ti01@inconelinox.com.br"],
            assunto="Automação: Atualizacao de Cambio",
            corpo_html="<p>Login Realizado pela automação de moedas no SAP</p>",
        )

        for moeda in MOEDAS:
            print(f"[ {moeda} ]")
            try:
                m, t = busca_ptax_venda.buscar_ptax_venda(moeda)
                dados.append((m, t))
                atualiza_taxa.atualizar_taxa_sap(cookies, m, t)
            except (requests.RequestException, RuntimeError, ValueError, KeyError) as e:
                msg = f"AVISO — {moeda}: {e}"
                email.enviar(
                    destinatarios=["ti01@inconelinox.com.br"],
                    assunto="Automação: Atualizacao de Cambio",
                    corpo_html=msg,
                )
                erros.append(msg)

    except (requests.RequestException, RuntimeError, OSError, ValueError) as e:
        email.enviar(
            destinatarios=["ti01@inconelinox.com.br"],
            assunto="Automação: Atualizacao de Cambio",
            corpo_html=f"<p>Erro geral na atualizacao de cambio: {e!s}</p>",
        )
        erros.append(str(e))

    finally:
        if cookies:
            login_logout_SAP.logout_sap(cookies)
            email.enviar(
                destinatarios=["ti01@inconelinox.com.br"],
                assunto="Automação: Atualizacao de Cambio",
                corpo_html="<p>Logout Realizado no SAP</p>",
            )

    print(separador)
    if erros:
        print("  Concluido com avisos:")
        for e in erros:
            print(f"    - {e}")
        email.enviar(
            destinatarios=["ti01@inconelinox.com.br"],
            assunto="Automação: Atualizacao de Cambio - Concluido com Avisos",
            corpo_html="""
                <p>Atualizacao de cambio finalizada com avisos:</p>
                """
            + "".join(f"<p>{e!s}</p>" for e in erros)
            + """
            """,
        )
    else:
        email.enviar(
            destinatarios=["ti01@inconelinox.com.br"],
            assunto="Automação: Atualizacao de Cambio - Concluido com Sucesso",
            corpo_html=f"""
                <p>Atualizacao de cambio finalizada com sucesso.</p>
                <p>Taxa Dolar Atualizada: {dados[0]}</p>
                <p>Taxa Euro Atualizada: {dados[1]}</p>
            """,
        )
