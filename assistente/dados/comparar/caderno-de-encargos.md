# Caderno de encargos (FICTÍCIO)

> ⚠️ Documento **fictício**, criado para uma demonstração de agentes de IA.
> A entidade, o procedimento e os números não existem.

**Entidade adjudicante:** ULS de Vale Fictício, E.P.E.
**Procedimento:** Consulta prévia n.º CP-07/2026-FIC
**Objeto:** Aquisição de uma plataforma de marcação e gestão da vacinação sazonal
(gripe e COVID-19) para utentes e profissionais, incluindo implementação e
manutenção durante 36 meses.
**Preço base:** **120 000 €** (sem IVA), para os 36 meses.
**Prazo de entrega de propostas:** 15/12/2026.

## 1. Requisitos obrigatórios

O não cumprimento, ou a não demonstração, de **qualquer** requisito obrigatório
é fundamento de exclusão da proposta, a decidir pelo júri.
Cada requisito tem de ser **demonstrado** na proposta (descrição concreta,
documento anexo, certificado ou compromisso contratual). Afirmações genéricas
de cumprimento ("cumpre integralmente") não constituem demonstração.

| N.º | Requisito |
|---|---|
| R1 | Marcação de vacinação pelo utente, por web e dispositivo móvel, disponível 24 horas por dia. |
| R2 | Integração com o sistema de registo de vacinação do hospital através de interface normalizada **HL7 FHIR R4**, com documentação da API. |
| R3 | Alojamento de todos os dados pessoais, incluindo cópias de segurança, em centros de dados localizados na **União Europeia / EEE**. |
| R4 | **Acordo de subcontratação** nos termos do art.º 28.º do RGPD, assinado e entregue com a proposta. |
| R5 | Autenticação do utente com Chave Móvel Digital ou meio de autenticação forte equivalente. |
| R6 | Conformidade com as **WCAG 2.1 nível AA** (Decreto-Lei n.º 83/2018), demonstrada por relatório de avaliação. |
| R7 | Disponibilidade mensal **≥ 99,5 %**, com acordo de nível de serviço (SLA) e penalizações definidas. |
| R8 | Lembretes ao utente por SMS e email, com possibilidade de recusa (opt-out) em cada mensagem. |
| R9 | Implementação completa em **≤ 60 dias** após a assinatura do contrato. |

## 2. Requisitos valorizados

| N.º | Requisito | Pontos (máx.) |
|---|---|---|
| V1 | Interface em português, inglês e pelo menos uma terceira língua. | 10 |
| V2 | Lista de espera com remarcação automática quando há cancelamentos. | 30 |
| V3 | Painel de gestão com indicadores em tempo real (marcações, faltas, doses administradas). | 30 |
| V4 | Certificação **ISO/IEC 27001** válida do prestador, com âmbito que inclua o serviço proposto. | 30 |

Um requisito valorizado só pontua se estiver **demonstrado**. Demonstração
parcial: metade dos pontos, a decidir pelo júri.

## 3. Critério de adjudicação

Proposta economicamente mais vantajosa, na modalidade **melhor relação
qualidade-preço**:

- **Qualidade técnica — 60 %**: soma dos pontos dos requisitos valorizados (0–100).
- **Preço — 40 %**: `100 × (preço mais baixo entre as propostas admitidas) / (preço da proposta)`.

Pontuação final = 0,6 × Qualidade + 0,4 × Preço.

Propostas com **preço acima do preço base** são excluídas (Código dos
Contratos Públicos, art.º 70.º, n.º 2, alínea d)).

## 4. Júri

A análise, a exclusão de propostas, a ordenação e a proposta de adjudicação
cabem **exclusivamente ao júri** do procedimento. A decisão de adjudicação
cabe ao órgão competente da entidade adjudicante. Qualquer apoio técnico à
análise (incluindo ferramentas automáticas) é meramente instrumental.
