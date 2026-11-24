#!/usr/bin/env python3
"""
verificar.py — "cada número tem a sua consulta".

O revisor chato do caso 3. Lê o relatório (o JSON que vai dar a página) e
confirma que CADA número escrito no texto das secções existe em
saida/relatorio/analise/numeros.json, o ficheiro que os scripts de análise escrevem.
Um número que não saiu de um script é um número inventado, ou copiado à
mão, que é quase o mesmo.

    python3 ferramentas/verificar.py saida/relatorio/relatorio.json

Formato de saida/relatorio/analise/numeros.json (escrito pelos scripts do agente):

    {
      "total_atendimentos_ago_2026": {"valor": 512345, "script": "saida/relatorio/analise/01_totais.py",
                                      "descricao": "Atendimentos em urgência, agosto 2026, todo o país"},
      "pct_verde_azul_ago_2026": {"valor": 41.7, ...}
    }

Ignora anos (1990–2100), números de 1 algarismo e números dentro de datas
(2026-08). Aceita "512 345", "512.345", "41,7 %". Tolerância: arredondamento
à casa decimal escrita.

Sai com código 0 se estiver tudo verificado, 1 se houver números sem origem.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
NUMEROS = RAIZ / "saida" / "relatorio" / "analise" / "numeros.json"
PADRAO = re.compile(r"(?<![\w-])(\d{1,3}(?:[ . ]\d{3})+|\d+)(?:,(\d+))?(?![\w-])")


def numeros_no_texto(texto: str) -> list[tuple[str, float, int]]:
    texto = re.sub(r"\b\d{4}-\d{2}(-\d{2})?\b", " ", texto)          # datas ISO
    texto = re.sub(r"\b\d{1,2}/\d{1,2}(/\d{2,4})?\b", " ", texto)     # datas 12/08
    achados = []
    for m in PADRAO.finditer(texto):
        inteiro = re.sub(r"[ . ]", "", m.group(1))
        dec = m.group(2) or ""
        valor = float(f"{inteiro}.{dec}" if dec else inteiro)
        if not dec and (len(inteiro) == 1 or 1990 <= valor <= 2100):
            continue
        achados.append((m.group(0), valor, len(dec)))
    return achados


def textos(relatorio: dict) -> list[tuple[str, str]]:
    """(onde, texto) de tudo o que é prosa: subtítulo, alertas, texto e listas."""
    out = [("subtitulo", relatorio.get("subtitulo") or "")]
    out += [(f"alertas[{i}]", a.get("texto", "")) for i, a in enumerate(relatorio.get("alertas") or [])]
    for s in relatorio.get("seccoes") or []:
        out.append((s.get("titulo", "?"), s.get("texto") or ""))
        out += [(s.get("titulo", "?"), item) for item in s.get("lista") or []]
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.split("\n\n")[2])
        return 2
    rel = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not NUMEROS.exists():
        print("ERRO: não existe saida/relatorio/analise/numeros.json. Os números do relatório têm de sair de scripts "
              "em saida/relatorio/analise/ que escrevam esse ficheiro.")
        return 1
    conhecidos = json.loads(NUMEROS.read_text(encoding="utf-8"))
    valores = [(k, float(v["valor"])) for k, v in conhecidos.items() if isinstance(v.get("valor"), (int, float))]
    ok, falhas = 0, []
    for onde, t in textos(rel):
        for escrito, valor, casas in numeros_no_texto(t):
            tol = 0.5 * 10 ** -casas + 1e-9
            origem = next((k for k, v in valores if abs(round(v, casas) - valor) <= tol), None)
            if origem:
                ok += 1
            else:
                falhas.append((onde, escrito))
    print(f"Números verificados: {ok}")
    if falhas:
        print(f"SEM ORIGEM ({len(falhas)}). Cada um destes tem de sair de um script em saida/relatorio/analise/ "
              "e estar em numeros.json, ou sair do texto:")
        for onde, escrito in falhas:
            print(f"  - '{escrito}' em «{onde}»")
        return 1
    print("Tudo verificado: cada número do texto tem a sua consulta.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
