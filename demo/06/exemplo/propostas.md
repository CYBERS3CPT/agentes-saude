# Propostas para amanhã — 23/11/2026

Cinco alterações ao manual e às receitas. Cada uma aponta para algo que
aconteceu hoje. **Nenhuma foi aplicada.**

---

## 1. Triagem: deixar de passar nomes com `--nomes`

**O problema.** Às 09:31:46 corri `python3 ferramentas/mascarar.py --nomes "…"`
com nomes de pessoas na linha de comando. O hook escreve cada comando no diário,
e por isso os nomes ficaram em `saida/diario.md` (linha 66): dados pessoais fora
de onde estavam, ao contrário da primeira regra do manual. A receita manda fazer
exatamente isto (passo 5). Além disso, os 22 rascunhos foram escritos
(09:30:42–09:31:42) antes de serem mascarados, por isso estiveram em `saida/` com
os nomes durante esse tempo.

**A alteração.** Ficheiro `.claude/skills/triagem/SKILL.md`, passo 5.

Sai:
```
   `python3 ferramentas/mascarar.py --verificar saida/triagem/`. Se houver nomes de
   utentes nos rascunhos, passa-os com `--nomes`. Só avanças com "Sem fugas."
```
Entra:
```
   `python3 ferramentas/mascarar.py --verificar saida/triagem/`. Só avanças com
   "Sem fugas." Os rascunhos já se escrevem sem nomes de utentes (iniciais, ou
   "a utente"). **Não uses `--nomes`**: a linha de comando fica escrita em
   `saida/diario.md`. Se encontrares um nome num rascunho, corrige-o à mão.
```

**O risco.** O `--verificar` procura NUS, NIF, telefones, emails e datas de
nascimento, mas não reconhece nomes. Sem o `--nomes`, um nome que me escape não é
apanhado pela ferramenta: depende de eu não o escrever e de quem revê. A
alternativa mais segura seria o `mascarar.py` ler os nomes de um ficheiro, mas isso
é uma alteração à ferramenta, que cabe à equipa. **Nota:** o diário de hoje já
tem os nomes; alguém da equipa deve decidir o que fazer com a linha 66 (eu não
edito o diário).

---

## 2. Manual: abrir sempre a página gerada

**O problema.** Gerei 5 páginas (08:01:05, 09:32:25, 11:02:41, 14:00:37,
16:01:10) e não abri nenhuma: não há nenhum `open` no diário. As receitas pedem-no
(`/onde-ir` passo 6, `/triagem` passo 7, `/comparar` passo 6), mas o manual só diz
como se faz a página. Quem estava a ver ficou sem ver o resultado.

**A alteração.** Ficheiro `CLAUDE.md`, secção "Como trabalhas", ponto 3.

Sai:
```
3. **Resultados** em `saida/<competência>/`. A página faz-se com
   `python3 ferramentas/pagina.py <ficheiro.json>` (formato: `--exemplo`). Se der
   erro, lês o erro, corriges o JSON e corres outra vez.
```
Entra:
```
3. **Resultados** em `saida/<competência>/`. A página faz-se com
   `python3 ferramentas/pagina.py <ficheiro.json>` (formato: `--exemplo`). Se der
   erro, lês o erro, corriges o JSON e corres outra vez. Depois **abres a página**
   com `open saida/<competência>/<ficheiro>.html` (no Linux, `xdg-open`): o
   caminho começa sempre por `saida/`, que é o que as permissões aceitam.
```

**O risco.** Baixo. No Windows (`start`) não há permissão prévia e o Claude Code
vai pedir autorização. Abre uma janela por competência, o que pode distrair numa
demonstração com várias seguidas.

---

## 3. Manual: procurar texto sem `grep` pelo Bash

**O problema.** Usei `grep` pelo Bash 5 vezes (14:00:08, 14:00:12, 14:00:16,
14:00:19, 16:00:35) para encontrar páginas nas normas e citações nas propostas.
O `grep` não está na lista `allow` do `settings.json`, por isso pode ter pedido
autorização a quem estava a ver (o diário não regista os pedidos, não sei quantas
vezes aconteceu). O manual já proíbe `cat`, `sed` e `python3 -c` para ler, mas
não fala em procurar.

**A alteração.** Ficheiro `CLAUDE.md`, nota "Comandos" no início de "Como trabalhas".

Sai:
```
> encadeado obriga a pedir autorização a quem está a ver. Para **ler** ficheiros,
> usa a leitura de ficheiros do Claude Code (está sempre autorizada), não `cat`,
> `sed` nem `python3 -c`.
```
Entra:
```
> encadeado obriga a pedir autorização a quem está a ver. Para **ler** ficheiros,
> usa a leitura de ficheiros do Claude Code (está sempre autorizada), não `cat`,
> `sed` nem `python3 -c`. Para **procurar** texto, usa `ferramentas/procurar.py`
> (normas) ou a pesquisa de ficheiros do Claude Code, não `grep` no Bash.
```

**O risco.** Se a pesquisa de ficheiros do Claude Code não estiver disponível, sobra
ler o ficheiro inteiro, o que gasta mais contexto (a norma de 08/10 é longa). Não
mexe nas permissões: essas ficam com a equipa.

---

## 4. `/onde-ir`: verificar a secção "No mapa"

**O problema.** A receita pede uma secção **"No mapa"** (passo 5), mas
`saida/onde-ir/lisboa.json` não a tem. A lista "Antes de entregar, confirma" não
fala no mapa, por isso a falha passou sem dar por ela.

**A alteração.** Ficheiro `.claude/skills/onde-ir/SKILL.md`, lista final.

Sai:
```
- [ ] Os avisos da ferramenta e da página estão na página.
```
Entra:
```
- [ ] Os avisos da ferramenta e da página estão na página.
- [ ] A página tem as secções do passo 5, incluindo "No mapa" (um ponto por
      urgência da lista, até 4, com as coordenadas da ferramenta).
```

**O risco.** Quase nenhum: a lista fica uma linha maior. Se a ferramenta não der
coordenadas para alguma unidade, o mapa fica incompleto, e isso tem de ir para
"O que não sei".

---

## 5. `/comparar`: conferir citações sem reler as propostas inteiras

**O problema.** Às 16:00:35 confirmei as citações com uma pesquisa, e logo a seguir
(16:00:37–16:00:38) li outra vez as três propostas inteiras, que os avaliadores já
tinham lido (16:00:04–16:00:06). O caderno de encargos foi lido 4 vezes no total
(3 pelos avaliadores e 1 por mim às 16:00:31). Gastou tempo e contexto sem mudar
nada no resultado.

**A alteração.** Ficheiro `.claude/skills/comparar/SKILL.md`, passo 3.

Sai:
```
   - escolhe 2 citações de estados `cumpre` e confirma que existem
     literalmente em `dados/comparar/propostas/<nome>.md`;
```
Entra:
```
   - escolhe 2 citações de estados `cumpre` e confirma que existem
     literalmente em `dados/comparar/propostas/<nome>.md`, com uma pesquisa no
     ficheiro. Só lês a proposta inteira se alguma citação não aparecer;
```

**O risco.** Fico a depender dos avaliadores para encontrar texto escondido numa
proposta: se um avaliador falhar uma nota escondida, a minha releitura deixava de
a apanhar. Hoje o avaliador da Beta encontrou-a, mas é uma rede de segurança a
menos. Se a equipa preferir manter a dupla leitura, esta proposta não se aplica.

---

## Observações (não são propostas)

- As horas do diário (08:00 no `/onde-ir`) não batem com a hora da leitura no browser
  ("lido às 23:17" na página de Lisboa). O painel usa as do diário.
- Há uma segunda resposta da norma (`resposta-gripe-profissionais-hospitais-militares`)
  que o diário não regista. Não sei quando nem como foi feita.
- O `/atacar` não correu hoje, por isso a triagem não foi testada contra um ataque novo.
