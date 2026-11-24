"""04 — Repartição por tipo de urgência (geral, pediátrica, obstétrica, psiquiátrica).
Fonte: atendimentos-por-tipo-de-urgencia-hospitalar-link. Serve SÓ para a repartição por tipo:
o total deste dataset não é igual ao da Triagem de Manchester e não é usado como total."""
from collections import defaultdict

from comum import TIPO, TIPOS, gravar, ler, mensal, ultimo_mes

linhas = ler(TIPO)
mes, _ = mensal(linhas, TIPOS)
ult = ultimo_mes(linhas)
hom = f"{int(ult[:4]) - 1}{ult[4:]}"
soma = {ult: defaultdict(int), hom: defaultdict(int)}
for (t, _i), v in mes.items():
    if t in soma:
        for c in TIPOS:
            soma[t][c] += v[c]

NOMES = {"urgencias_geral": "geral", "urgencias_pediatricas": "pediatrica",
         "urgencia_obstetricia": "obstetrica", "urgencia_psiquiatrica": "psiquiatrica"}
out = {}
for t, suf in ((ult, "ult"), (hom, "hom")):
    tot = sum(soma[t].values())
    print(f"\n{t} (soma dos tipos {tot})")
    for c in TIPOS:
        pct = round(100 * soma[t][c] / tot, 1)
        print(f"  {NOMES[c]:13s} {soma[t][c]:>8d} {pct:5.1f} %")
        out[f"tipo_{NOMES[c]}_{suf}"] = (soma[t][c], f"Atendimentos urgência {NOMES[c]}, {t} (dataset por tipo)")
        out[f"tipo_{NOMES[c]}_pct_{suf}"] = (pct, f"% urgência {NOMES[c]} na soma dos tipos, {t}")
for c in TIPOS:
    v = round(100 * (soma[ult][c] - soma[hom][c]) / soma[hom][c], 1)
    out[f"tipo_{NOMES[c]}_var"] = (v, f"Variação % urgência {NOMES[c]}, {ult} vs {hom}")
    print(f"  var {NOMES[c]}: {v} %")
gravar("04_tipos.py", out)
