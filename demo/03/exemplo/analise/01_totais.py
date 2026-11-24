"""01 — Quantos atendimentos no último mês e como compara com o mesmo mês do ano anterior?
Fonte única do total: atendimentos-em-urgencia-triagem-manchester (todas as cores + sem triagem)."""
import json
from collections import defaultdict

from comum import COL_COR, MAN, gravar, ler, mensal, rotulo, ultimo_mes, mes_anterior

linhas = ler(MAN)
cols = list(COL_COR.values())
mes, regiao = mensal(linhas, cols)
ult = ultimo_mes(linhas)
homologo = f"{int(ult[:4]) - 1}{ult[4:]}"

# Instituições por mês e valores mensais negativos (correções) — controlo de qualidade
inst = defaultdict(set)
negativos = 0
total = defaultdict(int)
for (t, i), v in mes.items():
    inst[t].add(i)
    s = sum(v.values())
    negativos += s < 0
    total[t] += s
print(f"Último mês: {ult}; instituições: {len(inst[ult])}; homólogo {homologo}: {len(inst[homologo])}")
print(f"Instituições-mês com total mensal negativo: {negativos}")
assert {i for (t, i) in mes if t == ult} == {i for (t, i) in mes if t == homologo}, "conjuntos diferentes"

# Série de 13 meses
serie = []
m = ult
for _ in range(13):
    serie.append(m)
    m = mes_anterior(m)
serie.reverse()
for m in serie:
    print(rotulo(m), total[m])

var = round(100 * (total[ult] - total[homologo]) / total[homologo], 1)
# Acumulado jan–último mês: é o valor publicado no último mês (dataset acumulado)
acum = defaultdict(int)
for r in linhas:
    if r["tempo"] in (ult, homologo):
        acum[r["tempo"]] += sum(int(float(r[c] or 0)) for c in cols)
var_acum = round(100 * (acum[ult] - acum[homologo]) / acum[homologo], 1)
media_dia = round(total[ult] / 31)
print(f"{ult}: {total[ult]}  {homologo}: {total[homologo]}  variação {var} %")
print(f"Jan–{ult}: {acum[ult]}  Jan–{homologo}: {acum[homologo]}  variação {var_acum} %")
print(f"Média diária {ult}: {media_dia}")

gravar("01_totais.py", {
    "total_ult": (total[ult], f"Atendimentos em urgência, {ult}, todo o país (mensal, cores + sem triagem)"),
    "total_homologo": (total[homologo], f"Atendimentos em urgência, {homologo}, todo o país"),
    "var_total_pct": (var, f"Variação % {ult} vs {homologo}"),
    "dif_total": (total[ult] - total[homologo], f"Diferença absoluta {ult} − {homologo}"),
    "acum_ult": (acum[ult], f"Atendimentos acumulados jan–{ult}"),
    "acum_homologo": (acum[homologo], f"Atendimentos acumulados jan–{homologo}"),
    "var_acum_pct": (var_acum, f"Variação % acumulado jan–ago, {ult[:4]} vs {homologo[:4]}"),
    "queda_acum_pct": (abs(var_acum), "Valor absoluto da variação % do acumulado (para escrever 'desce X %')"),
    "media_dia_ult":(media_dia, f"Média diária de atendimentos em {ult} (31 dias)"),
    "n_instituicoes": (len(inst[ult]), f"Instituições com dados em {ult}"),
    "n_meses_serie": (len(serie), "Número de meses na série do gráfico"),
    "serie_13m": ([total[m] for m in serie], "Série mensal de 13 meses (lista, para o gráfico)"),
})
json.dump({"rotulos": [rotulo(m) for m in serie], "valores": [total[m] for m in serie]},
          open(__file__.replace("01_totais.py", "serie_13m.json"), "w"), ensure_ascii=False)
