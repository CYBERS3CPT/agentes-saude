#!/usr/bin/env python3
"""
notificar.py — "envia" a notificação de adjudicação a um concorrente.

É de mentira: não envia nada. Escreve a mensagem no ecrã e em
saida/comparar/notificacoes.log. Existe para a demonstração ter um botão perigoso.

Num agente a sério, esta ferramenta mandaria um email com efeitos jurídicos.
Por isso, em .claude/settings.json, está na lista "ask": o agente não a pode
usar sem que uma pessoa diga que sim. E o CLAUDE.md diz que só o júri decide.

    python3 ferramentas/notificar.py --para gama --assunto "Adjudicação" --texto "..."
"""

import argparse
import datetime as dt
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent

ap = argparse.ArgumentParser(description="Notificação (simulada) a um concorrente.")
ap.add_argument("--para", required=True)
ap.add_argument("--assunto", required=True)
ap.add_argument("--texto", required=True)
a = ap.parse_args()

registo = (f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] SIMULAÇÃO — nada foi enviado\n"
           f"Para: {a.para}\nAssunto: {a.assunto}\n\n{a.texto}\n{'-' * 60}\n")
(RAIZ / "saida" / "comparar").mkdir(parents=True, exist_ok=True)
with (RAIZ / "saida" / "comparar" / "notificacoes.log").open("a", encoding="utf-8") as f:
    f.write(registo)
print(registo)
print("(Simulação. Num sistema real, este email teria acabado de sair, com efeitos jurídicos.)")
