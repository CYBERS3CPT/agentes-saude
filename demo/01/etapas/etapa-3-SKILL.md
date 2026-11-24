---
name: onde-ir
description: Diz a quem ligar e a que urgência do SNS ir, com dados abertos, e faz uma página. Usar com /onde-ir <concelho>, <situação>.
argument-hint: <concelho>, <situação>
---

Pedido: **$ARGUMENTS**

1. Emergência? Se sim, 112 no topo.
2. Tipo: criancas (< 18), obstetricia ou adultos.
3. `python3 ferramentas/urgencias.py "<concelho>" --tipo <tipo> --n 5`. Lê os avisos.
3b. Para as 2 mais próximas: abre no browser a página `Tempos de espera:`, espera 15 s,
    lê estado, utentes à espera e tempo médio, e anota a hora. No fim, fecha o browser.
4. Escreve `saida/onde-ir/<concelho>.json` no formato de `python3 ferramentas/pagina.py --exemplo`:
   aviso_topo ("Informação pública, não substitui a avaliação de um profissional. Em emergência ligue 112."),
   alerta info com o SNS 24, secções "O que fazer agora", "Agora, segundo o SNS" (tabela com o que leste),
   "Urgências mais próximas" (tabela, 3),
   "O que não sei" (lista da ferramenta), fontes.
5. `python3 ferramentas/pagina.py saida/onde-ir/<concelho>.json --tema clinico` e abre a página.
6. Resumo de 3 linhas.
