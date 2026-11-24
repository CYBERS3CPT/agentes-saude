#!/usr/bin/env python3
"""
dados_sns.py — vai buscar dados abertos ao Portal da Transparência do SNS.

A "mão" do agente analista (caso 3). Não analisa nada: procura, descreve e
descarrega. A análise é o agente que a escreve, em Python, em saida/relatorio/analise/.

    python3 ferramentas/dados_sns.py procurar urgência
    python3 ferramentas/dados_sns.py info atendimentos-em-urgencia-triagem-manchester
    python3 ferramentas/dados_sns.py descarregar atendimentos-em-urgencia-triagem-manchester
    python3 ferramentas/dados_sns.py descarregar atividade-operacional-do-sns-24 --offline

Os CSV ficam em dados/relatorio/<dataset>.csv (separador ';', UTF-8) e cada descarga
escreve dados/relatorio/<dataset>.meta.json com a data do download e a data em que o SNS
atualizou o dataset. Num relatório, a data dos dados é tão importante como os dados.

API: OpenDataSoft Explore v2.1, sem chave. Só biblioteca-padrão do Python.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import pathlib
import sys
import urllib.parse
import urllib.error
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados" / "relatorio"
API = "https://transparencia.sns.gov.pt/api/explore/v2.1/catalog/datasets"
PAGINA = "https://transparencia.sns.gov.pt/explore/dataset/{id}/"


def obter(url: str) -> bytes:
    pedido = urllib.request.Request(url, headers={"User-Agent": "agentes-saude-demo/1.0"})
    with urllib.request.urlopen(pedido, timeout=60) as r:
        return r.read()


def meta(ds: str) -> dict:
    d = json.loads(obter(f"{API}/{urllib.parse.quote(ds)}"))
    m = d.get("metas", {}).get("default", {})
    return {"id": ds, "titulo": m.get("title"), "atualizado_pelo_sns": (m.get("modified") or "")[:10],
            "registos": m.get("records_count"), "url": PAGINA.format(id=ds),
            "campos": [{"nome": f["name"], "tipo": f["type"], "descricao": f.get("label")} for f in d.get("fields", [])]}


def cmd_procurar(termo: str) -> int:
    q = urllib.parse.quote(f'search("{termo}")')
    res = json.loads(obter(f"{API}?where={q}&limit=40"))["results"]
    if not res:
        print(f"Nenhum dataset com '{termo}'.")
        return 0
    for r in res:
        m = r.get("metas", {}).get("default", {})
        print(f"- {r['dataset_id']}  ·  {m.get('title')}  ·  atualizado {(m.get('modified') or '')[:10]}")
    return 0


def cmd_info(ds: str) -> int:
    m = meta(ds)
    print(f"{m['titulo']}\n  id: {m['id']}\n  registos: {m['registos']}\n  atualizado pelo SNS: {m['atualizado_pelo_sns']}\n  {m['url']}\n\nCampos:")
    for c in m["campos"]:
        print(f"  - {c['nome']} ({c['tipo']})" + (f": {c['descricao']}" if c["descricao"] and c["descricao"] != c["nome"] else ""))
    return 0


def resumo_csv(caminho: pathlib.Path) -> None:
    with caminho.open(encoding="utf-8") as f:
        leitor = csv.DictReader(f, delimiter=";")
        linhas = list(leitor)
        campos = leitor.fieldnames or []
    print(f"{caminho.relative_to(RAIZ)}: {len(linhas)} linhas, {len(campos)} colunas")
    print("Colunas: " + ", ".join(campos))
    for c in campos:
        if c in ("tempo", "periodo"):
            vals = sorted(l[c] for l in linhas if l.get(c))
            if vals:
                print(f"Período: {vals[0][:7]} a {vals[-1][:7]}")
    if linhas:
        print("Primeira linha: " + json.dumps(linhas[0], ensure_ascii=False)[:400])


def cmd_descarregar(ds: str, offline: bool) -> int:
    DADOS.mkdir(exist_ok=True)
    csv_p, meta_p = DADOS / f"{ds}.csv", DADOS / f"{ds}.meta.json"
    if offline:
        if not csv_p.exists():
            print(f"ERRO: modo offline e não há {csv_p.relative_to(RAIZ)}.", file=sys.stderr)
            return 2
        m = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
        print(f"Cópia local (descarregada em {m.get('descarregado_em', '?')}; SNS atualizou em {m.get('atualizado_pelo_sns', '?')}).")
        resumo_csv(csv_p)
        return 0
    try:
        m = meta(ds)
        conteudo = obter(f"{API}/{urllib.parse.quote(ds)}/exports/csv?delimiter=%3B")
    except Exception as e:
        if csv_p.exists():
            print(f"AVISO: o portal não respondeu ({e}). Uso a cópia local, que pode estar desatualizada.")
            return cmd_descarregar(ds, offline=True)
        print(f"ERRO: não consegui descarregar '{ds}' ({e}). Não inventes números: diz isto ao utilizador.", file=sys.stderr)
        return 2
    texto = conteudo.decode("utf-8-sig")
    csv_p.write_text(texto, encoding="utf-8")
    m["descarregado_em"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    meta_p.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Descarregado: {m['titulo']} (SNS atualizou em {m['atualizado_pelo_sns']})")
    resumo_csv(csv_p)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Dados abertos do Portal da Transparência do SNS.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("procurar", help="procura datasets por palavra").add_argument("termo")
    sub.add_parser("info", help="descreve um dataset e os seus campos").add_argument("dataset")
    d = sub.add_parser("descarregar", help="descarrega um dataset para dados/<id>.csv")
    d.add_argument("dataset")
    d.add_argument("--offline", action="store_true", help="usar só a cópia local")
    a = ap.parse_args()
    try:
        if a.cmd == "procurar":
            return cmd_procurar(a.termo)
        if a.cmd == "info":
            return cmd_info(a.dataset)
        return cmd_descarregar(a.dataset, a.offline)
    except urllib.error.HTTPError as e:
        print(f"ERRO: o portal respondeu {e.code}. O id do dataset está certo? Usa 'procurar'.", file=sys.stderr)
        return 2
    except urllib.error.URLError as e:
        print(f"ERRO: sem ligação ao portal ({e.reason}). Tenta --offline.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
