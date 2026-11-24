"""03 — Que regiões mudaram mais face ao mesmo mês do ano anterior?
Fonte: atendimentos-em-urgencia-triagem-manchester (região tal como publicada pelo SNS)."""
import json
import pathlib
from collections import defaultdict

from comum import COL_COR, MAN, gravar, ler, mensal, ultimo_mes

linhas = ler(MAN)
mes, regiao = mensal(linhas, list(COL_COR.values()))
ult = ultimo_mes(linhas)
hom = f"{int(ult[:4]) - 1}{ult[4:]}"

# Confirma que nenhuma instituição mudou de região entre os dois meses
for (t, i) in mes:
    if t == ult:
        assert regiao[(t, i)] == regiao[(hom, i)], f"{i} mudou de região"

tot = {ult: defaultdict(int), hom: defaultdict(int)}
for (t, i), v in mes.items():
    if t in tot:
        tot[t][regiao[(t, i)]] += sum(v.values())

NOMES = {"Região de Saúde Norte": "Norte", "Região de Saúde do Centro": "Centro", "Região de Saúde LVT": "Lisboa e Vale do Tejo",
         "Região de Saúde do Alentejo": "Alentejo", "Região de Saúde do Algarve": "Algarve"}
out, tabela = {}, []
total_ult = sum(tot[ult].values())
for r in sorted(tot[ult], key=lambda r: -tot[ult][r]):
    var = round(100 * (tot[ult][r] - tot[hom][r]) / tot[hom][r], 1)
    peso = round(100 * tot[ult][r] / total_ult, 1)
    curto = NOMES.get(r, r)
    chave = curto.lower().replace(" ", "_")
    print(f"{curto:22s} {tot[hom][r]:>8d} {tot[ult][r]:>8d} {var:6.1f} %  peso {peso} %")
    out[f"reg_{chave}_ult"] = (tot[ult][r], f"Atendimentos {curto}, {ult}")
    out[f"reg_{chave}_hom"] = (tot[hom][r], f"Atendimentos {curto}, {hom}")
    out[f"reg_{chave}_var"] = (var, f"Variação % {curto}, {ult} vs {hom}")
    if var < 0:
        out[f"reg_{chave}_queda"] = (abs(var), f"Descida % de {curto} (valor absoluto), {ult} vs {hom}")
    out[f"reg_{chave}_peso"] = (peso, f"Peso % de {curto} no total nacional, {ult}")
    tabela.append([curto, tot[hom][r], tot[ult][r], var, peso])
gravar("03_regioes.py", out)
(pathlib.Path(__file__).parent / "tabela_regioes.json").write_text(json.dumps(tabela, ensure_ascii=False))
