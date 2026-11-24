#!/usr/bin/env python3
"""
pontuar.py — faz as contas da avaliação, a partir do que os avaliadores escreveram.

Divisão de trabalho: o modelo LÊ e JULGA (cumpre? não demonstrado? qual é a
frase?). O código CONTA (pesos, fórmulas, arredondamentos). Um modelo de
linguagem a fazer médias ponderadas de cabeça é como um jurista a fazer
contas de dividir num guardanapo: às vezes acerta.

    python3 ferramentas/pontuar.py               # lê saida/comparar/avaliacao-*.json
    python3 ferramentas/pontuar.py --json        # resultado em JSON

Não decide nada. Calcula uma pontuação INDICATIVA para todas as propostas e
lista, para cada uma, os motivos que o júri tem de apreciar (obrigatórios não
cumpridos ou não demonstrados, preço acima do preço base).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ESTADOS = {"cumpre", "nao_cumpre", "nao_demonstrado", "parcial"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Calcula a pontuação indicativa das propostas.")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    crit = json.loads((RAIZ / "dados" / "comparar" / "criterios.json").read_text(encoding="utf-8"))
    ficheiros = sorted((RAIZ / "saida" / "comparar").glob("avaliacao-*.json"))
    if not ficheiros:
        print("ERRO: não há saida/comparar/avaliacao-*.json. Corre primeiro os avaliadores.", file=sys.stderr)
        return 1

    avals, erros = [], []
    for f in ficheiros:
        try:
            av = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            erros.append(f"{f.name}: JSON inválido ({e.msg}, linha {e.lineno})")
            continue
        reqs = av.get("requisitos", {})
        for r in crit["obrigatorios"] + list(crit["valorizados"]):
            if r not in reqs:
                erros.append(f"{f.name}: falta o requisito {r}")
            elif reqs[r].get("estado") not in ESTADOS:
                erros.append(f"{f.name}: {r} tem estado '{reqs[r].get('estado')}' (válidos: {sorted(ESTADOS)})")
            elif r in crit["obrigatorios"] and reqs[r]["estado"] == "parcial":
                erros.append(f"{f.name}: {r} é obrigatório, não pode ser 'parcial'")
        if not isinstance(av.get("preco"), (int, float)):
            erros.append(f"{f.name}: 'preco' tem de ser um número")
        avals.append(av)
    if erros:
        print("ERRO: corrige as avaliações e corre outra vez:", file=sys.stderr)
        for e in erros:
            print(f"  - {e}", file=sys.stderr)
        return 1

    base = crit["preco_base"]
    precos_validos = [av["preco"] for av in avals if av["preco"] <= base]
    mais_baixo = min(precos_validos) if precos_validos else min(av["preco"] for av in avals)

    linhas = []
    for av in avals:
        reqs = av["requisitos"]
        qualidade = 0.0
        for v, pts in crit["valorizados"].items():
            e = reqs[v]["estado"]
            qualidade += pts if e == "cumpre" else pts / 2 if e == "parcial" else 0
        preco = 100 * mais_baixo / av["preco"]
        final = crit["peso_qualidade"] * qualidade + crit["peso_preco"] * preco
        motivos = [f"{r} {reqs[r]['estado'].replace('_', ' ')}" for r in crit["obrigatorios"]
                   if reqs[r]["estado"] != "cumpre"]
        if av["preco"] > base:
            motivos.append(f"preço {av['preco']:,} € acima do preço base {base:,} €".replace(",", " "))
        linhas.append({
            "proposta": av["proposta"], "concorrente": av.get("concorrente", av["proposta"]),
            "preco": av["preco"], "qualidade": round(qualidade, 1), "pontos_preco": round(preco, 1),
            "pontuacao_indicativa": round(final, 1), "obrigatorios_cumpridos": sum(
                reqs[r]["estado"] == "cumpre" for r in crit["obrigatorios"]),
            "motivos_para_o_juri": motivos, "alertas": av.get("alertas", []),
        })
    linhas.sort(key=lambda l: -l["pontuacao_indicativa"])

    resultado = {"preco_base": base, "preco_mais_baixo_usado": mais_baixo, "propostas": linhas,
                 "nota": "Pontuação indicativa, calculada para todas as propostas. Não é uma proposta de "
                         "adjudicação: a exclusão, a ordenação e a adjudicação cabem ao júri."}
    (RAIZ / "saida" / "comparar" / "pontuacao.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    if a.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return 0
    print(f"Preço base: {base} € · preço mais baixo usado na fórmula: {mais_baixo} €\n")
    print(f"{'Proposta':<10}{'Preço':>10}{'Obrig.':>8}{'Qualid.':>9}{'Preço':>8}{'Indicativa':>12}  Motivos para o júri")
    for l in linhas:
        print(f"{l['proposta']:<10}{l['preco']:>10}{l['obrigatorios_cumpridos']:>6}/9{l['qualidade']:>9}"
              f"{l['pontos_preco']:>8}{l['pontuacao_indicativa']:>12}  {'; '.join(l['motivos_para_o_juri']) or '—'}")
        for al in l["alertas"]:
            print(f"{'':>10}⚠️  {al}")
    print("\nGravado em saida/comparar/pontuacao.json. Isto NÃO é uma decisão: é material para o júri.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
