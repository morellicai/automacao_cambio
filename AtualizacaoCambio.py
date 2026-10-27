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
            destinatarios=["ti01@inconelinox.com.br", "caiomorelli.it@gmail.com"],
            assunto="Automação: Atualizacao de Cambio - Concluido com Sucesso",
            corpo_html=f"""                
                <!DOCTYPE html>
                    <html lang="pt-BR" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <meta name="color-scheme" content="light dark">
                        <meta name="supported-color-schemes" content="light dark">
                        <!--[if mso]>
                        <noscript>
                            <xml>
                                <o:OfficeDocumentSettings>
                                    <o:PixelsPerInch>96</o:PixelsPerInch>
                                </o:OfficeDocumentSettings>
                            </xml>
                        </noscript>
                        <![endif]-->
                        <style>
                            :root {{
                                color-scheme: light dark;
                                supported-color-schemes: light dark;
                            }}
                        </style>
                    </head>
                    <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; word-spacing:normal; background-color: #f4f7f6;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f4f7f6; padding: 20px;">
                            <tr>
                                <td align="center">
                                    <!-- Tabela principal atuando como o container branco -->
                                    <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 8px; border-top: 4px solid #0052cc; max-width: 600px;">
                                        <tr>
                                            <td style="padding: 30px;">
                                                
                                                <h2 style="color: #0052cc; margin-top: 0; font-size: 22px;">Atualização de Câmbio</h2>
                                                
                                                <p style="font-size: 16px; line-height: 1.6; color: #333333;">
                                                    A atualização das taxas de câmbio foi finalizada com <strong style="color: #2e7d32;">sucesso</strong>. Confira os valores atualizados abaixo:
                                                </p>
                                                
                                                <!-- Tabela de dados -->
                                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top: 25px; margin-bottom: 25px;">
                                                    <tr>
                                                        <td style="padding: 12px 15px; border-bottom: 1px solid #eeeeee; font-weight: bold; width: 60%; color: #333333;">
                                                           🇺🇸 Taxa Dólar (USD)
                                                        </td>
                                                        <td align="right" style="padding: 12px 15px; border-bottom: 1px solid #eeeeee; font-weight: bold; color: #0052cc; font-size: 16px;">
                                                            R$ {dados[0][1]:.2f}
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 12px 15px; border-bottom: 1px solid #eeeeee; font-weight: bold; color: #333333;">
                                                            🇪🇺 Taxa Euro (EUR)
                                                        </td>
                                                        <td align="right" style="padding: 12px 15px; border-bottom: 1px solid #eeeeee; font-weight: bold; color: #0052cc; font-size: 16px;">
                                                            R$ {dados[1][1]:.2f}
                                                        </td>
                                                    </tr>
                                                </table>
                                                
                                                <hr style="border: none; border-top: 1px solid #eeeeee; margin: 30px 0;">
                                                
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </body>
                    </html>
                    """,
        )
