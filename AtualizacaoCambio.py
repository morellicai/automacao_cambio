import os
from datetime import datetime, time

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
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                </head>
                <body style="font-family: Arial, sans-serif; background-color: #f4f7f6; padding: 20px; color: #333333; margin: 0;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 4px solid #0052cc;">
                        
                        <h2 style="color: #0052cc; margin-top: 0; font-size: 22px;">Atualização de Câmbio</h2>
                        
                        <p style="font-size: 16px; line-height: 1.6; color: #555555;">
                            A atualização das taxas de câmbio foi finalizada com <strong style="color: #2e7d32;">sucesso</strong>. Confira os valores atualizados abaixo:
                        </p>
                        
                        <table style="width: 100%; border-collapse: collapse; margin-top: 25px; margin-bottom: 25px;">
                            <tr>
                                <td style="padding: 12px 15px; border-bottom: 1px solid #eeeeee; font-weight: bold; background-color: #f9f9f9; width: 60%;">
                                    🇺🇸 Taxa Dólar (USD)
                                </td>
                                <td style="padding: 12px 15px; border-bottom: 1px solid #eeeeee; text-align: right; font-weight: bold; color: #0052cc; font-size: 16px;">
                                    R$ {dados[0][1]:.4f}
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 12px 15px; border-bottom: 1px solid #eeeeee; font-weight: bold; background-color: #f9f9f9;">
                                    🇪🇺 Taxa Euro (EUR)
                                </td>
                                <td style="padding: 12px 15px; border-bottom: 1px solid #eeeeee; text-align: right; font-weight: bold; color: #0052cc; font-size: 16px;">
                                    R$ {dados[1][1]:.4f}
                                </td>
                            </tr>
                        </table>
                        
                        <hr style="border: none; border-top: 1px solid #eeeeee; margin: 30px 0;">
                        
                        <p style="font-size: 12px; color: #999999; text-align: center; margin: 0;">
                            Mensagem gerada automaticamente pelo sistema.<br>Por favor, não responda a este e-mail.
                        </p>
                    </div>
                </body>
                </html>
                """,
        )
