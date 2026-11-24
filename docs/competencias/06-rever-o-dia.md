# Competência 06 — /rever-o-dia (18:00 — O fecho do dia)

> Parte do **assistente da ULS de Vale Fictício** (`assistente/`). Para a ter:
> `./demo/preparar.sh --ate 6` (ou `--proxima` depois das 16:00). A receita está em
> `assistente/.claude/skills/rever-o-dia/SKILL.md`; resultados em `assistente/saida/dia/`.

Ao fim do dia, o agente lê o seu **diário de bordo** (`saida/diario.md`, escrito por um
*hook* que ele não controla) e os resultados de cada competência, e faz:

- **o painel do dia** (`saida/dia/painel.html`): a linha do dia com as horas reais,
  as tentativas de manipulação que encontrou, os números do dia contados no diário,
  o que fez bem e o que fez mal, com provas;
- **propostas para amanhã** (`saida/dia/propostas.md`): 3 a 5 alterações ao manual ou
  às receitas, cada uma com o problema, a prova, o texto exato que sai e que entra, e
  o risco. **Não aplica nenhuma** sem que lhe digam qual.

Não pode propor enfraquecer as regras de segurança, nem mexer nas permissões. Se lhe
pedirem para aplicar uma proposta, o Claude Code pede autorização para editar o manual
ou a receita: é suposto.

## O que aconteceu no ensaio (23/11/2026)

Com o diário de um dia inteiro (147 passos), encontrou um **defeito real do sistema**:
a receita da triagem mandava passar nomes de utentes ao `mascarar.py` com `--nomes`, e
o diário registava a linha de comando, com os nomes. Propôs mudar a receita; quando lhe
pedimos para aplicar, a edição esbarrou na autorização. Corrigimos no código: o *hook*
do diário passou a omitir o que vem depois de `--nomes` e os números de 9 algarismos.
Tudo em `demo/06/exemplo/`.

## Para apontar durante a demo

- A pergunta "o que acontece se eu disser *aplica a proposta 1*?", antes de a dizer.
- O pedido de autorização que aparece: o agente propõe, uma pessoa decide.
- Ao vivo as propostas vão ser outras (o defeito do ensaio já foi corrigido).
