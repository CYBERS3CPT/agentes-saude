# Competência 01 — /onde-ir (08:00 — A linha de informação)

> Parte do **assistente da ULS de Vale Fictício** (`assistente/`). Para ter só esta
> competência e as anteriores: `./demo/preparar.sh --ate 1`. A receita está em
> `assistente/.claude/skills/onde-ir/SKILL.md`; dados em `assistente/dados/onde-ir/`,
> resultados em `assistente/saida/onde-ir/`.

Um agente que diz **a quem ligar, para onde ir e quanto se espera agora** quando
alguém precisa de uma urgência do SNS, a partir do concelho e da situação. Usa
dados abertos do Portal da Transparência do SNS para saber que urgências existem
e onde, e **abre num browser** o site tempos.min-saude.pt para ler os tempos de
espera, que só existem lá, num relatório Power BI feito para pessoas.

```bash
cd assistente
claude
```

```
/onde-ir Odivelas, criança de 3 anos com febre desde ontem
/onde-ir Mértola, grávida de 38 semanas
/onde-ir Funchal, adulto com dor de garganta
```

## O que esta competência ensina

| Peça | Onde está |
|---|---|
| Ferramenta (as mãos) | `ferramentas/urgencias.py`: dados abertos, distância em linha reta e o endereço da página de tempos de cada hospital |
| Browser (os olhos) | `.mcp.json`: Playwright MCP, que **só consegue pedir** o site dos tempos e o Power BI (`--allowed-origins`) |
| Instruções (o manual) | `CLAUDE.md` e a receita: não és médico, 112 primeiro, SNS 24 antes da urgência, tempos só lidos e com hora |
| Receita | `.claude/skills/onde-ir/SKILL.md` |
| Permissões | `navigate`, `snapshot`, `click`, `wait_for` sozinho; escrever em formulários pede autorização; correr JavaScript no browser, nunca |
| Registo | `saida/diario.md`: cada página aberta aparece como `🌐 Browser` |

## Para apontar durante a demo

- **O browser à vista.** Ao vivo, a janela abre-se: o público vê o agente a
  navegar no site do SNS, esperar pelo Power BI e ler. Leva cerca de 15 segundos
  por página; a corrida inteira, 1 a 2 minutos.
- **O site também tem defeitos.** Nos ensaios de 23/11/2026: a ULS Loures/Odivelas
  não publicava tempos de urgência e o Santa Maria mostrava "dados temporariamente
  indisponíveis por manutenção", com zeros. O agente tem de dizer isso, e não os zeros.
- **Sem manual** (etapa 1), no ensaio, **nem abriu o browser**: inventou "a espera
  pode ir de 1 a 4 horas", deu conselhos clínicos e indicou hospitais de memória.
- **O limite não está no modelo.** Pedir-lhe que vá a outro site (um jornal, uma
  pesquisa): o browser recusa, porque o domínio não está em `--allowed-origins`.
- **Dados reais têm defeitos.** No dataset, várias valências aparecem associadas a
  outra unidade (a obstetrícia de Faro aparece em Évora). A ferramenta assinala, não
  corrige. Com `Mértola, grávida` vê-se o aviso e a distância de 70 km.
- **Regiões autónomas**: Madeira e Açores têm serviços regionais fora deste dataset.
- **Dados pessoais**: escrever o nome e o número de utente no pedido. O agente
  deve ignorá-los e dizê-lo.

## Sem internet

`python3 ferramentas/urgencias.py Lisboa --offline`. A cópia local está em
`dados/onde-ir/cache/` (dataset + 80 concelhos já localizados + lista de páginas do
site dos tempos). Sem rede, o browser não lê nada: o agente diz que não conseguiu
ler e o resto da página faz-se na mesma.
