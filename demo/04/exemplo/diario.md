# Diário de bordo do agente

Escrito por um hook depois de cada ferramenta. O agente não escolhe o que aqui fica.

```
23:01:14  🔧 Bash      python3 ferramentas/procurar.py --listar
23:01:16  🔧 Bash      python3 ferramentas/procurar.py "profissionais de saúde vacinação gratuita gripe"
23:01:17  🔧 Bash      python3 ferramentas/procurar.py "administrativos sem contacto direto com doentes serviços de urgência"
23:01:22  🔧 Bash      grep -n "=== página" dados/norma/gripe-006-2026-v08out.txt
23:01:24  📖 Lê        dados/norma/gripe-006-2026-v08out.txt
23:01:26  🔧 Bash      grep -n -A12 "contextos ocupacionais de risco" dados/norma/gripe-006-2026-v17set.txt
23:01:30  🔧 Bash      grep -n -B3 -A14 "^1[34]\. " dados/norma/gripe-006-2026-v08out.txt
23:01:33  🔧 Bash      grep -n "decorre entre" dados/norma/gripe-006-2026-v08out.txt
23:01:34  🔧 Bash      python3 ferramentas/pagina.py --exemplo
23:01:34  📖 Lê        dados/norma/normas.json
23:01:51  📝 Escreve   saida/norma/resposta-gripe-administrativos-sns.json
23:01:51  🔧 Bash      python3 ferramentas/pagina.py saida/norma/resposta-gripe-administrativos-sns.json --tema clinico
