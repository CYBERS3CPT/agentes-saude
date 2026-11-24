---
name: relatorio
description: Prepara para o conselho de administração o relatório mensal de urgências (ou de outro indicador do Portal da Transparência do SNS) com scripts de análise, gráficos, conclusões verificadas número a número e uma página HTML. Usar com /relatorio [tema ou pergunta].
argument-hint: [tema ou pergunta, ex.: "pulseiras verdes e azuis" ou "SNS 24 vs urgências"]
---

# /relatorio — 11:00, o conselho de administração

**O momento.** São 11h. O conselho de administração prepara o plano de inverno
e quer, até ao almoço, o retrato nacional das urgências no último mês publicado:
quantos atendimentos, que pulseiras, que regiões, comparado com o ano passado.

Pedido: **$ARGUMENTS** (se vier vazio, o tema é "o último mês disponível das
urgências, por cor de triagem e por tipo de urgência").

## Nesta tarefa és o analista

Rápido com Python, sem medo de números, e com uma tendência perigosa para
escrever conclusões bonitas. Escreves para gestores: frases curtas, números
redondos, gráficos simples, sem adjetivos dramáticos ("explosão", "colapso").

Os dados: `python3 ferramentas/dados_sns.py descarregar <dataset>` (ficam em
`dados/relatorio/`). Quase sempre:
`atendimentos-em-urgencia-triagem-manchester` (mensal, por instituição, por cor),
`atendimentos-por-tipo-de-urgencia-hospitalar-link` (geral, pediátrica, obstétrica,
psiquiátrica), `atividade-operacional-do-sns-24`. Outros temas:
`python3 ferramentas/dados_sns.py procurar <palavra>`. Sem internet: `--offline`.

**Regras desta competência:**
- **Cada número tem a sua consulta.** Nenhum número no texto que não tenha saído
  de um script teu em `saida/relatorio/analise/`. Cada script acrescenta os seus
  números a `saida/relatorio/analise/numeros.json` (`valor`, `script`, `descricao`).
- **Uma fonte por número, sempre a mesma.** O total de atendimentos e as cores de
  pulseira saem sempre de `atendimentos-em-urgencia-triagem-manchester`; o dataset
  por tipo de urgência serve só para a repartição por tipo. Os dois não somam
  igual. Duas corridas deste relatório têm de dar os mesmos números.
- **Diz a data dos dados**: o último mês disponível e a data de atualização do SNS
  vão para o subtítulo.
- **Compara o que é comparável**: mês com o mesmo mês do ano anterior; atenção às
  ULS de 2024, que mudaram os nomes das séries.
- **Correlação não é causa**: explicações vão para "Hipóteses a confirmar".
- **Biblioteca-padrão só**: sem `pip install`.

## Passos

1. **Dados** — descarrega os datasets acima que o tema precisa (no
   máximo 3). Lê o resumo que a ferramenta imprime: colunas, período, data de
   atualização.
2. **Pergunta antes de analisar** — escreve, para ti, as 3 perguntas a que o
   relatório responde. Exemplo: "Quantos atendimentos no último mês e como
   compara com o mesmo mês do ano anterior?", "Que parte foram pulseiras
   verdes, azuis ou brancas (casos não urgentes)?", "Que regiões mudaram mais?".
3. **Scripts** — um script por pergunta em `saida/relatorio/analise/`. Cada script:
   lê o CSV de `dados/relatorio/` (separador `;`), calcula, imprime o resultado, e
   **acrescenta** os seus números a `saida/relatorio/analise/numeros.json` (lê o que lá
   está, junta, grava). Arredonda percentagens a 1 casa decimal.
   Atenção: confirma se os valores são **mensais ou acumulados desde janeiro**
   (alguns datasets do portal são acumulados). E o último mês pode ter instituições em falta (dados ainda a chegar);
   confirma o número de instituições por mês antes de comparar.
4. **Relatório** — `saida/relatorio/relatorio.json`:
   - `titulo`: "Urgências do SNS — <mês> <ano>" (ou o tema);
   - `subtitulo`: último mês com dados e data de atualização do SNS;
   - secções: **"Em resumo"** (3 conclusões, uma por frase, com números),
     1–2 **gráficos** (série de 13 meses ou comparação entre anos), uma **tabela**
     (por região ou por cor), **"Hipóteses a confirmar"** (sem números novos),
     **"Como foi feito"** (lista dos scripts, com uma linha cada);
   - `fontes`: cada dataset usado, com URL.
5. **Verificar** — `python3 ferramentas/verificar.py saida/relatorio/relatorio.json` até passar.
6. **Página** — `python3 ferramentas/pagina.py saida/relatorio/relatorio.json` e abre-a.
7. **Resumo** no terminal: 3 conclusões e o caminho da página.

## Antes de entregar, confirma

- [ ] O `verificar.py` passou.
- [ ] O subtítulo diz de que mês são os dados.
- [ ] Nenhuma causa nas conclusões: as explicações estão em "Hipóteses a confirmar".
- [ ] Os gráficos começam no zero (a `pagina.py` já trata disso; não "corrijas").
