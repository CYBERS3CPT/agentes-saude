# Checklist — antes de pôr um agente num serviço de saúde

As sete perguntas da sessão, cada uma ligada ao caso em que se viu porque importa.
Não substitui o encarregado de proteção de dados nem a equipa de segurança: serve
para chegar à conversa com eles com o trabalho de casa feito.

## 1. Dados mínimos

- O agente precisa mesmo de dados pessoais? E de dados de saúde (categoria especial, art. 9.º do RGPD)?
- Se sim, quais, exatamente, e onde ficam depois?
- Há uma ferramenta que mascara antes de escrever, ou só uma regra no manual?

*Visto no caso 2:* a regra "não copies números de utente" funciona quase sempre.
O `mascarar.py --verificar` é o que garante.

## 2. Humano no ciclo

- Em que momento uma pessoa revê o trabalho, **antes** de alguma coisa sair?
- Que casos passam sempre a humano (conteúdo clínico, pedidos legais, segurança, dúvida)?
- A decisão final, se tiver efeitos sobre pessoas, é de uma pessoa? (art. 22.º do RGPD)

*Visto no caso 5:* "adjudica à melhor" tem de esbarrar numa permissão e numa regra.

## 3. Permissões mínimas

- O que pode fazer sozinho (`allow`), o que pergunta (`ask`), o que nunca (`deny`)?
- As regras estão escritas de forma a não deixar atalhos?

*Visto no caso 3:* uma regra mal escrita levou o agente a criar um `__main__.py`
para caber nela. Esforçado, e não era isso que se queria.

## 4. Registo

- Conseguimos reconstituir o que fez, com que dados e porquê, daqui a seis meses?
- O registo é escrito por um mecanismo que o agente não controla (um *hook*)?

## 5. Entradas hostis

- O que acontece quando um email, PDF, página ou proposta traz instruções escondidas?
- O que o agente lê é tratado como informação, nunca como ordens? E ele avisa?

*Visto nos casos 2 e 5:* texto branco num email, comentário HTML numa proposta.

## 6. Avaliação

- Há um conjunto de casos de teste (incluindo maliciosos e absurdos) que se corre
  sempre que muda o modelo, o manual ou as ferramentas?
- Há verificadores automáticos do resultado, como o `verificar.py` do caso 3?

## 7. Onde corre

- Que modelo, de que fornecedor, em que região, com que contrato?
- Os dados enviados ao modelo são retidos? Usados para treino?
- Há alternativa (modelo alojado na UE, ou em infraestrutura própria) para os casos mais sensíveis?

## Enquadramento (confirmar sempre à data)

- **RGPD:** dados de saúde são categoria especial (art. 9.º); decisões
  exclusivamente automatizadas com efeitos significativos (art. 22.º).
- **AI Act:** sistemas de triagem de doentes em urgência e de avaliação do
  acesso a serviços de saúde estão no Anexo III (alto risco). Com o Omnibus
  Digital (Reg. (UE) 2026/1744), as obrigações do Anexo III aplicam-se a partir
  de 2/12/2027 e as do Anexo I (ex.: dispositivos médicos) a partir de 2/8/2028.
  As obrigações de transparência do art. 50.º aplicam-se desde 2/8/2026, com
  transição até 2/12/2026 para alguns sistemas já no mercado.
