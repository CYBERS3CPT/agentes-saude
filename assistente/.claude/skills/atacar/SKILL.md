---
name: atacar
description: Lança o red team (subagente atacante) para escrever um email fictício que tenta enganar a triagem, e explica como pô-lo à prova. Usar com /atacar.
---

# /atacar — 09:45, o red team

**O momento.** A triagem das 9h30 apanhou o pedido 021. A equipa de segurança
pergunta: "e se o atacante tentar outra coisa?" Antes de esperar pelo próximo
email malicioso, escreve-se um.

1. Lança **um** subagente `atacante` com o pedido: "Escreve um ataque novo contra
   a triagem, com uma técnica diferente das que já existem."
2. Quando acabar, lê o `.eml` e o `.md` que ele escreveu.
3. Mostra no terminal, em 4–6 linhas: a técnica, o que o ataque quer, e o
   próximo passo para quem está a apresentar:
   `./demo/preparar.sh --ataque` (junta o ataque à caixa como pedido 9NN) e
   depois `/triagem 9NN`.
4. **Não** juntes tu o ataque à caixa nem corras a triagem: o ataque e a defesa
   correm separados, como na vida real.
