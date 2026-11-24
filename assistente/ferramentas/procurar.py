#!/usr/bin/env python3
"""
procurar.py — procura passagens nas normas carregadas em dados/norma/.

É a "biblioteca" do agente. O agente não sabe as normas de cor (e ainda bem:
a memória de um modelo tem data de validade e não avisa). Antes de responder,
procura aqui, lê as passagens e cita-as. Se não encontrar, diz que não encontrou.

    python3 ferramentas/procurar.py "vacina gripe profissionais de saúde"
    python3 ferramentas/procurar.py "nirsevimab prematuros" --n 8
    python3 ferramentas/procurar.py --listar          # que normas há, e em que estado

Como funciona (é menos mágico do que parece):
  1. Cada norma está em texto (.txt), com marcas "=== página N ===".
  2. Cada página é partida em trechos de ~10 linhas que se sobrepõem.
  3. Cada trecho recebe uma pontuação BM25: conta quantas palavras da pergunta
     lá aparecem, dando mais peso às palavras raras (gripe aparece em todo o
     lado; "Defesa Nacional" não).
  4. Devolve os melhores trechos com norma, página, estado e o texto literal.

Isto é a versão de bolso de um RAG (retrieval-augmented generation). Os
sistemas a sério usam embeddings; a ideia é a mesma: primeiro procurar,
depois responder com o que se encontrou.

Só biblioteca-padrão do Python.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys
import unicodedata
from collections import Counter

PASTA = pathlib.Path(__file__).resolve().parent.parent / "dados" / "norma"
LINHAS_POR_TRECHO = 10
SOBREPOSICAO = 4
PONTUACAO_FRACA = 6.0   # abaixo disto, os trechos só partilham palavras soltas com a pergunta

PARAGENS = set("""a o as os de da do das dos e é em no na nos nas um uma uns umas para por com sem
que se ao aos à às ou como mais menos sua seu suas seus pela pelo pelas pelos entre sobre até
este esta estes estas esse essa isso isto ser são foi há tem têm qual quais quem onde quando
eu tu ele ela nós vós eles elas me te lhe nos vos lhes meu minha teu tua já não sim muito
pode podem deve devem dgs norma normas""".split())


def sem_acentos(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def palavras(t: str) -> list[str]:
    """Minúsculas, sem acentos, sem palavras vazias, com um 'stemming' de
    pobre: tira o plural (profissionais → profissional, vacinas → vacina)."""
    out = []
    for p in re.findall(r"[a-z0-9]+", sem_acentos(t.lower())):
        if p in {sem_acentos(x) for x in PARAGENS} or len(p) < 2:
            continue
        if p.endswith("ais") and len(p) > 5:
            p = p[:-3] + "al"
        elif p.endswith("oes") and len(p) > 5:
            p = p[:-3] + "ao"
        elif p.endswith("s") and len(p) > 4:
            p = p[:-1]
        out.append(p)
    return out


def carregar_metadados() -> dict[str, dict]:
    f = PASTA / "normas.json"
    if not f.exists():
        return {}
    return {n["id"]: n for n in json.loads(f.read_text(encoding="utf-8"))}


def trechos() -> list[dict]:
    """Parte cada .txt em trechos sobrepostos, guardando norma e página."""
    out = []
    for txt in sorted(PASTA.glob("*.txt")):
        pagina, linhas = 0, []

        def fechar():
            limpas = [l.rstrip() for l in linhas if l.strip()]
            for i in range(0, max(1, len(limpas)), LINHAS_POR_TRECHO - SOBREPOSICAO):
                bloco = limpas[i:i + LINHAS_POR_TRECHO]
                if bloco:
                    out.append({"id": txt.stem, "pagina": pagina, "texto": "\n".join(bloco)})
                if i + LINHAS_POR_TRECHO >= len(limpas):
                    break

        for linha in txt.read_text(encoding="utf-8").splitlines():
            m = re.match(r"=== página (\d+) ===", linha)
            if m:
                fechar()
                pagina, linhas = int(m.group(1)), []
            else:
                linhas.append(linha)
        fechar()
    return out


def bm25(consulta: list[str], docs: list[list[str]], k1: float = 1.4, b: float = 0.75) -> list[float]:
    n = len(docs)
    media = sum(len(d) for d in docs) / max(1, n)
    df = Counter(t for d in docs for t in set(d))
    pont = []
    for d in docs:
        tf = Counter(d)
        s = 0.0
        for t in set(consulta):
            if t not in tf:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(d) / media))
        pont.append(s)
    return pont


def compactar(texto: str) -> str:
    """O texto vem de um PDF com colunas: junta os espaços, mantém as palavras."""
    return re.sub(r"[ \t]{2,}", "  ", texto).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Procura passagens nas normas carregadas.")
    ap.add_argument("consulta", nargs="?", help="palavras a procurar")
    ap.add_argument("--n", type=int, default=5, help="quantos trechos devolver (máx. 15)")
    ap.add_argument("--listar", action="store_true", help="lista as normas carregadas")
    ap.add_argument("--json", action="store_true", help="saída em JSON")
    a = ap.parse_args()

    meta = carregar_metadados()
    if a.listar:
        for i, m in meta.items():
            versao = f"atualizada a {m['atualizada']}" if m.get("atualizada") else "versão original"
            aviso = f"  ⚠️ REVOGADA (substituída por {m['substituida_por']})" if m["estado"] == "revogada" else ""
            print(f"{i}: {m['numero']} de {m['data']}, {versao} — {m['titulo']} [{m['estado']}]{aviso}")
        return 0
    if not a.consulta:
        ap.error("diz o que procurar (ou --listar)")

    q = palavras(a.consulta)
    if not q:
        print("ERRO: a consulta só tem palavras vazias. Usa termos concretos.", file=sys.stderr)
        return 1
    ts = trechos()
    pont = bm25(q, [palavras(t["texto"]) for t in ts])
    ordem = sorted(range(len(ts)), key=lambda i: -pont[i])
    resultados, vistos = [], set()
    for i in ordem:
        if pont[i] <= 0 or len(resultados) >= min(15, a.n):
            break
        t = ts[i]
        chave = (t["id"], t["pagina"], t["texto"][:60])
        if chave in vistos:
            continue
        vistos.add(chave)
        m = meta.get(t["id"], {})
        resultados.append({
            "norma": m.get("numero", t["id"]), "id": t["id"], "pagina": t["pagina"],
            "data": m.get("data"), "atualizada": m.get("atualizada"), "estado": m.get("estado", "desconhecido"),
            "substituida_por": m.get("substituida_por"), "url": m.get("url"),
            "pontuacao": round(pont[i], 2), "texto": compactar(t["texto"]),
        })

    if a.json:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
        return 0
    if not resultados:
        print(f"Nada encontrado para: {a.consulta}")
        print("Nenhuma norma carregada fala disto. Não inventes: diz que não encontraste.")
        return 0
    if resultados[0]["pontuacao"] < PONTUACAO_FRACA:
        print(f"⚠️ Pontuações baixas (melhor: {resultados[0]['pontuacao']}): os trechos só partilham palavras soltas "
              "com a pergunta. É provável que nenhuma norma carregada responda a isto.\n")
    for r in resultados:
        versao = f"atualizada a {r['atualizada']}" if r["atualizada"] else "versão original"
        estado = (f"⚠️ REVOGADA — substituída por {r['substituida_por']}" if r["estado"] == "revogada"
                  else r["estado"])
        print(f"── {r['norma']} ({r['id']}), de {r['data']}, {versao} · página {r['pagina']} · {estado} · pontuação {r['pontuacao']}")
        print(r["texto"])
        print()
    print("Lembra-te: cita norma + página + uma frase literal. Se nenhum trecho responde à pergunta, diz que não encontraste.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
