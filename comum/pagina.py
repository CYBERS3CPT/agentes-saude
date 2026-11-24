#!/usr/bin/env python3
"""
pagina.py — transforma o trabalho do agente (um JSON) numa página HTML.

É a mesma ferramenta nos cinco casos. O agente DECIDE o conteúdo (o que
recomendar, que números mostrar, que conclusões tirar); o código FORMATA.
Cada um faz aquilo em que é bom, e a página sai sempre com o mesmo cuidado.

    python3 ferramentas/pagina.py saida/resultado.json
    python3 ferramentas/pagina.py saida/resultado.json --tema noite
    python3 ferramentas/pagina.py --exemplo          # mostra o formato

Se o JSON estiver mal, a ferramenta diz exatamente o quê, e o agente corrige.
É o ciclo pensar → agir → OBSERVAR, em pequenino.

Só biblioteca-padrão do Python. Sem pip install, sem internet.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import pathlib
import re
import sys

TEMAS = {
    # nome: (fundo, texto, destaque, destaque2, cartão, linha, suave)
    "nova":   ("#F4F7FF", "#0B0B0B", "#3676FE", "#0DDF70", "#FFFFFF", "#DCE5FA", "#5A6275"),
    "clinico": ("#F6F8F7", "#14201C", "#0E7C66", "#E0A31A", "#FFFFFF", "#DCE6E2", "#5B6B66"),
    "noite":  ("#14161C", "#ECEEF3", "#8AB4FF", "#7CE0A3", "#1E2129", "#2C303A", "#A6ACBA"),
}
NIVEIS = {"info": ("ℹ️", "#3676FE"), "aviso": ("⚠️", "#E0A31A"), "perigo": ("🛑", "#D64545"),
          "ok": ("✅", "#14A06B")}
CORES_SERIES = ["#3676FE", "#0DDF70", "#E0A31A", "#D64545", "#8E5CF7", "#14A0A0"]

EXEMPLO = {
    "titulo": "Onde vou hoje? — Odivelas",
    "subtitulo": "Criança de 3 anos, febre desde ontem, sem sinais de alarme",
    "aviso_topo": "Informação pública, não substitui a avaliação de um profissional. Em emergência: 112.",
    "alertas": [{"nivel": "info", "texto": "Antes de sair de casa, ligue SNS 24: 808 24 24 24."}],
    "seccoes": [
        {"titulo": "Recomendação", "texto": "Ligar SNS 24 primeiro. Se encaminhar para urgência, "
                                           "a pediátrica mais próxima é a do **Hospital X** (6,2 km)."},
        {"titulo": "Urgências pediátricas mais próximas",
         "tabela": {"colunas": ["Unidade", "Tipo", "Distância", "Telefone"],
                    "linhas": [["Hospital X", "Polivalente", "6,2 km", "210 000 000"]]}},
        {"titulo": "Atendimentos por mês",
         "grafico": {"tipo": "barras", "rotulos": ["jun", "jul", "ago"],
                     "series": [{"nome": "Atendimentos", "valores": [9100, 8800, 8300]}],
                     "unidade": "atendimentos"}},
        {"titulo": "No mapa", "mapa": {"centro": {"nome": "Odivelas", "lat": 38.79, "lon": -9.18},
                                       "pontos": [{"nome": "Hospital X", "lat": 38.81, "lon": -9.16,
                                                   "etiqueta": "aberta · 10 à espera · 1h18 (às 08:12)", "nivel": "ok"}],
                                       "nota": "Distâncias em linha reta."}},
        {"titulo": "O que não sei", "lista": ["Tempos de espera em tempo real: ver tempos.min-saude.pt"]},
        {"titulo": "Cartões (opcional)", "cartoes": [
            {"titulo": "Pedido #12", "etiqueta": "Acessos", "nivel": "aviso",
             "linhas": ["Encaminhar: equipa de identidade", "Prioridade: alta"]}]},
    ],
    "fontes": [{"nome": "Portal da Transparência SNS — valências de urgência",
                "url": "https://transparencia.sns.gov.pt/explore/dataset/caracterizacao-das-valencias-de-urgencia/"}],
}


def esc(x) -> str:
    return html.escape(str(x)) if x is not None else ""


def md(x) -> str:
    """Markdown mínimo: **negrito**, `código`, [ligações](url) e parágrafos. Nada mais."""
    t = esc(x)
    t = re.sub(r"\[([^\]]+)\]\(((?:https?://|\.{0,2}/|[\w./-]+\.html)[^)\s]*)\)", r'<a href="\2">\1</a>', t)
    # negrito só com ** isolados: "***4321" (um número mascarado) não é negrito
    t = re.sub(r"(?<!\*)\*\*(?!\*)(.+?)(?<!\*)\*\*(?!\*)", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return "".join(f"<p>{p.strip()}</p>" for p in t.split("\n\n") if p.strip())


def validar(p: dict) -> list[str]:
    erros = []
    if not isinstance(p.get("titulo"), str):
        erros.append("falta 'titulo' (texto)")
    if not isinstance(p.get("seccoes"), list) or not p.get("seccoes"):
        erros.append("falta 'seccoes' (lista com pelo menos uma secção)")
    for i, s in enumerate(p.get("seccoes") or []):
        if not isinstance(s, dict) or "titulo" not in s:
            erros.append(f"seccoes[{i}] precisa de 'titulo'")
            continue
        if not any(k in s for k in ("texto", "lista", "tabela", "grafico", "cartoes", "mapa")):
            erros.append(f"seccoes[{i}] ('{s['titulo']}') precisa de texto, lista, tabela, grafico, cartoes ou mapa")
        m = s.get("mapa")
        if m is not None:
            c = m.get("centro") or {}
            if not all(isinstance(c.get(k), (int, float)) for k in ("lat", "lon")):
                erros.append(f"seccoes[{i}].mapa.centro precisa de lat e lon (números)")
            for j, pt in enumerate(m.get("pontos", [])):
                if not all(isinstance(pt.get(k), (int, float)) for k in ("lat", "lon")) or not pt.get("nome"):
                    erros.append(f"seccoes[{i}].mapa.pontos[{j}] precisa de nome, lat e lon")
        t = s.get("tabela")
        if t is not None:
            n = len(t.get("colunas", []))
            for j, linha in enumerate(t.get("linhas", [])):
                if len(linha) != n:
                    erros.append(f"seccoes[{i}].tabela.linhas[{j}] tem {len(linha)} valores e há {n} colunas")
        g = s.get("grafico")
        if g is not None:
            n = len(g.get("rotulos", []))
            for j, serie in enumerate(g.get("series", [])):
                vals = serie.get("valores", [])
                if len(vals) != n:
                    erros.append(f"seccoes[{i}].grafico.series[{j}] tem {len(vals)} valores e há {n} rótulos")
                if any(not isinstance(v, (int, float)) for v in vals if v is not None):
                    erros.append(f"seccoes[{i}].grafico.series[{j}]: os valores têm de ser números")
    for i, a in enumerate(p.get("alertas") or []):
        if a.get("nivel") not in NIVEIS:
            erros.append(f"alertas[{i}].nivel tem de ser um de {sorted(NIVEIS)}")
    return erros


def numero(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float) and not v.is_integer():
        return f"{v:,.1f}".replace(",", " ").replace(".", ",")
    return f"{int(v):,}".replace(",", " ")


def mapa_svg(m: dict, cor_texto: str, cor_linha: str, cor_destaque: str) -> str:
    """Um mapa sem mapa: o centro (o concelho), anéis de distância e os pontos
    (as urgências) no sítio certo, em linha reta. Sem tiles, sem internet."""
    import math
    c = m["centro"]
    W, H = 760, 470
    cx, cy = W / 2, H / 2 + 6
    kx = 111.32 * math.cos(math.radians(c["lat"]))  # km por grau de longitude
    pts = [((p["lon"] - c["lon"]) * kx, (p["lat"] - c["lat"]) * 110.57, p) for p in m.get("pontos", [])]
    dmax = max([math.hypot(x, y) for x, y, _ in pts] + [1.0])
    aneis = m.get("aneis_km") or [r for r in (1, 2, 5, 10, 20, 50, 100) if r < dmax * 1.3][-3:] or [round(dmax)]
    raio = max(aneis[-1], dmax) * 1.12
    esc_ = (min(W, H) / 2 - 34) / raio
    cores = {"ok": "#14A06B", "aviso": "#E0A31A", "perigo": "#D64545", "info": "#3676FE"}
    o = [f'<svg viewBox="0 0 {W} {H}" class="mapa" role="img" aria-label="Mapa das distâncias a partir de {esc(c.get("nome", "centro"))}">']
    for r in aneis:
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r * esc_:.1f}" fill="none" stroke="{cor_linha}" stroke-width="1.5" stroke-dasharray="4 5"/>'
                 f'<text x="{cx + r * esc_ * 0.71 + 4:.1f}" y="{cy - r * esc_ * 0.71 - 4:.1f}" font-size="12" fill="{cor_texto}">{r} km</text>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{cor_destaque}"/><circle cx="{cx}" cy="{cy}" r="16" fill="{cor_destaque}" opacity=".18"/>'
             f'<text x="{cx}" y="{cy + 34}" text-anchor="middle" font-size="14" font-weight="700" fill="{cor_texto}">{esc(c.get("nome", ""))}</text>')
    for x, y, p in pts:
        px, py = cx + x * esc_, cy - y * esc_
        cor = cores.get(p.get("nivel"), "#8A93A6")
        lado = "start" if px >= cx else "end"
        dx = 16 if px >= cx else -16
        o.append(f'<line x1="{cx}" y1="{cy}" x2="{px:.1f}" y2="{py:.1f}" stroke="{cor}" stroke-width="1" opacity=".35"/>'
                 f'<circle cx="{px:.1f}" cy="{py:.1f}" r="11" fill="{cor}"><title>{esc(p["nome"])}</title></circle>'
                 f'<text x="{px + dx:.1f}" y="{py - 2:.1f}" text-anchor="{lado}" font-size="15" font-weight="700" fill="{cor_texto}">{esc(p["nome"])}</text>')
        if p.get("etiqueta"):
            o.append(f'<text x="{px + dx:.1f}" y="{py + 16:.1f}" text-anchor="{lado}" font-size="13" fill="{cor}">{esc(p["etiqueta"])}</text>')
    o.append("</svg>")
    return "".join(o)


def grafico_svg(g: dict, cor_texto: str, cor_linha: str) -> str:
    """Barras agrupadas ou linhas, em SVG puro. Escala a começar no zero
    (um gráfico que corta o eixo é uma pequena mentira)."""
    rotulos, series = g["rotulos"], g["series"]
    tipo = g.get("tipo", "barras")
    L, A, mE, mB, mT = 760, 300, 64, 44, 16
    vals = [v for s in series for v in s["valores"] if v is not None]
    vmax = max(vals) if vals else 1
    passo = 10 ** max(0, len(str(int(vmax))) - 1)
    topo = (int(vmax / passo) + 1) * passo or 1
    largura_util, altura_util = L - mE - 12, A - mB - mT
    y = lambda v: mT + altura_util * (1 - v / topo)
    partes = [f'<svg viewBox="0 0 {L} {A + 26 * ((len(series) > 1))}" role="img" '
              f'aria-label="{esc(g.get("titulo", "gráfico"))}" class="grafico">']
    for k in range(5):
        v = topo * k / 4
        partes.append(f'<line x1="{mE}" x2="{L - 12}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{cor_linha}"/>'
                      f'<text x="{mE - 8}" y="{y(v) + 4:.1f}" text-anchor="end" font-size="12" fill="{cor_texto}">{numero(v)}</text>')
    n = max(1, len(rotulos))
    slot = largura_util / n
    salto = max(1, int(n / 14) + (n > 14))
    for i, r in enumerate(rotulos):
        if i % salto == 0:
            partes.append(f'<text x="{mE + slot * (i + .5):.1f}" y="{A - mB + 18}" text-anchor="middle" '
                          f'font-size="12" fill="{cor_texto}">{esc(r)}</text>')
    for j, s in enumerate(series):
        cor = s.get("cor") or CORES_SERIES[j % len(CORES_SERIES)]
        if tipo == "linhas":
            pts = [(mE + slot * (i + .5), y(v)) for i, v in enumerate(s["valores"]) if v is not None]
            partes.append(f'<polyline fill="none" stroke="{cor}" stroke-width="2.5" points="'
                          + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + '"/>')
            for (a, b), v in zip(pts, [v for v in s["valores"] if v is not None]):
                partes.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="3" fill="{cor}"><title>{esc(s["nome"])}: {numero(v)}</title></circle>')
        else:
            bw = slot * .8 / len(series)
            for i, v in enumerate(s["valores"]):
                if v is None:
                    continue
                x = mE + slot * i + slot * .1 + bw * j
                partes.append(f'<rect x="{x:.1f}" y="{y(v):.1f}" width="{bw - 2:.1f}" height="{y(0) - y(v):.1f}" '
                              f'rx="2" fill="{cor}"><title>{esc(rotulos[i])} · {esc(s["nome"])}: {numero(v)}</title></rect>')
    if len(series) > 1:
        x = mE
        for j, s in enumerate(series):
            cor = s.get("cor") or CORES_SERIES[j % len(CORES_SERIES)]
            partes.append(f'<rect x="{x}" y="{A + 8}" width="12" height="12" rx="2" fill="{cor}"/>'
                          f'<text x="{x + 18}" y="{A + 18}" font-size="13" fill="{cor_texto}">{esc(s["nome"])}</text>')
            x += 30 + 8 * len(s["nome"])
    partes.append("</svg>")
    return "".join(partes)


def gerar_html(p: dict, tema: str) -> str:
    fundo, texto, dest, dest2, cartao, linha, suave = TEMAS[tema]
    corpo = []
    if p.get("aviso_topo"):
        corpo.append(f'<div class="faixa">{esc(p["aviso_topo"])}</div>')
    for a in p.get("alertas") or []:
        ic, cor = NIVEIS[a["nivel"]]
        corpo.append(f'<div class="alerta" style="border-color:{cor}"><span>{ic}</span><div>{md(a["texto"])}</div></div>')
    for s in p["seccoes"]:
        bloco = [f'<section><h2>{esc(s["titulo"])}</h2>']
        if s.get("texto"):
            bloco.append(md(s["texto"]))
        if s.get("lista"):
            bloco.append("<ul>" + "".join(f"<li>{md(i)[3:-4]}</li>" for i in s["lista"]) + "</ul>")
        if s.get("tabela"):
            t = s["tabela"]
            bloco.append('<div class="tabela"><table><thead><tr>' + "".join(f"<th>{esc(c)}</th>" for c in t["colunas"])
                         + "</tr></thead><tbody>" + "".join(
                             "<tr>" + "".join(f"<td>{esc(numero(c) if isinstance(c, (int, float)) and not isinstance(c, bool) else c)}</td>" for c in l) + "</tr>"
                             for l in t.get("linhas", [])) + "</tbody></table></div>")
            if t.get("nota"):
                bloco.append(f'<p class="nota">{esc(t["nota"])}</p>')
        if s.get("grafico"):
            g = s["grafico"]
            bloco.append(grafico_svg(g, suave, linha))
            if g.get("nota"):
                bloco.append(f'<p class="nota">{esc(g["nota"])}</p>')
        if s.get("mapa"):
            bloco.append(mapa_svg(s["mapa"], texto, linha, dest))
            if s["mapa"].get("nota"):
                bloco.append(f'<p class="nota">{esc(s["mapa"]["nota"])}</p>')
        if s.get("cartoes"):
            bloco.append('<div class="cartoes">')
            for c in s["cartoes"]:
                cor = NIVEIS.get(c.get("nivel", ""), ("", dest))[1]
                bloco.append(f'<article style="border-top-color:{cor}"><header><strong>{esc(c.get("titulo", ""))}</strong>'
                             + (f'<span class="etiqueta" style="background:{cor}">{esc(c["etiqueta"])}</span>' if c.get("etiqueta") else "")
                             + "</header>" + "".join(f"<p>{md(l)[3:-4]}</p>" for l in c.get("linhas", [])) + "</article>")
            bloco.append("</div>")
        bloco.append("</section>")
        corpo.append("".join(bloco))
    if p.get("fontes"):
        corpo.append('<section class="fontes"><h2>Fontes</h2><ul>' + "".join(
            f'<li><a href="{esc(f["url"])}">{esc(f["nome"])}</a></li>' if f.get("url") else f'<li>{esc(f.get("nome", f))}</li>'
            for f in p["fontes"]) + "</ul></section>")
    gerado = p.get("gerado_em") or dt.datetime.now().strftime("%d/%m/%Y %H:%M")
    return f"""<!DOCTYPE html>
<html lang="pt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(p["titulo"])}</title>
<style>
:root{{color-scheme:{'dark' if tema == 'noite' else 'light'}}}
*{{box-sizing:border-box}}
body{{margin:0;background:{fundo};color:{texto};font:17px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
main{{max-width:900px;margin:0 auto;padding:40px 22px 60px}}
h1{{font-size:2.1rem;line-height:1.15;margin:0 0 6px;letter-spacing:-.01em}}
.sub{{color:{suave};margin:0 0 22px;font-size:1.08rem}}
.faixa{{background:{texto};color:{fundo};padding:10px 14px;border-radius:8px;font-weight:600;margin:0 0 14px}}
.alerta{{display:flex;gap:12px;align-items:flex-start;background:{cartao};border-left:5px solid;padding:10px 14px;border-radius:8px;margin:0 0 10px}}
.alerta p{{margin:0}}
section{{background:{cartao};border:1px solid {linha};border-radius:14px;padding:18px 22px;margin:16px 0}}
h2{{font-size:1.15rem;margin:0 0 10px;color:{dest}}}
section p{{margin:.4em 0}}
code{{background:{linha};padding:1px 5px;border-radius:4px;font-size:.92em}}
.tabela{{overflow-x:auto}}
table{{border-collapse:collapse;width:100%;font-size:.95rem}}
th{{text-align:left;border-bottom:2px solid {dest};padding:6px 8px;white-space:nowrap}}
td{{border-bottom:1px solid {linha};padding:6px 8px;vertical-align:top}}
.grafico{{width:100%;height:auto;display:block;margin-top:6px}}
.mapa{{width:100%;height:auto;display:block;background:{fundo};border-radius:10px}}
.nota{{color:{suave};font-size:.88rem}}
.cartoes{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}}
.cartoes article{{border:1px solid {linha};border-top:5px solid;border-radius:10px;padding:10px 12px;font-size:.94rem}}
.cartoes header{{display:flex;justify-content:space-between;gap:8px;align-items:center;margin-bottom:4px}}
.etiqueta{{color:#fff;border-radius:99px;padding:1px 9px;font-size:.78rem;white-space:nowrap}}
.fontes a{{color:{dest}}}
footer{{color:{suave};font-size:.85rem;margin-top:24px}}
@media print{{body{{background:#fff}}section{{break-inside:avoid}}}}
</style></head><body><main>
<h1>{esc(p["titulo"])}</h1>
{f'<p class="sub">{esc(p["subtitulo"])}</p>' if p.get("subtitulo") else ""}
{"".join(corpo)}
<footer>Gerado por um agente de IA em {esc(gerado)}. Confirme sempre a informação nas fontes.</footer>
</main></body></html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Transforma o JSON do agente numa página HTML.")
    ap.add_argument("ficheiro", nargs="?", help="o JSON escrito pelo agente")
    ap.add_argument("--tema", choices=sorted(TEMAS), default="nova")
    ap.add_argument("--exemplo", action="store_true", help="mostra o formato esperado")
    a = ap.parse_args()
    if a.exemplo:
        print(json.dumps(EXEMPLO, ensure_ascii=False, indent=2))
        return 0
    if not a.ficheiro:
        ap.error("indica o ficheiro JSON (ou --exemplo para ver o formato)")
    caminho = pathlib.Path(a.ficheiro)
    try:
        p = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERRO: não encontro {caminho}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"ERRO: JSON inválido em {caminho}: linha {e.lineno}, coluna {e.colno}: {e.msg}", file=sys.stderr)
        return 2
    erros = validar(p)
    if erros:
        print("ERRO: o JSON não está no formato certo. Corrige e corre outra vez:", file=sys.stderr)
        for e in erros:
            print(f"  - {e}", file=sys.stderr)
        print("Formato: python3 ferramentas/pagina.py --exemplo", file=sys.stderr)
        return 1
    destino = caminho.with_suffix(".html")
    destino.write_text(gerar_html(p, a.tema), encoding="utf-8")
    print(f"Página: {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
