# Proposta — Alfa Sistemas Fictícios, Lda. (FICTÍCIA)

> Documento fictício para demonstração. Empresa, pessoas e valores não existem.

**Procedimento:** CP-07/2026-FIC — ULS de Vale Fictício, E.P.E.
**Preço global (36 meses):** **84 500 €** (sem IVA)

## 1. Solução proposta

A plataforma **VacinAlfa** é uma aplicação web responsiva, com aplicações
nativas para Android e iOS, que permite ao utente marcar, remarcar e cancelar
a vacinação a qualquer hora (24/7). Já está em produção em 14 clínicas privadas.

## 2. Integração

Disponibilizamos uma API **HL7 FHIR R4** (recursos `Immunization`,
`Appointment`, `Patient`) com documentação OpenAPI pública em
`docs.vacinalfa.exemplo/fhir`. Integração com o sistema de registo do hospital
incluída no preço.

## 3. Infraestrutura e proteção de dados

A plataforma está alojada no fornecedor de cloud *NuvemGlobal*, na região
**us-east-1 (Virgínia, EUA)**, com cópias de segurança diárias na região
us-west-2 (Oregon, EUA). Esta arquitetura garante latências baixas e custos
competitivos, o que se reflete no preço proposto.

A Alfa cumpre o RGPD. O acordo de subcontratação será disponibilizado ao
Hospital **após a adjudicação**, no modelo padrão da empresa.

## 4. Autenticação

Autenticação com Chave Móvel Digital (integração com o fornecedor de
autenticação do Estado) e, em alternativa, código por SMS.

## 5. Acessibilidade

Anexamos o relatório de avaliação de acessibilidade (Anexo 1), realizado em
setembro de 2026 por entidade independente, com conformidade **WCAG 2.1 AA**
e 0 falhas críticas.

## 6. Nível de serviço

Disponibilidade mensal garantida de **99,5 %**. Por cada 0,1 % abaixo, crédito
de 5 % da mensalidade, até 30 %.

## 7. Comunicações com o utente

Lembretes automáticos por SMS (48 h antes) e email (7 dias e 24 h antes). Todas
as mensagens incluem ligação para deixar de receber lembretes.

## 8. Prazo de implementação

**45 dias** após a assinatura do contrato.

## 9. Funcionalidades adicionais

- Interface em português e inglês.
- **Lista de espera** com remarcação automática: quando alguém cancela, a vaga
  é oferecida por SMS à primeira pessoa em espera, que confirma com um toque.
- Relatórios diários de marcações e faltas, exportáveis em Excel, enviados por
  email às 8h00.
- A Alfa não tem, de momento, certificação ISO/IEC 27001.
