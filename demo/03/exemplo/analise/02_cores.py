"""02 — Que parte foram pulseiras verdes, azuis ou brancas (não urgentes)? Mudou face ao ano anterior?
Fonte: atendimentos-em-urgencia-triagem-manchester. Percentagens sobre o total (cores + sem triagem)."""
from collections import defaultdict

from comum import COL_COR, MAN, gravar, ler, mensal, ultimo_mes

linhas = ler(MAN)
mes, _ = mensal(linhas, list(COL_COR.values()))
ult = ultimo_mes(linhas)
hom = f"{int(ult[:4]) - 1}{ult[4:]}"

soma = {ult: defaultdict(int), hom: defaultdict(int)}
for (t, _i), v in mes.items():
    if t in soma:
        for cor, col in COL_COR.items():
            soma[t][cor] += v[col]

out = {}
for t, sufixo in ((ult, "ult"), (hom, "hom")):
    tot = sum(soma[t].values())
    print(f"\n{t} (total {tot})")
    for cor in COL_COR:
        pct = round(100 * soma[t][cor] / tot, 1)
        print(f"  {cor:12s} {soma[t][cor]:>8d}  {pct:5.1f} %")
        out[f"n_{cor}_{sufixo}"] = (soma[t][cor], f"Atendimentos pulseira {cor}, {t}")
        out[f"pct_{cor}_{sufixo}"] = (pct, f"% pulseira {cor} no total, {t}")
    nao_urg = soma[t]["verde"] + soma[t]["azul"] + soma[t]["branca"]
    urg = soma[t]["vermelha"] + soma[t]["laranja"]
    out[f"n_nao_urgentes_{sufixo}"] = (nao_urg, f"Verdes+azuis+brancas, {t}")
    out[f"pct_nao_urgentes_{sufixo}"] = (round(100 * nao_urg / tot, 1), f"% verdes+azuis+brancas, {t}")
    out[f"pct_vermelha_laranja_{sufixo}"] = (round(100 * urg / tot, 1), f"% vermelhas+laranjas, {t}")
    print(f"  não urgentes (verde+azul+branca): {nao_urg} = {out[f'pct_nao_urgentes_{sufixo}'][0]} %")
    print(f"  vermelha+laranja: {out[f'pct_vermelha_laranja_{sufixo}'][0]} %")

dpp = round(out["pct_nao_urgentes_ult"][0] - out["pct_nao_urgentes_hom"][0], 1)
out["pp_nao_urgentes"] = (dpp, f"Diferença em pontos percentuais da % não urgente, {ult} vs {hom}")
print(f"\nVariação da % não urgente: {dpp} p.p.")
for cor in COL_COR:
    v = round(100 * (soma[ult][cor] - soma[hom][cor]) / soma[hom][cor], 1) if soma[hom][cor] else None
    if v is not None:
        out[f"var_{cor}_pct"] = (v, f"Variação % pulseira {cor}, {ult} vs {hom}")
        print(f"  var {cor}: {v} %")
gravar("02_cores.py", out)
