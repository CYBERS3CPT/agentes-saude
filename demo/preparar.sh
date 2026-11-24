#!/usr/bin/env bash
# preparar.sh — monta o assistente da ULS de Vale Fictício para a sessão.
# Tudo é feito pelo demo/montar.py; este ficheiro existe para o comando ser fácil de lembrar.
#
#   ./demo/preparar.sh                # ~/saude-ao-vivo/assistente com as 5 competências
#   ./demo/preparar.sh --etapa 1      # 08:00: começar a construção ao vivo (sem manual)
#   ./demo/preparar.sh --proxima      # instalar a competência seguinte e ver as permissões novas
#   ./demo/preparar.sh --ate 3        # saltar para depois das 11:00
#   ./demo/preparar.sh --injecao      # 09:30: juntar o pedido 021 à caixa
#   ./demo/preparar.sh --ataque       # 09:45: juntar à caixa o ataque escrito pelo red team (/atacar)
#   ./demo/preparar.sh --sem-regra | --com-regra
#   ./demo/preparar.sh --help         # todas as opções
exec python3 "$(cd "$(dirname "$0")" && pwd)/montar.py" "$@"
