"""06 — Monta saida/relatorio/relatorio.json a partir de numeros.json (nenhum número escrito à mão).
Correr depois de 01–05."""
import json
import pathlib

from comum import MESES, NUMEROS, RAIZ

N = {k: v["valor"] for k, v in json.loads(NUMEROS.read_text(encoding="utf-8")).items()}
AQUI = pathlib.Path(__file__).parent
serie = json.loads((AQUI / "serie_13m.json").read_text(encoding="utf-8"))
tabela = json.loads((AQUI / "tabela_regioes.json").read_text(encoding="utf-8"))
meta = json.loads((RAIZ / "dados/relatorio/atendimentos-em-urgencia-triagem-manchester.meta.json").read_text(encoding="utf-8"))
meta_t = json.loads((RAIZ / "dados/relatorio/atendimentos-por-tipo-de-urgencia-hospitalar-link.meta.json").read_text(encoding="utf-8"))


def i(x):
    return f"{int(x):,}".replace(",", " ")


def p(x):
    return f"{x:.1f}".replace(".", ",") + " %"


def sp(x):
    return ("+" if x > 0 else "−") + p(abs(x))


MES_LONGO = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
             "setembro", "outubro", "novembro", "dezembro"]
mes_txt = "agosto"
assert serie["rotulos"][-1].startswith(MESES[7]), "o texto assume que o último mês é agosto"
d = meta["atualizado_pelo_sns"]
atualizado = f"{int(d[8:])} de {MES_LONGO[int(d[5:7]) - 1]} de {d[:4]}"

rel = {
    "titulo": "Urgências do SNS — agosto 2026",
    "subtitulo": f"Último mês com dados: agosto de 2026 · Dados atualizados pelo SNS a {atualizado} · "
                 "Comparação com agosto de 2025",
    "alertas": [{"nivel": "info", "texto":
                 "Os dados do portal são acumulados desde janeiro; os valores mensais foram obtidos por diferença "
                 f"entre meses. Agosto de 2026 tem dados das {i(N['n_instituicoes'])} instituições, tal como agosto de 2025."}],
    "seccoes": [
        {"titulo": "Em resumo", "lista": [
            f"Em agosto de 2026 houve {i(N['total_ult'])} atendimentos nas urgências do SNS, "
            f"{p(N['var_total_pct'])} mais do que em agosto de 2025 ({i(N['total_homologo'])}); "
            f"no acumulado de janeiro a agosto, o ano está {p(N['queda_acum_pct'])} abaixo de 2025.",
            f"Um em cada três atendimentos ({p(N['pct_nao_urgentes_ult'])}) teve pulseira verde, azul ou branca, "
            f"praticamente o mesmo que um ano antes ({p(N['pct_nao_urgentes_hom'])}); "
            f"vermelhas e laranjas foram {p(N['pct_vermelha_laranja_ult'])}.",
            f"Lisboa e Vale do Tejo ({sp(N['reg_lisboa_e_vale_do_tejo_var'])}) e o Alentejo "
            f"({sp(N['reg_alentejo_var'])}) foram as regiões que mais subiram; o Algarve foi a única a descer "
            f"({p(N['reg_algarve_queda'])} a menos) e o Norte ficou estável ({sp(N['reg_norte_var'])}).",
        ]},
        {"titulo": f"Atendimentos por mês, últimos {N['n_meses_serie']} meses", "grafico": {
            "tipo": "barras", "rotulos": serie["rotulos"],
            "series": [{"nome": "Atendimentos (Triagem de Manchester)", "valores": serie["valores"]}],
            "unidade": "atendimentos"}},
        {"titulo": "Pulseiras de triagem: agosto 2025 e agosto 2026", "grafico": {
            "tipo": "barras",
            "rotulos": ["Vermelha", "Laranja", "Amarela", "Verde", "Azul", "Branca", "Sem triagem"],
            "series": [
                {"nome": "agosto 2025", "valores": [N[f"n_{c}_hom"] for c in
                                                    ["vermelha", "laranja", "amarela", "verde", "azul", "branca", "sem_triagem"]]},
                {"nome": "agosto 2026", "valores": [N[f"n_{c}_ult"] for c in
                                                    ["vermelha", "laranja", "amarela", "verde", "azul", "branca", "sem_triagem"]]}],
            "unidade": "atendimentos"}},
        {"titulo": "Por cor de pulseira", "tabela": {
            "colunas": ["Pulseira", "Ago 2025", "Ago 2026", "Peso em ago 2026", "Variação"],
            "linhas": [[nome, i(N[f"n_{c}_hom"]), i(N[f"n_{c}_ult"]), p(N[f"pct_{c}_ult"]), sp(N[f"var_{c}_pct"])]
                       for nome, c in [("Vermelha", "vermelha"), ("Laranja", "laranja"), ("Amarela", "amarela"),
                                       ("Verde", "verde"), ("Azul", "azul"), ("Branca", "branca"),
                                       ("Sem triagem", "sem_triagem")]]
                      + [["Total", i(N["total_homologo"]), i(N["total_ult"]), p(100.0), sp(N["var_total_pct"])]]}},
        {"titulo": "Por região", "tabela": {
            "colunas": ["Região", "Ago 2025", "Ago 2026", "Variação", "Peso no total"],
            "linhas": [[r, i(a), i(b), sp(v), p(w)] for r, a, b, v, w in tabela]}},
        {"titulo": "Por tipo de urgência (outra fonte)", "texto":
            f"Em agosto de 2026, {p(N['tipo_geral_pct_ult'])} dos atendimentos foram em urgência geral, "
            f"{p(N['tipo_pediatrica_pct_ult'])} em pediátrica, {p(N['tipo_obstetrica_pct_ult'])} em obstétrica e "
            f"{p(N['tipo_psiquiatrica_pct_ult'])} em psiquiátrica. A pediátrica subiu {p(N['tipo_pediatrica_var'])} "
            "face a agosto de 2025. Estes valores vêm do dataset por tipo de urgência, que não soma igual ao da "
            "Triagem de Manchester: servem só para a repartição, não para o total."},
        {"titulo": "Hipóteses a confirmar", "lista": [
            "A subida de agosto contrasta com o acumulado do ano abaixo de 2025: ver se os primeiros meses de 2026 "
            "foram mais fracos (por exemplo, uma época de gripe mais leve) ou se agosto teve um efeito pontual.",
            "A descida das pulseiras brancas e dos atendimentos sem triagem pode refletir mudanças de registo ou de "
            "circuitos (encaminhamentos pela linha telefónica do SNS, consultas de doença aguda), e não menos procura. Confirmar com as ULS.",
            "As subidas em Lisboa e Vale do Tejo e no Alentejo podem estar ligadas a urgências encerradas ou com "
            "horário reduzido noutras unidades durante o verão, que desviam doentes. Confirmar com as escalas.",
            "A descida no Algarve pode ter a ver com a afluência turística de agosto; não há dados de turismo neste relatório.",
        ]},
        {"titulo": "Como foi feito", "lista": [
            "00_explorar.py — confirma que os valores são acumulados desde janeiro e conta as instituições por mês.",
            "comum.py — converte acumulados em valores mensais (mês menos mês anterior, por instituição).",
            "01_totais.py — total mensal (todas as pulseiras e sem triagem), série de " + str(N["n_meses_serie"]) + " meses e acumulado de janeiro a agosto.",
            "02_cores.py — atendimentos e percentagem por cor de pulseira, agosto 2026 e agosto 2025.",
            "03_regioes.py — total por região e variação face a agosto de 2025.",
            "04_tipos.py — repartição por tipo de urgência (dataset por tipo).",
            "05_controlo.py — procura valores mensais negativos (nenhum nos meses comparados) e compara as duas fontes: "
            f"em agosto de 2025 o dataset por tipo soma mais {i(N['dif_fontes_hom'])} atendimentos do que o de Manchester "
            f"e, ano a ano, desce {p(N['tipo_soma_queda'])} em vez de subir. Por isso o total vem sempre da Triagem de Manchester.",
            "06_relatorio.py — monta este relatório a partir de numeros.json; nenhum número foi escrito à mão.",
        ]},
    ],
    "fontes": [
        {"nome": f"Portal da Transparência SNS — {meta['titulo']} (atualizado a {meta['atualizado_pelo_sns']})",
         "url": meta["url"]},
        {"nome": f"Portal da Transparência SNS — {meta_t['titulo']} (atualizado a {meta_t['atualizado_pelo_sns']})",
         "url": meta_t["url"]},
    ],
}
saida = RAIZ / "saida" / "relatorio" / "relatorio.json"
saida.write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")
print("Escrito:", saida)
