"""05 — Controlo de qualidade: meses-instituição com valor mensal negativo
(o acumulado desceu) e comparação dos totais das duas fontes no último mês e no homólogo."""
from comum import COL_COR, MAN, TIPO, TIPOS, gravar, ler, mensal, ultimo_mes

man = ler(MAN)
mes, _ = mensal(man, list(COL_COR.values()))
ult = ultimo_mes(man)
hom = f"{int(ult[:4]) - 1}{ult[4:]}"
neg = [(t, i, sum(v.values())) for (t, i), v in mes.items() if sum(v.values()) < 0]
print("Negativos (Manchester):", neg)
neg_rel = [x for x in neg if x[0] in (ult, hom, f"{ult[:4]}-07", f"{hom[:4]}-07")]
print("Nos meses usados no relatório:", neg_rel)

tmes, _ = mensal(ler(TIPO), TIPOS)
out = {"n_negativos_periodo": (len(neg_rel), "Meses-instituição com valor mensal negativo nos meses comparados")}
for t, suf in ((ult, "ult"), (hom, "hom")):
    a = sum(sum(v.values()) for (tt, _), v in mes.items() if tt == t)
    b = sum(sum(v.values()) for (tt, _), v in tmes.items() if tt == t)
    print(f"{t}: Manchester {a}  por tipo {b}  diferença {b - a}")
    out[f"tipo_soma_{suf}"] = (b, f"Soma dos quatro tipos de urgência, {t} (dataset por tipo)")
va = sum(sum(v.values()) for (tt, _), v in tmes.items() if tt == ult)
vb = sum(sum(v.values()) for (tt, _), v in tmes.items() if tt == hom)
out["tipo_soma_var"] = (round(100 * (va - vb) / vb, 1), f"Variação % da soma por tipo, {ult} vs {hom}")
out["tipo_soma_queda"] = (abs(out["tipo_soma_var"][0]), "Valor absoluto da variação % da soma por tipo")
out["dif_fontes_hom"] = (out["tipo_soma_hom"][0] - sum(sum(v.values()) for (tt, _), v in mes.items() if tt == hom),
                         f"Diferença entre a soma por tipo e o total de Manchester, {hom}")
print("Variação da soma por tipo:", out["tipo_soma_var"][0], "%")
gravar("05_controlo.py", out)
