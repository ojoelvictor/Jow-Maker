#!/bin/bash
# Instala o clonador de voz (Chatterbox Multilingual) no Mac. Rode uma vez só.
set -e
cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
  echo "Instalando o uv (gerenciador de Python)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "Criando o ambiente Python 3.11..."
uv venv --python 3.11 .venv

echo "Instalando o Chatterbox (pode levar alguns minutos)..."
uv pip install --python .venv/bin/python chatterbox-tts==0.1.7

chmod +x falar servidor
echo
echo "Pronto! Agora grave sua voz em voz/minha_voz.wav e rode:"
echo "  ./voz/falar \"Olá, essa é a minha voz.\""
