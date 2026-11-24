#!/usr/bin/env python3
"""
mascarar.py — esconde dados pessoais num texto antes de ele sair da caixa.

Um rascunho de resposta, um resumo ou uma página não precisam do número de
utente completo, do NIF ou do telefone de ninguém. Esta ferramenta troca-os
por versões mascaradas, deixando só os últimos dígitos para quem trata do
pedido conseguir confirmar de que caso se trata.

    python3 ferramentas/mascarar.py saida/triagem/respostas/007.md     # mascara o ficheiro no sítio
    python3 ferramentas/mascarar.py --verificar saida/triagem/         # procura fugas, não altera nada
    echo "NUS 287654321" | python3 ferramentas/mascarar.py -    # lê do stdin, escreve no stdout
    python3 ferramentas/mascarar.py --nomes "Maria Gertrudes Pinheiro" ficheiro.md

Nomes de pessoas não se apanham com expressões regulares (a "Rosa" pode ser uma
farmácia). Passa-os com --nomes, separados por vírgulas.

É uma rede de segurança, não um substituto do juízo: o agente não deve
escrever estes dados nas saídas, e esta ferramenta apanha o que escapar.
Só biblioteca-padrão do Python.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

# Nove dígitos, com ou sem espaços de 3 em 3: NUS, NIF e telefones portugueses
# têm todos este formato. Mascaramos tudo, deixando os últimos 4.
NOVE = re.compile(r"(?<![\d\w])(\d{3})[ .]?(\d{2})(\d)[ .]?(\d{3})(?![\d\w])")
EMAIL = re.compile(r"\b([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
DATA_NASC = re.compile(r"(nascid[oa] (?:a|em) )(\d{1,2}/\d{1,2}/\d{4})", re.I)
# Endereços que podem aparecer: o do próprio apoio.
PERMITIDOS = {"suporte@uls-valeficticio.example"}


def mascarar(texto: str, nomes: list[str] | None = None) -> tuple[str, int]:
    n = 0

    def nove(m):
        nonlocal n
        n += 1
        return f"***{m.group(3)}{m.group(4)}"

    def email(m):
        nonlocal n
        if m.group(0).lower() in PERMITIDOS:
            return m.group(0)
        n += 1
        return f"{m.group(1)}***@{m.group(2)}"

    texto = NOVE.sub(nove, texto)
    texto = EMAIL.sub(email, texto)
    texto, k = DATA_NASC.subn(r"\1**/**/****", texto)
    n += k
    for nome in nomes or []:
        nome = nome.strip()
        if not nome:
            continue
        iniciais = ".".join(p[0] for p in nome.split()) + "."
        texto, k = re.subn(re.escape(nome), iniciais, texto, flags=re.I)
        n += k
    return texto, n


def fugas(texto: str) -> list[str]:
    achados = [m.group(0) for m in NOVE.finditer(texto)]
    achados += [m.group(0) for m in EMAIL.finditer(texto) if m.group(0).lower() not in PERMITIDOS]
    return achados


def main() -> int:
    ap = argparse.ArgumentParser(description="Mascara NUS, NIF, telefones, emails e datas de nascimento.")
    ap.add_argument("alvos", nargs="+", help="ficheiros ou pastas; '-' lê do stdin")
    ap.add_argument("--nomes", default="", help="nomes a substituir por iniciais, separados por vírgulas")
    ap.add_argument("--verificar", action="store_true", help="só procura fugas; não altera nada")
    a = ap.parse_args()
    nomes = [x for x in a.nomes.split(",") if x.strip()]

    if a.alvos == ["-"]:
        t, n = mascarar(sys.stdin.read(), nomes)
        sys.stdout.write(t)
        print(f"\n[mascarar] {n} substituições", file=sys.stderr)
        return 0

    ficheiros = []
    for alvo in a.alvos:
        p = pathlib.Path(alvo)
        if p.is_dir():
            ficheiros += sorted(x for x in p.rglob("*") if x.suffix in (".md", ".json", ".html", ".txt"))
        elif p.exists():
            ficheiros.append(p)
        else:
            print(f"ERRO: não encontro {p}", file=sys.stderr)
            return 2

    total = 0
    for f in ficheiros:
        texto = f.read_text(encoding="utf-8")
        if a.verificar:
            achados = fugas(texto)
            for x in achados:
                print(f"FUGA {f}: {x}")
            total += len(achados)
        else:
            novo, n = mascarar(texto, nomes)
            if n:
                f.write_text(novo, encoding="utf-8")
                print(f"{f}: {n} substituições")
            total += n
    if a.verificar:
        print("Sem fugas." if total == 0 else f"{total} possíveis fugas. Corre sem --verificar para mascarar.")
        return 1 if total else 0
    print(f"Total: {total} substituições em {len(ficheiros)} ficheiro(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
