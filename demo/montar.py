#!/usr/bin/env python3
"""
montar.py — monta o assistente da ULS de Vale Fictício num momento do dia.

Há um só agente (assistente/), que ganha uma competência de cada vez. Este
script copia para uma pasta de demonstração só o que pertence às competências
1..N: receitas, ferramentas, dados, subagentes, as linhas do manual marcadas
com <!-- competencia:N --> e as regras de permissão de demo/competencias.json.

    python3 demo/montar.py                  # ~/saude-ao-vivo/assistente, dia completo (5 + revisão)
    python3 demo/montar.py --ate 0          # chega sem competências (só o manual base)
    python3 demo/montar.py --etapa 1        # 08:00, construção ao vivo: sem manual nem receita
    python3 demo/montar.py --etapa 3        # plano B: fim da etapa 3 da construção ao vivo
    python3 demo/montar.py --proxima        # instala a competência seguinte e mostra as permissões novas
    python3 demo/montar.py --injecao        # 09:30: junta à caixa o pedido 021 (com a injeção)
    python3 demo/montar.py --sem-regra      # tira do manual a regra contra injeções
    python3 demo/montar.py --com-regra      # volta a pô-la
    python3 demo/montar.py --settings       # só regenera assistente/.claude/settings.json

Opção comum: --destino PASTA (por omissão ~/saude-ao-vivo/assistente; evita /tmp).
Só apaga pastas criadas por este script (marca .saude-ao-vivo).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "assistente"
MANIFESTO = json.loads((RAIZ / "demo" / "competencias.json").read_text(encoding="utf-8"))
ETAPAS = RAIZ / "demo" / "01" / "etapas"
REGRA = RAIZ / "demo" / "02" / "regra-injecao.md"
MARCA = ".saude-ao-vivo"
ESTADO = ".competencias"
HOOKS = {"PostToolUse": [{"matcher": "*", "hooks": [{"type": "command",
         "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/diario.py\"", "timeout": 10}]}]}


def comps(n: int) -> list[dict]:
    return [c for c in MANIFESTO["competencias"] if c["n"] <= n]


def settings(n: int) -> dict:
    b = MANIFESTO["base"]
    allow, ask, deny = list(b["allow"]), list(b["ask"]), list(b["deny"])
    mcp = []
    for c in comps(n):
        allow += c["allow"]
        ask += c["ask"]
        deny += c.get("deny", [])
        if c.get("mcp"):
            mcp.append(c["mcp"])
    s = {"$schema": "https://json.schemastore.org/claude-code-settings.json",
         "permissions": {"allow": allow, "ask": ask, "deny": deny}}
    if mcp:
        s["enabledMcpjsonServers"] = mcp
    s["hooks"] = HOOKS
    return s


def manual(n: int) -> str:
    """O CLAUDE.md só com as linhas das competências 1..n (e sem as marcas)."""
    texto = (ORIGEM / "CLAUDE.md").read_text(encoding="utf-8")
    def bloco(m):
        return m.group(2) if int(m.group(1)) <= n else ""
    texto = re.sub(r"<!-- competencia:(\d+) -->\n(.*?)<!-- /competencia -->\n", bloco, texto, flags=re.S)
    texto = re.sub(r">\n> \(Nota para quem mantém o agente:[^\n]*\n", "", texto)  # nota interna sobre as marcas
    if n == 0:
        texto = texto.replace("## O que já sabes fazer\n\n", "## O que já sabes fazer\n\nAinda nada. As competências chegam ao longo do dia.\n\n")
    return texto


def escrever_json(p: pathlib.Path, dados: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def preparar_destino(destino: pathlib.Path, manter_saida: bool) -> None:
    if destino.exists():
        if not (destino / MARCA).exists():
            sys.exit(f"'{destino}' já existe e não foi criada por este script. Não lhe toco.")
        for f in destino.iterdir():
            if f.name == MARCA or (manter_saida and f.name == "saida"):
                continue
            shutil.rmtree(f) if f.is_dir() else f.unlink()
    destino.mkdir(parents=True, exist_ok=True)
    (destino / MARCA).touch()


def montar(destino: pathlib.Path, n: int, com_manual: bool = True, com_skills: bool = True,
           manter_saida: bool = False) -> None:
    preparar_destino(destino, manter_saida)
    (destino / "ferramentas").mkdir()
    for f in MANIFESTO["base"]["ferramentas"]:
        shutil.copy(ORIGEM / "ferramentas" / f, destino / "ferramentas" / f)
    shutil.copytree(ORIGEM / ".claude" / "hooks", destino / ".claude" / "hooks")
    escrever_json(destino / ".claude" / "settings.json", settings(n))
    if com_manual:
        (destino / "CLAUDE.md").write_text(manual(n), encoding="utf-8")
    if any(c.get("mcp") for c in comps(n)):
        shutil.copy(ORIGEM / ".mcp.json", destino / ".mcp.json")
    for c in comps(n):
        for f in c["ferramentas"]:
            shutil.copy(ORIGEM / "ferramentas" / f, destino / "ferramentas" / f)
        if (ORIGEM / "dados" / c["nome"]).exists():
            shutil.copytree(ORIGEM / "dados" / c["nome"], destino / "dados" / c["nome"])
        if com_skills:
            for sk in [c["nome"]] + c.get("skills_extra", []):
                shutil.copytree(ORIGEM / ".claude" / "skills" / sk, destino / ".claude" / "skills" / sk)
        for a in c["agentes"]:
            (destino / ".claude" / "agents").mkdir(parents=True, exist_ok=True)
            shutil.copy(ORIGEM / ".claude" / "agents" / a, destino / ".claude" / "agents" / a)
        s = destino / "saida" / c.get("saida", c["nome"])
        s.mkdir(parents=True, exist_ok=True)
        if c["nome"] == "triagem":
            (s / "respostas").mkdir(exist_ok=True)
    (destino / ESTADO).write_text(str(n), encoding="utf-8")


def estado(destino: pathlib.Path) -> int:
    if not (destino / MARCA).exists():
        sys.exit("Primeiro monta a pasta: ./demo/preparar.sh")
    return int((destino / ESTADO).read_text().strip() or 0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--destino", default=str(pathlib.Path.home() / "saude-ao-vivo" / "assistente"))
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--ate", type=int, choices=range(0, 7), help="competências instaladas (0–6; a 6 é a revisão das 18:00)")
    g.add_argument("--etapa", type=int, choices=range(1, 6), help="construção ao vivo da 1.ª competência")
    g.add_argument("--proxima", action="store_true")
    g.add_argument("--injecao", action="store_true")
    g.add_argument("--ataque", action="store_true", help="junta à caixa o último ataque do red team (/atacar)")
    g.add_argument("--sem-regra", action="store_true")
    g.add_argument("--com-regra", action="store_true")
    g.add_argument("--settings", action="store_true")
    a = ap.parse_args()
    destino = pathlib.Path(a.destino).expanduser()

    if a.settings:
        escrever_json(ORIGEM / ".claude" / "settings.json", settings(6))
        print("assistente/.claude/settings.json regenerado (dia completo).")
        return 0

    if a.injecao:
        if estado(destino) < 2:
            sys.exit("A caixa de suporte chega com a competência 2: ./demo/preparar.sh --proxima")
        shutil.copy(RAIZ / "demo" / "02" / "injecao" / "021.eml", destino / "dados" / "triagem" / "caixa" / "021.eml")
        print(f"Pedido 021 em {destino}/dados/triagem/caixa/021.eml. Abre-o num editor antes de /triagem 021.")
        return 0

    if a.ataque:
        if estado(destino) < 2:
            sys.exit("A caixa de suporte chega com a competência 2: ./demo/preparar.sh --proxima")
        ataques = sorted((destino / "saida" / "triagem" / "ataques").glob("ataque-*.eml"))
        if not ataques:
            sys.exit("Ainda não há ataques: corre /atacar no Claude Code primeiro.")
        caixa = destino / "dados" / "triagem" / "caixa"
        n = 901
        while (caixa / f"{n}.eml").exists():
            n += 1
        shutil.copy(ataques[-1], caixa / f"{n}.eml")
        print(f"{ataques[-1].name} está agora na caixa como pedido {n}. No Claude Code: /triagem {n}")
        return 0

    if a.sem_regra or a.com_regra:
        n = estado(destino)
        regra = "\n".join(l for l in REGRA.read_text(encoding="utf-8").splitlines() if not l.startswith("<!--")).strip("\n") + "\n"
        alvo = destino / "CLAUDE.md"
        if a.sem_regra:
            t = alvo.read_text(encoding="utf-8")
            if regra not in t:
                sys.exit("A regra já não está no CLAUDE.md (ou foi editada à mão).")
            alvo.write_text(t.replace(regra, ""), encoding="utf-8")
            print("Regra retirada. /exit e volta a entrar para ele reler o manual.")
        else:
            alvo.write_text(manual(n), encoding="utf-8")
            print("Manual reposto (com a regra). /exit e volta a entrar.")
        return 0

    if a.proxima:
        n = estado(destino)
        if n >= 6:
            sys.exit("O dia já acabou: as cinco competências e a revisão das 18:00 estão instaladas.")
        antes = json.loads((destino / ".claude" / "settings.json").read_text(encoding="utf-8"))["permissions"]
        ao_vivo = (destino / ".etapa").exists()
        montar(destino, n + 1, manter_saida=True)
        depois = settings(n + 1)["permissions"]
        c = MANIFESTO["competencias"][n]
        print(f"\n{c['hora']} — {c['momento']}: nova competência /{c['nome']}\n")
        if ao_vivo:
            print("  (o manual escrito ao vivo às 8h foi substituído pelo manual oficial da equipa)\n")
        for chave, rotulo in (("allow", "pode sozinho"), ("ask", "tem de perguntar"), ("deny", "nunca")):
            novas = [r for r in depois[chave] if r not in antes.get(chave, [])]
            for r in novas:
                print(f"  + {rotulo:16} {r}")
        print(f"\n  Porquê: {c['porque']}.")
        print("\n  /exit e volta a entrar (claude) para ele ler a nova receita e as permissões.")
        return 0

    if a.etapa:
        montar(destino, 1, com_manual=False, com_skills=False)
        (destino / ".etapa").write_text(str(a.etapa), encoding="utf-8")
        if a.etapa >= 2:
            shutil.copy(ETAPAS / "etapa-2-CLAUDE.md", destino / "CLAUDE.md")
        if a.etapa >= 3:
            d = destino / ".claude" / "skills" / "onde-ir"
            d.mkdir(parents=True, exist_ok=True)
            shutil.copy(ETAPAS / "etapa-3-SKILL.md", d / "SKILL.md")
        if a.etapa >= 5:
            with (destino / "CLAUDE.md").open("a", encoding="utf-8") as f:
                f.write((ETAPAS / "etapa-5-melhorias.md").read_text(encoding="utf-8"))
        print(f"08:00 — construção ao vivo, etapa {a.etapa}: {destino}")
    else:
        n = 6 if a.ate is None else a.ate
        montar(destino, n)
        print(f"Assistente com {n} competência(s): {destino}")

    print(f"""
  cd {destino} && claude

Na primeira vez, aceita a pergunta de confiança. É sempre a mesma pasta, por
isso basta uma vez: --proxima, --etapa e --sem-regra não mudam o caminho.""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
