# Competência 04 — /norma (14:00 — A saúde ocupacional)

> Parte do **assistente da ULS de Vale Fictício** (`assistente/`). Para ter só esta
> competência e as anteriores: `./demo/preparar.sh --ate 4`. A receita está em
> `assistente/.claude/skills/norma/SKILL.md`; dados em `assistente/dados/norma/`,
> resultados em `assistente/saida/norma/`.

**O que mostra:** um agente que responde a perguntas sobre normas **com a
página e a frase exata**, e que diz "não encontrei" quando não encontra.
É a versão de bolso de um RAG: primeiro procurar, depois responder com o
que se encontrou.

| Peça | Onde |
|---|---|
| Instruções | `CLAUDE.md` — "sem citação, não há afirmação" |
| Receita | `.claude/skills/norma/SKILL.md` → `/norma <pergunta>` |
| Ferramenta de pesquisa | `ferramentas/procurar.py` (BM25, só Python) |
| Biblioteca | `dados/norma/` — 4 PDFs da DGS + texto por página + `normas.json` (estado de cada uma) |
| Página | `ferramentas/pagina.py` (tema `clinico`) |
| Permissões | `.claude/settings.json` — internet e edição de `dados/` pedem autorização |
| Diário | `.claude/hooks/diario.py` → `saida/diario.md` |

## Correr

```bash
cd assistente
claude
```

```
/norma Quem trabalha nos serviços centrais do Ministério da Saúde tem vacina da gripe gratuita?
```

Ou usar só a ferramenta, sem agente: `python3 ferramentas/procurar.py "nirsevimab recém-nascido"`.

## O que apontar na demo

1. **Ele procura antes de responder** (o diário mostra 2–3 chamadas ao `procurar.py`).
2. **A citação existe mesmo.** Abrir o PDF na página indicada e ler a frase.
3. **A versão revogada.** A pesquisa devolve trechos da versão original da
   Norma 006/2026, marcada "REVOGADA". O agente deve usar a de 08/10/2026.
   Sem os metadados em `normas.json`, a versão velha parecia igualmente boa.
4. **"Não encontrei nas normas carregadas."** A pergunta sobre antibióticos
   não tem resposta aqui. A ferramenta devolve trechos com pontuação baixa;
   o agente tem de os recusar em vez de "compor" uma resposta.

## Riscos que este caso ensina

- **Alucinação com cara séria:** uma citação inventada é pior do que nenhuma.
  Confirmar uma citação contra o `.txt` é trivial (`grep`) — e um bom teste automático.
- **Desatualização:** as normas mudam. A coleção tem data (23/11/2026). Um
  sistema real precisa de um dono que a mantenha.
- **Conselho clínico:** o agente fala de grupos, não de pessoas.
- **Recuperação fraca:** BM25 não percebe sinónimos que não estão no texto.
  Se a pergunta usa palavras diferentes da norma, pode falhar. Embeddings ajudam,
  mas o princípio (citar ou calar) é o que protege.

Fontes e datas: [`dados/normas/FONTES.md`](../../assistente/dados/norma/FONTES.md).
