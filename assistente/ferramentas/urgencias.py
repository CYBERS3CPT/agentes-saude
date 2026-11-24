#!/usr/bin/env python3
"""
urgencias.py — as urgências do SNS mais próximas de um concelho.

A "mão" do agente do caso 1. Usa DADOS ABERTOS do Portal da Transparência
do SNS (dataset "Caracterização das valências de urgência"): que serviços
de urgência existem, de que tipo, que valências têm, para que idades, como
se lá chega, morada e telefone.

    python3 ferramentas/urgencias.py Odivelas
    python3 ferramentas/urgencias.py Odivelas --tipo criancas
    python3 ferramentas/urgencias.py "Vila Real" --tipo obstetricia --n 3
    python3 ferramentas/urgencias.py Beja --json        # para o agente ler
    python3 ferramentas/urgencias.py Beja --offline     # só a cópia local

O que esta ferramenta NÃO sabe, e diz sempre no fim:
  - tempos de espera em tempo real (o SNS publica-os em tempos.min-saude.pt,
    mas não como dados abertos);
  - se uma urgência está aberta HOJE (encerramentos temporários, escalas);
  - nada sobre o doente. Não lhe deem dados de doentes.

Um agente só sabe o que as ferramentas lhe dão. Se o agente disser um tempo
de espera, inventou-o.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import pathlib
import sys
import unicodedata
from collections import Counter
import urllib.parse
import urllib.request

PASTA = pathlib.Path(__file__).resolve().parent.parent / "dados" / "onde-ir" / "cache"
DATASET = "caracterizacao-das-valencias-de-urgencia"
BASE = "https://transparencia.sns.gov.pt/api/explore/v2.1/catalog/datasets/" + DATASET
URL_DADOS = BASE + "/exports/json"
URL_PAGINA = "https://transparencia.sns.gov.pt/explore/dataset/" + DATASET + "/"
URL_TEMPOS = "https://tempos.min-saude.pt"
URL_INSTITUICOES = URL_TEMPOS + "/institutions.json"
URL_GEO = "https://geocoding-api.open-meteo.com/v1/search?name={nome}&count=5&language=pt&countryCode=PT"
VALIDADE_DIAS = 7

TIPOS = {
    "adultos": "Urgência Adultos",
    "criancas": "Urgência Crianças e Adolescentes",
    "obstetricia": "Obstetrícia",
}
# Nomes do dia a dia que o geocodificador percebe mal ("Gaia" dá uma aldeia
# em Castelo Branco). Um agente herda os defeitos das ferramentas.
ALCUNHAS = {"gaia": "Vila Nova de Gaia", "famalicao": "Vila Nova de Famalicao",
            "feira": "Santa Maria da Feira", "vfx": "Vila Franca de Xira", "caldas": "Caldas da Rainha"}

NAO_SEI = [
    "Tempos de espera e se a urgência está aberta agora: não estão nestes dados abertos. Estão em tempos.min-saude.pt "
    "(página de cada hospital, em 'tempos_url'), num relatório que só se lê com um browser.",
    "Distâncias em linha reta, não por estrada.",
]


def sem_acentos(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").lower().strip()


def obter(url: str) -> bytes:
    pedido = urllib.request.Request(url, headers={"User-Agent": "agentes-saude-demo/1.0"})
    with urllib.request.urlopen(pedido, timeout=30) as r:
        return r.read()


def carregar_dados(offline: bool) -> tuple[list[dict], str]:
    """Devolve (registos, de onde vieram). Cache local de 7 dias; se a
    internet falhar, usa a cópia que houver e diz que é antiga."""
    PASTA.mkdir(parents=True, exist_ok=True)
    cache = PASTA / "valencias.json"
    if cache.exists():
        idade = dt.datetime.now() - dt.datetime.fromtimestamp(cache.stat().st_mtime)
        if offline or idade.days < VALIDADE_DIAS:
            return json.loads(cache.read_text(encoding="utf-8")), f"cópia local de {dt.datetime.fromtimestamp(cache.stat().st_mtime):%d/%m/%Y}"
    if offline:
        raise SystemExit("ERRO: modo offline e não há cópia local em dados/onde-ir/cache/valencias.json")
    try:
        dados = json.loads(obter(URL_DADOS))
    except Exception as e:  # rede em baixo: a cópia antiga é melhor do que nada, desde que se diga
        if cache.exists():
            return json.loads(cache.read_text(encoding="utf-8")), f"cópia local ANTIGA (o portal não respondeu: {e})"
        raise SystemExit(f"ERRO: não consegui obter os dados do Portal da Transparência ({e}). Não inventes: diz isto ao utilizador.")
    cache.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return dados, "Portal da Transparência do SNS (descarregado agora)"


def data_do_dataset() -> str | None:
    """A data em que o SNS atualizou o dataset. Pode ser de há meses, e isso importa."""
    cache = PASTA / "dataset-meta.json"
    try:
        meta = json.loads(obter(BASE))
        cache.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    except Exception:
        if not cache.exists():
            return None
        meta = json.loads(cache.read_text(encoding="utf-8"))
    m = (meta.get("metas") or {}).get("default", {}).get("modified") or ""
    return m[:10] or None


def geocodificar(nome: str, offline: bool) -> tuple[float, float, str]:
    PASTA.mkdir(parents=True, exist_ok=True)
    cache = PASTA / "geo.json"
    geo = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    nome = ALCUNHAS.get(sem_acentos(nome), nome)
    chave = sem_acentos(nome)
    if chave in geo:
        g = geo[chave]
        return g["lat"], g["lon"], g["nome"]
    if offline:
        raise SystemExit(f"ERRO: modo offline e não sei onde fica '{nome}'. Concelhos em cache: {', '.join(sorted(geo)) or 'nenhum'}")
    try:
        res = json.loads(obter(URL_GEO.format(nome=urllib.parse.quote(nome)))).get("results") or []
    except Exception as e:
        raise SystemExit(f"ERRO: não consegui localizar '{nome}' ({e}).")
    if not res:
        raise SystemExit(f"ERRO: não encontrei '{nome}' em Portugal. Confirma o nome do concelho com o utilizador.")
    r = max(res, key=lambda x: x.get("population") or 0)  # a sede de concelho ganha à aldeia homónima
    rotulo = r["name"] + (f" ({r['admin1'].replace('Distrito de ', '')})" if r.get("admin1") else "")
    geo[chave] = {"lat": r["latitude"], "lon": r["longitude"], "nome": rotulo}
    cache.write_text(json.dumps(geo, ensure_ascii=False, indent=1), encoding="utf-8")
    return r["latitude"], r["longitude"], rotulo


def km(lat1, lon1, lat2, lon2) -> float:
    """Distância em linha reta (fórmula de haversine). A estrada é sempre mais longa."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def _tokens(nome: str) -> set[str]:
    s = sem_acentos(nome or "")
    for a, b in ((r"\bu\.\s*h\.\s*", "unidade hospitalar "), (r"\bh\.\s*", "hospital "), (r"\bsub\b", "servico urgencia basica "),
                 (r"\bprof\.\s*", "professor "), (r"\bdr\.\s*", "doutor "), (r"\bn\.?\s*sra\.?\s*", "nossa senhora "),
                 (r"\bsta\.\s*", "santa "), (r"\bs\.\s*", "sao ")):
        s = re.sub(a, b, s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    vazias = {"de", "do", "da", "dos", "das", "e", "hospital", "servico", "urgencia", "unidade", "hospitalar", "basica", "em"}
    return {w for w in s.split() if w not in vazias and len(w) > 1}


def instituicoes_tempos(offline: bool) -> list[dict]:
    """A lista de instituições do site dos tempos de espera (para saber o endereço de cada uma)."""
    cache = PASTA / "instituicoes-tempos.json"
    if not offline:
        try:
            cache.write_bytes(obter(URL_INSTITUICOES))
        except Exception:
            pass
    return json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else []


def pagina_tempos(unidade: str, insts: list[dict]) -> dict:
    """Encontra a página da unidade em tempos.min-saude.pt. Os nomes não são iguais nos dois
    sítios ("H. D. Estefânia" e "Hospital D. Estefânia - Lisboa"): só aceita o par se todas as
    palavras do nosso nome aparecerem no outro, ou se forem quase iguais. Na dúvida, não inventa."""
    a = _tokens(unidade)
    melhor, nota = None, 0.0
    for t in insts:
        b = _tokens(t["name"])
        if not a or not b:
            continue
        jac = len(a & b) / len(a | b)
        ok = a <= b or jac >= 0.6
        if ok and (jac, t.get("hasEmergencyData")) > (nota, melhor and melhor.get("hasEmergencyData")):
            melhor, nota = t, jac
    if not melhor:
        return {"tempos_url": None, "tempos_nota": "não encontrei esta unidade no site dos tempos de espera"}
    if melhor.get("hasEmergencyData"):
        return {"tempos_url": f"{URL_TEMPOS}/instituicao/{melhor['id']}", "tempos_nome": melhor["name"]}
    uls = next((t for t in insts if t["id"] == melhor.get("ulsId") and t.get("hasEmergencyData")), None)
    if uls:
        return {"tempos_url": f"{URL_TEMPOS}/instituicao/{uls['id']}", "tempos_nome": uls["name"],
                "tempos_nota": f"o site agrupa esta unidade na {uls['name']}; nem sempre há lá tempos de urgência"}
    return {"tempos_url": None, "tempos_nota": "o site não publica tempos de urgência para esta unidade"}


def servicos(registos: list[dict]) -> list[dict]:
    """Junta as linhas (uma por valência) num registo por SERVIÇO de urgência,
    que é a porta por onde se entra.

    Armadilha dos dados reais: numa linha, a "unidade_hospitalar" é onde a
    valência é PRESTADA, que pode ser outro hospital da rede de referenciação
    (a cirurgia cardíaca da urgência de Beja é feita noutro hospital), ou
    simplesmente um erro de quem preencheu (a obstetrícia de Faro aparece
    em Évora). As coordenadas são do serviço; morada e telefone são da unidade.
    A "casa" de cada serviço é a unidade que aparece em mais linhas dele, e
    uma valência associada a outra unidade é ASSINALADA, nunca corrigida nem
    escondida: a ferramenta não sabe qual dos dois casos é."""
    linhas = {}
    for r in registos:
        linhas.setdefault(r.get("nome_do_servico_de_urgencia"), []).append(r)
    resultado = []
    for nome, rs in linhas.items():
        casa = Counter(r.get("unidade_hospitalar") for r in rs).most_common(1)[0][0]
        r0 = next(r for r in rs if r.get("unidade_hospitalar") == casa)
        geo = r0.get("localizacao_geografica") or {}
        if geo.get("lat") is None:
            continue
        s = {"unidade": casa, "servico": nome, "tipo": r0.get("tipo_de_urgencia"),
             "morada": ", ".join(x for x in (r0.get("endereco"), r0.get("codigo_postal"), r0.get("localidade")) if x),
             "telefone": str(int(r0["telefone"])) if isinstance(r0.get("telefone"), (int, float)) else r0.get("telefone"),
             "lat": geo["lat"], "lon": geo["lon"], "valencias": {}}
        for r in rs:
            s["valencias"][r.get("nome_da_valencia")] = {
                "idades": r.get("intervalo_idades"),
                "prestada_em": r.get("unidade_hospitalar"),
                "noutra_unidade": r.get("unidade_hospitalar") != casa,
                "por_iniciativa_propria": r.get("acesso_por_iniciativa_do_utente") == "Sim",
                "via_sns24": r.get("acesso_por_via_saude_24") == "Sim",
                "via_centro_de_saude": r.get("acesso_por_iniciativa_csp") == "Sim",
            }
        resultado.append(s)
    return resultado


def main() -> int:
    ap = argparse.ArgumentParser(description="Urgências do SNS mais próximas de um concelho (dados abertos).")
    ap.add_argument("concelho")
    ap.add_argument("--tipo", choices=sorted(TIPOS), default="adultos",
                    help="adultos (por omissão), criancas (0-17 anos) ou obstetricia")
    ap.add_argument("--n", type=int, default=5, help="quantas mostrar (por omissão 5)")
    ap.add_argument("--json", action="store_true", help="saída em JSON")
    ap.add_argument("--offline", action="store_true", help="não ir à internet; usar a cópia local")
    a = ap.parse_args()

    registos, origem = carregar_dados(a.offline)
    atualizado = None if a.offline else data_do_dataset()
    lat, lon, rotulo = geocodificar(a.concelho, a.offline)
    valencia = TIPOS[a.tipo]
    lista = []
    for s in servicos(registos):
        v = s["valencias"].get(valencia)
        if not v:
            continue
        lista.append({**{k: s[k] for k in ("unidade", "servico", "tipo", "morada", "telefone")},
                      "distancia_km": round(km(lat, lon, s["lat"], s["lon"]), 1),
                      "lat": round(s["lat"], 5), "lon": round(s["lon"], 5),
                      "idades": v["idades"], "acesso": v,
                      "outras_valencias": sorted(k for k in s["valencias"] if k != valencia)})
    lista.sort(key=lambda x: x["distancia_km"])
    lista = lista[: a.n]
    insts = instituicoes_tempos(a.offline)
    for r in lista:
        r.update(pagina_tempos(r["unidade"], insts))
    avisos = []
    if lon < -10 or lat < 36.8:
        avisos.append("Regiões autónomas (Madeira e Açores) têm serviços regionais de saúde que NÃO estão neste dataset. "
                      "Os resultados abaixo ficam no continente e não servem. Diz isto ao utilizador e sugere o serviço regional.")
    elif lista and lista[0]["distancia_km"] > 50:
        avisos.append(f"A mais próxima fica a {lista[0]['distancia_km']} km em linha reta. Sugere ligar ao SNS 24 antes de sair.")

    resultado = {
        "concelho": rotulo, "concelho_lat": round(lat, 5), "concelho_lon": round(lon, 5),
        "tipo_pedido": a.tipo, "valencia": valencia,
        "fonte": {"nome": "Portal da Transparência do SNS — Caracterização das valências de urgência",
                  "url": URL_PAGINA, "obtido_de": origem, "dataset_atualizado_em": atualizado},
        "avisos": avisos, "resultados": lista, "nao_sei": NAO_SEI,
    }
    if a.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return 0

    for av in avisos:
        print(f"⚠️  AVISO: {av}\n")
    print(f"Urgências com '{valencia}' mais próximas de {rotulo} (linha reta):")
    print(f"(coordenadas de {rotulo}: {lat:.5f}, {lon:.5f}, para o mapa)\n")
    for i, r in enumerate(lista, 1):
        acesso = r["acesso"]
        como = ", ".join(x for x, ok in (("por iniciativa própria", acesso["por_iniciativa_propria"]),
                                         ("via SNS 24", acesso["via_sns24"]),
                                         ("via centro de saúde", acesso["via_centro_de_saude"])) if ok) or "só por referenciação"
        print(f"{i}. {r['unidade']} — {r['distancia_km']} km")
        print(f"   {r['servico']} · {r['tipo']}")
        print(f"   Idades: {r['idades']} · Acesso: {como}")
        if acesso["noutra_unidade"]:
            print(f"   ⚠️  O dataset associa esta valência a outra unidade ({acesso['prestada_em']}). "
                  "Pode ser a rede de referenciação ou um erro nos dados: confirmar com o SNS 24.")
        print(f"   {r['morada']} · tel. {r['telefone']} · coordenadas {r['lat']}, {r['lon']}")
        if r.get("tempos_url"):
            print(f"   Tempos de espera: {r['tempos_url']}" + (f"  ({r['tempos_nota']})" if r.get("tempos_nota") else ""))
        else:
            print(f"   Tempos de espera: {r.get('tempos_nota', 'sem página')}")
    if not lista:
        print("Nenhuma encontrada. Não inventes uma: diz ao utilizador e sugere o SNS 24.")
    print(f"\nFonte: {resultado['fonte']['nome']} ({origem}"
          + (f"; dataset atualizado pelo SNS em {atualizado}" if atualizado else "") + ")")
    print(f"       {URL_PAGINA}")
    print("\nO que esta ferramenta NÃO sabe:")
    for n in NAO_SEI:
        print(f"  - {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
