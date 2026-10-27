import requests


def api_esta_online():
    url_teste = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    try:
        # Faz uma requisição rápida esperando no máximo 5 segundos
        resposta = requests.get(url_teste, timeout=5)
        # Retorna True apenas se o servidor disser "200 OK"
        return resposta.status_code == 200
    except requests.exceptions.RequestException:
        return False


if api_esta_online():
    print("API online! Iniciando extração do câmbio...")
else:
    print("API do Banco Central está fora do ar. Tentaremos novamente mais tarde.")
