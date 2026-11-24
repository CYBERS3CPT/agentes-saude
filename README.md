# 🏥 Agentes de IA na saúde, ao vivo

**Um dia na ULS de Vale Fictício: um assistente de IA chega de manhã sem saber
nada e, ao fim do dia, tem cinco competências. Cada uma construída com o
Claude Code, sem escrever código, e posta à prova com uma armadilha.**

Material da sessão *Agentes de IA na saúde* (NOVA IMS, 2 h, online). Usa só
**dados abertos** (Portal da Transparência do SNS, normas da DGS) e **dados
inventados**. A ULS de Vale Fictício não existe. Nenhum dado real de utentes.
Não é aconselhamento clínico, e nada disto é um sistema do SNS ou da SPMS.

## O dia

| Hora | Momento | Competência | A peça que ensina | A armadilha |
|---|---|---|---|---|
| 08:00 | [A linha de informação](docs/competencias/01-onde-ir.md) | `/onde-ir` (construída ao vivo) | manual + ferramenta + um browser | fazer de médico; inventar tempos; páginas sem dados; erros nos dados do SNS |
| 09:30 | [A caixa de suporte](docs/competencias/02-triagem.md) | `/triagem` | receita + máscara de dados | *prompt injection* num email; dados pessoais |
| 09:45 | [O atacante](docs/competencias/02-triagem.md#0945--o-atacante-também-é-um-agente) | `/atacar` | um subagente *red team* | um ataque escrito à medida das nossas regras |
| 11:00 | [O conselho de administração](docs/competencias/03-relatorio.md) | `/relatorio` | código do agente + verificador | números sem origem; duas corridas, dois totais |
| 14:00 | [A saúde ocupacional](docs/competencias/04-norma.md) | `/norma` | pesquisa em documentos | resposta sem fonte; versão revogada |
| 16:00 | [O júri da plataforma de vacinação](docs/competencias/05-comparar.md) | `/comparar` | subagentes em paralelo | autonomia a mais: "adjudica" |
| 18:00 | [O fecho do dia](docs/competencias/06-rever-o-dia.md) | `/rever-o-dia` | o diário como prova; o agente propõe, uma pessoa decide | aplicar mudanças ao próprio manual |

Os momentos referem-se uns aos outros (o pedido 022 da caixa de suporte é a
pergunta das 14h; o fornecedor do pedido 021 é o da plataforma das 16h), mas
cada competência corre sozinha.

## Experimentar

Precisas do [Claude Code](https://docs.claude.com/en/docs/claude-code/overview),
do Python 3 e do [Node.js](https://nodejs.org) (só para o browser das 08:00, que
lê os tempos de espera em tempos.min-saude.pt). Sem `pip install`, sem chaves de API.

O browser é o servidor [Playwright MCP](https://github.com/microsoft/playwright-mcp),
configurado em `assistente/.mcp.json`, e **só consegue pedir** os domínios do site
dos tempos e do relatório Power BI que ele embebe (`--allowed-origins`). Na
primeira vez, o Claude Code pede para aprovar o servidor `browser`: aceita.

```bash
cd assistente
claude
```

Na primeira vez, o Claude Code pergunta se confias na pasta: **diz que sim**
(senão as permissões do agente são ignoradas e ele pede autorização para tudo).
Depois:

```
/onde-ir Odivelas, criança de 3 anos com febre desde ontem
/triagem
/relatorio
/norma Os administrativos da urgência têm vacina da gripe gratuita?
/comparar
```

## Ver o assistente a crescer

```bash
./demo/preparar.sh --ate 0      # ~/saude-ao-vivo/assistente: chega sem competências
./demo/preparar.sh --proxima    # 08:00 → /onde-ir; outra vez → 09:30 /triagem; …
./demo/preparar.sh --help
```

Cada `--proxima` instala uma competência (receita, ferramentas, dados) e mostra
as **permissões novas** e porquê. O que pertence a cada competência está em
[`demo/competencias.json`](demo/competencias.json); as marcas
`<!-- competencia:N -->` no `assistente/CLAUDE.md` dizem que linhas do manual
entram com cada uma.

## Estrutura

```
assistente/            o agente, com as cinco competências (o fim do dia)
  CLAUDE.md              o manual: quem é, o que sabe fazer, regras que não se negoceiam
  .claude/skills/        as receitas: onde-ir, triagem, relatorio, norma, comparar
  .claude/agents/        o subagente avaliador (16:00)
  .claude/settings.json  permissões: allow / ask / deny (gerado de demo/competencias.json)
  .claude/hooks/         o diário de bordo (saida/diario.md)
  .mcp.json              o browser (08:00), limitado ao site dos tempos de espera
  ferramentas/           as mãos, em Python só com biblioteca-padrão
  dados/<competência>/   dados abertos (com cache) ou inventados
  saida/<competência>/   tudo o que o agente escreve
comum/                 origem de pagina.py e diario.py
demo/                  preparar.sh + montar.py, competencias.json, etapas da construção ao vivo,
                       injeção, resultados dos ensaios (demo/0N/exemplo/, planos B)
docs/                  uma página por competência, e a checklist para levar um agente
                       para um serviço de saúde (também em PDF)
palestra/              slides.html (+ PDF), guiao.md minuto a minuto
```

## Fontes dos dados

- Portal da Transparência do SNS — <https://transparencia.sns.gov.pt>
  (caracterização das valências de urgência; atendimentos por triagem de
  Manchester; atendimentos por tipo de urgência; atividade do SNS 24).
- Direção-Geral da Saúde — normas 004/2026, 006/2026 e 007/2026, ver
  [`assistente/dados/norma/FONTES.md`](assistente/dados/norma/FONTES.md).
- Tempos de espera nas urgências: <https://tempos.min-saude.pt> (lidos com um
  browser no momento do pedido; não são dados abertos).
- Localização de concelhos: Open-Meteo Geocoding API.

Os dados foram descarregados a 23/11/2026. Antes de os usar, confirmar nas fontes.
