# Diário de bordo do agente

Escrito por um hook depois de cada ferramenta. O agente não escolhe o que aqui fica.

```
22:58:18  🔧 Bash      ls ferramentas dados/relatorio saida saida/relatorio
22:58:18  🔧 Bash      python3 ferramentas/pagina.py --exemplo
22:58:21  🔧 Bash      python3 ferramentas/dados_sns.py descarregar atendimentos-em-urgencia-triagem-manchester
22:58:22  🔧 Bash      python3 ferramentas/dados_sns.py descarregar atendimentos-por-tipo-de-urgencia-hospitalar-link
22:58:26  📖 Lê        ferramentas/verificar.py
22:58:36  📝 Escreve   saida/relatorio/analise/00_explorar.py
22:58:37  🔧 Bash      python3 saida/relatorio/analise/00_explorar.py
22:58:55  📝 Escreve   saida/relatorio/analise/comum.py
22:59:08  📝 Escreve   saida/relatorio/analise/01_totais.py
22:59:17  📝 Escreve   saida/relatorio/analise/02_cores.py
22:59:24  📝 Escreve   saida/relatorio/analise/03_regioes.py
22:59:30  📝 Escreve   saida/relatorio/analise/04_tipos.py
22:59:32  🔧 Bash      python3 saida/relatorio/analise/01_totais.py
22:59:33  🔧 Bash      python3 saida/relatorio/analise/02_cores.py
22:59:34  🔧 Bash      python3 saida/relatorio/analise/03_regioes.py
22:59:34  🔧 Bash      python3 saida/relatorio/analise/04_tipos.py
22:59:45  📝 Escreve   saida/relatorio/analise/05_controlo.py
22:59:47  🔧 Bash      python3 saida/relatorio/analise/05_controlo.py
23:00:07  ✏️  Edita     saida/relatorio/analise/01_totais.py
23:00:09  ✏️  Edita     saida/relatorio/analise/03_regioes.py
23:00:11  ✏️  Edita     saida/relatorio/analise/05_controlo.py
23:00:39  📝 Escreve   saida/relatorio/analise/06_relatorio.py
23:00:41  🔧 Bash      python3 saida/relatorio/analise/01_totais.py
23:00:42  🔧 Bash      python3 saida/relatorio/analise/03_regioes.py
23:00:42  🔧 Bash      python3 saida/relatorio/analise/05_controlo.py
23:00:44  🔧 Bash      python3 saida/relatorio/analise/06_relatorio.py
23:00:49  ✏️  Edita     saida/relatorio/analise/01_totais.py
23:00:50  ✏️  Edita     saida/relatorio/analise/06_relatorio.py
23:00:51  ✏️  Edita     saida/relatorio/analise/06_relatorio.py
23:00:54  ✏️  Edita     saida/relatorio/analise/06_relatorio.py
23:00:55  🔧 Bash      python3 saida/relatorio/analise/01_totais.py
23:00:56  🔧 Bash      python3 saida/relatorio/analise/06_relatorio.py
23:00:57  🔧 Bash      python3 ferramentas/verificar.py saida/relatorio/relatorio.json
23:00:59  🔧 Bash      python3 ferramentas/pagina.py saida/relatorio/relatorio.json
