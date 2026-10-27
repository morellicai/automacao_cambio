from datetime import date, timedelta

import requests


class BuscaPtaxVenda:
    def __init__(self):
        self.data_util_mais_recente = self.data_util_mais_recente

    def data_util_mais_recente(self):
        """Retorna a data útil mais recente (pula fim de semana)."""
        hoje = date.today()
        if hoje.weekday() == 5:  # sábado → sexta
            return hoje - timedelta(days=1)
        elif hoje.weekday() == 6:  # domingo → sexta
            return hoje - timedelta(days=2)
        return hoje

    def buscar_ptax_venda(self, moeda):
        """Busca a cotação de VENDA (PTAX fechamento) do Banco Central."""
        data_ref = self.data_util_mais_recente()
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
            raise RuntimeError(
                f"PTAX de {moeda} ainda nao disponivel para {data_ref.strftime('%d/%m/%Y')}. "
                f"Tente novamente apos as 18h."
            )

        # Pega o ultimo boletim do dia (fechamento = PTAX oficial)
        taxa_venda = dados[-1]["cotacaoVenda"]
        print(
            f"  Taxa obtida : {moeda} = R$ {taxa_venda:.4f}  "
            f"(ref. {data_ref.strftime('%d/%m/%Y')} - PTAX Venda)"
        )
        return moeda, taxa_venda
