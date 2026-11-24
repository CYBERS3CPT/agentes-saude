# Diário de bordo do agente

Escrito por um hook depois de cada ferramenta. O agente não escolhe o que aqui fica.

```
23:16:57  🔧 Bash      python3 ferramentas/urgencias.py "Lisboa" --tipo criancas --n 5
23:17:00  ⚙️  mcp__bro  {"url": "https://tempos.min-saude.pt/instituicao/249"}
23:17:16  ⚙️  mcp__bro  {"time": 15}
23:17:17  ⚙️  mcp__bro  {}
23:17:21  ⚙️  mcp__bro  {"url": "https://tempos.min-saude.pt/instituicao/237"}
23:17:36  ⚙️  mcp__bro  {"time": 15}
23:17:37  ⚙️  mcp__bro  {}
23:17:40  ⚙️  mcp__bro  {}
23:17:40  🔧 Bash      python3 ferramentas/pagina.py --exemplo
23:17:57  📝 Escreve   saida/onde-ir/lisboa.json
23:18:01  ✏️  Edita     saida/onde-ir/lisboa.json
23:18:02  🔧 Bash      python3 ferramentas/pagina.py saida/onde-ir/lisboa.json --tema clinico
