"""00 — Exploração: valores mensais ou acumulados? Quantas instituições por mês?
Não escreve números para o relatório; serve para decidir como ler os dados."""
import csv
import pathlib
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parents[3]
MAN = RAIZ / "dados/relatorio/atendimentos-em-urgencia-triagem-manchester.csv"
TIPO = RAIZ / "dados/relatorio/atendimentos-por-tipo-de-urgencia-hospitalar-link.csv"
CORES = ["vermelha", "laranja", "amarela", "verde", "azul", "branca"]


def n(x):
    return int(float(x)) if x and x.strip() else 0


def ler(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


man = ler(MAN)
por_mes = defaultdict(lambda: [0, set()])
for r in man:
    tot = sum(n(r[f"no_de_atendimentos_em_urgencia_su_triagem_manchester_{c}"]) for c in CORES)
    tot += n(r["no_de_atendimentos_em_sem_triagem_manchester"])
    por_mes[r["tempo"]][0] += tot
    por_mes[r["tempo"]][1].add(r["instituicao"])
print("MANCHESTER — mês, total (cores + sem triagem), nº instituições")
for m in sorted(por_mes)[-26:]:
    print(m, por_mes[m][0], len(por_mes[m][1]))

# Uma instituição ao longo de 2025-2026, para ver se cresce mês a mês (acumulado)
inst = "Unidade Local de Saúde Castelo Branco, EPE"
print("\nCastelo Branco (amarela) por mês:")
for r in sorted((r for r in man if r["instituicao"] == inst), key=lambda r: r["tempo"])[-20:]:
    print(r["tempo"], r["no_de_atendimentos_em_urgencia_su_triagem_manchester_amarela"])

tipo = ler(TIPO)
pm = defaultdict(lambda: [0, set()])
for r in tipo:
    pm[r["tempo"]][0] += n(r["total_urgencias"])
    pm[r["tempo"]][1].add(r["instituicao"])
print("\nTIPO — mês, total_urgencias, nº instituições")
for m in sorted(pm)[-20:]:
    print(m, pm[m][0], len(pm[m][1]))

print("\nRegiões (Manchester, 2026-08 e 2025-08):")
for m in ("2025-08", "2026-08"):
    print(m, sorted({r["regiao"] for r in man if r["tempo"] == m}))
