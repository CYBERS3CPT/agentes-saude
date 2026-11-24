"""Funções comuns aos scripts de análise.

Os datasets do Portal da Transparência usados aqui são ACUMULADOS desde janeiro
(confirmado em 00_explorar.py). O valor de um mês = acumulado do mês − acumulado
do mês anterior, por instituição, dentro do mesmo ano; janeiro fica como está.
"""
import csv
import json
import pathlib
from collections import defaultdict

RAIZ = pathlib.Path(__file__).resolve().parents[2].parent
DADOS = RAIZ / "dados" / "relatorio"
NUMEROS = RAIZ / "saida" / "relatorio" / "analise" / "numeros.json"
MAN = DADOS / "atendimentos-em-urgencia-triagem-manchester.csv"
TIPO = DADOS / "atendimentos-por-tipo-de-urgencia-hospitalar-link.csv"

CORES = ["vermelha", "laranja", "amarela", "verde", "azul", "branca"]
COL_COR = {c: f"no_de_atendimentos_em_urgencia_su_triagem_manchester_{c}" for c in CORES}
COL_COR["sem_triagem"] = "no_de_atendimentos_em_sem_triagem_manchester"
TIPOS = ["urgencias_geral", "urgencias_pediatricas", "urgencia_obstetricia", "urgencia_psiquiatrica"]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def num(x):
    return int(float(x)) if x and x.strip() else 0


def ler(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def mes_anterior(m):
    a, mm = int(m[:4]), int(m[5:])
    return f"{a - 1}-12" if mm == 1 else f"{a}-{mm - 1:02d}"


def mensal(linhas, colunas):
    """{(tempo, instituicao): {coluna: valor_mensal}, ...} + {(tempo, inst): regiao}."""
    acum = {}
    regiao = {}
    for r in linhas:
        k = (r["tempo"], r["instituicao"])
        acum[k] = {c: num(r[c]) for c in colunas}
        regiao[k] = r["regiao"]
    out = {}
    for (t, inst), v in acum.items():
        if t.endswith("-01"):
            out[(t, inst)] = dict(v)
            continue
        ant = acum.get((mes_anterior(t), inst))
        if ant is None:
            continue  # sem mês anterior não se consegue isolar o mês
        out[(t, inst)] = {c: v[c] - ant[c] for c in colunas}
    return out, regiao


def ultimo_mes(linhas):
    return max(r["tempo"] for r in linhas)


def rotulo(m):
    return f"{MESES[int(m[5:]) - 1]} {m[2:4]}"


def gravar(script, numeros):
    """Acrescenta (substituindo as chaves do próprio script) a numeros.json."""
    atual = json.loads(NUMEROS.read_text(encoding="utf-8")) if NUMEROS.exists() else {}
    for chave, (valor, descricao) in numeros.items():
        atual[chave] = {"valor": valor, "script": f"saida/relatorio/analise/{script}", "descricao": descricao}
    NUMEROS.write_text(json.dumps(atual, ensure_ascii=False, indent=2), encoding="utf-8")
