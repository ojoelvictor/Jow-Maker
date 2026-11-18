# Minha voz (grátis, no Mac)

Clona a sua voz e fala qualquer texto com ela, rodando no seu próprio MacBook.
Usa o [Chatterbox Multilingual](https://github.com/resemble-ai/chatterbox), que tem código aberto (licença MIT) e fala português.
Não tem mensalidade nem créditos, e depois de instalado funciona sem internet.

## 1. Instalar (uma vez só)

No Terminal, dentro da pasta do projeto:

```bash
./voz/instalar.sh
```

A instalação baixa o Python e as bibliotecas (alguns GB). Na primeira fala, o programa também baixa o modelo (~3 GB).

## 2. Gravar sua voz (uma vez só)

Grave de **10 a 30 segundos** falando naturalmente, num lugar silencioso e sem música de fundo.
Pode usar o app **Gravador** do Mac ou do iPhone. Depois converta para WAV com este comando:

```bash
afconvert -f WAVE -d LEI16 ~/Downloads/gravacao.m4a voz/minha_voz.wav
```

Esse arquivo é a sua voz salva: enquanto ele existir, a voz está disponível.
O `.gitignore` impede que ele vá para o GitHub. Faça um backup dele por conta própria.

## 3. Usar

```bash
./voz/falar "Olá, essa é a minha voz."              # salva em voz/saidas/
./voz/falar -a roteiro.txt -s narracao.wav         # texto longo de um arquivo
./voz/falar "Que notícia incrível!" --emocao 0.8   # mais expressivo
./voz/falar "Calma, vai dar tudo certo." --ritmo 0.3   # mais devagar
./voz/falar "Hello, this is my voice." -l en       # outros idiomas
```

Textos longos são divididos em frases automaticamente e juntados num áudio só.

## Dicas

- **Mac com chip Apple (M1, M2, M3...)**: usa a placa de vídeo do chip e fica rápido.
- **Mac com Intel**: também funciona, só que mais devagar.
- Se a voz sair pouco parecida, grave de novo com mais clareza. Uma referência de ~20 segundos costuma dar o melhor resultado.
- O áudio gerado leva uma marca d'água inaudível (padrão do Chatterbox) que identifica fala sintética.
- Use apenas a sua voz, ou a de alguém que autorizou.
