#!/usr/bin/env python3
"""
diario.py — o diário de bordo do agente (um *hook*).

Um hook é uma regra automática: o Claude Code corre este script DEPOIS de
cada ferramenta que o agente usa (evento PostToolUse, ver settings.json).
O agente não decide se o corre nem o pode desligar: é o equivalente a
pôr uma câmara de vigilância no escritório do estagiário. Simpática.

Cada linha do diário diz a hora, a ferramenta e o essencial do que foi feito:

    10:02:13  🔧 Bash      python3 ferramentas/tempo.py Lisboa
    10:02:20  🔎 Pesquisa  agenda Lisboa fim de semana 21 22 novembro
    10:02:31  📝 Escreve   saida/plano-lisboa.json

Na palestra, abrir saida/diario.md é a maneira mais limpa de mostrar o ciclo
pensar → agir → observar, sem rolar o terminal para cima feito arqueólogo.

O Claude Code envia ao hook um JSON pelo stdin com, entre outros, os campos
tool_name e tool_input. Um hook que rebenta não deve estragar o trabalho do
agente: por isso, qualquer erro aqui é engolido em silêncio.
"""

import datetime as dt
import json
import os
import pathlib
import re
import sys

ICONES = {
    "Bash": "🔧 Bash    ", "PowerShell": "🔧 Shell   ", "WebSearch": "🔎 Pesquisa",
    "WebFetch": "🌐 Abre    ", "Write": "📝 Escreve ", "Edit": "✏️  Edita   ",
    "Read": "📖 Lê      ", "Agent": "🤖 Subagente", "Task": "🤖 Subagente",
    "Skill": "📋 Receita ", "Glob": "📂 Procura ", "Grep": "📂 Procura ",
}


def resumo(nome: str, entrada: dict, raiz: pathlib.Path) -> str:
    def relativo(caminho: str) -> str:
        try:
            return str(pathlib.Path(caminho).resolve().relative_to(raiz.resolve()))
        except (ValueError, OSError):
            return caminho

    if nome.startswith("mcp__browser__browser_"):
        acao = nome.rsplit("browser_", 1)[1]
        alvo = entrada.get("url") or entrada.get("element") or entrada.get("text") or (
            f"{entrada['time']} s" if "time" in entrada else "")
        texto = f"{acao} {alvo}".strip()
    elif nome in ("Bash", "PowerShell"):
        texto = entrada.get("command", "")
    elif nome == "WebSearch":
        texto = entrada.get("query", "")
    elif nome == "WebFetch":
        texto = entrada.get("url", "")
    elif nome in ("Write", "Edit", "Read"):
        texto = relativo(entrada.get("file_path", ""))
    elif nome in ("Agent", "Task"):
        texto = entrada.get("description") or entrada.get("prompt", "")
    elif nome == "Skill":
        texto = "/" + str(entrada.get("skill", "")) + " " + str(entrada.get("args", "") or "")
    else:
        texto = json.dumps(entrada, ensure_ascii=False)
    texto = " ".join(str(texto).split())  # uma linha só, sem quebras
    # O diário também não pode guardar dados pessoais. Descoberto pelo próprio
    # agente na revisão do dia (/rever-o-dia): a triagem passava nomes de utentes
    # ao mascarar.py com --nomes, e a linha de comando vinha parar aqui.
    texto = re.sub(r"(--nomes)((?:[ =]+(?!--)(?:\"[^\"]*\"|'[^']*'|\S+))+)", r"\1 [omitido]", texto)
    texto = re.sub(r"(?<!\d)\d{9}(?!\d)", "*********", texto)  # NUS, NIF, telefones
    return texto[:110] + ("…" if len(texto) > 110 else "")


def main() -> None:
    try:
        evento = json.load(sys.stdin)
        raiz = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or evento.get("cwd") or ".")
        nome = evento.get("tool_name", "?")
        if nome == "ToolSearch":
            return  # bastidores do Claude Code; não interessam ao público
        quem = "  ↳ " if evento.get("agent_id") else ""  # passo dado por um subagente
        icone = "🌐 Browser " if nome.startswith("mcp__browser__") else ICONES.get(nome, '⚙️  ' + nome[:8].ljust(8))
        linha = f"{dt.datetime.now():%H:%M:%S}  {quem}{icone}  {resumo(nome, evento.get('tool_input') or {}, raiz)}"
        diario = raiz / "saida" / "diario.md"
        diario.parent.mkdir(exist_ok=True)
        novo = not diario.exists()
        with diario.open("a", encoding="utf-8") as f:
            if novo:
                f.write("# Diário de bordo do agente\n\n"
                        "Escrito por um hook depois de cada ferramenta. O agente não escolhe o que aqui fica.\n\n```\n")
            f.write(linha + "\n")
    except Exception:
        pass  # o diário é um extra: nunca pode estragar o plano


if __name__ == "__main__":
    main()
