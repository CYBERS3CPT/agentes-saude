# Competência 03 — /relatorio (11:00 — O conselho de administração)

> Parte do **assistente da ULS de Vale Fictício** (`assistente/`). Para ter só esta
> competência e as anteriores: `./demo/preparar.sh --ate 3`. A receita está em
> `assistente/.claude/skills/relatorio/SKILL.md`; dados em `assistente/dados/relatorio/`,
> resultados em `assistente/saida/relatorio/`.

Um agente que vai buscar dados abertos ao Portal da Transparência do SNS,
**escreve e corre os seus próprios scripts de análise**, faz gráficos e
conclusões, e só entrega depois de um verificador confirmar que cada número
do texto saiu de um script.

```bash
cd assistente
claude
```

```
/relatorio
/relatorio pulseiras verdes e azuis no último ano
/relatorio SNS 24 e urgências: quando o SNS 24 atende menos, as urgências enchem?
```

## O que este caso ensina

| Peça | Onde está |
|---|---|
| Ferramenta de dados | `ferramentas/dados_sns.py`: procurar, descrever e descarregar datasets |
| Código escrito pelo agente | `saida/relatorio/analise/*.py`, criados e corridos por ele |
| Verificação automática | `ferramentas/verificar.py`: "cada número tem a sua consulta" |
| Instruções | `CLAUDE.md`: data dos dados, comparar o comparável, correlação ≠ causa |
| Permissões | só escreve em `saida/`; `dados/` é só de leitura; `pip` pede autorização |

## Para apontar durante a demo

- **Abrir um script que o agente escreveu** em `saida/relatorio/analise/`. Toda a gente
  percebe a diferença entre "o modelo disse" e "este código calculou".
- **O verificador a falhar.** Se a primeira versão tiver um "cerca de 15 %" sem
  origem, o `verificar.py` recusa e o agente corrige sozinho. É o ciclo
  pensar → agir → observar a funcionar como controlo de qualidade.
- **A data dos dados.** Em novembro, os dados mais recentes são de agosto.
- **A terceira pergunta** (SNS 24 e urgências) é uma armadilha: o agente deve pôr a
  explicação em "Hipóteses a confirmar", não nas conclusões.
- **A permissão mais perigosa deste repositório** é `python3 saida/relatorio/analise/*`: o
  agente corre código que ele próprio escreveu. Aqui é aceitável porque só lê
  CSV locais, não há rede e tudo fica registado no diário. Num serviço a sério,
  isto corre numa sandbox.

## Sem internet

Os três datasets principais já estão em `dados/relatorio/` (descarregados a 23/11/2026).
`python3 ferramentas/dados_sns.py descarregar <dataset> --offline`.
