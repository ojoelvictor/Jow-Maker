"""Gera fala com a sua voz clonada, de graça e no seu próprio Mac.

Usa o Chatterbox Multilingual (código aberto, licença MIT). Na primeira vez
ele baixa o modelo (~3 GB); depois funciona sem internet.

Exemplos:
    ./voz/falar "Olá, essa é a minha voz."
    ./voz/falar -a roteiro.txt -s narracao.wav
    ./voz/falar "Que notícia boa!" --emocao 0.8
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
VOZ_PADRAO = PASTA / "minha_voz.wav"
LIMITE_TRECHO = 250  # caracteres por trecho; o modelo gera no máximo ~40 s por vez


def dividir_texto(texto: str, limite: int = LIMITE_TRECHO) -> list[str]:
    """Quebra o texto em trechos curtos, cortando em fim de frase sempre que possível."""
    texto = re.sub(r"\s+", " ", texto).strip()
    frases = re.split(r"(?<=[.!?…;:])\s+", texto)
    trechos, atual = [], ""
    for frase in frases:
        # Frase longa demais sozinha: corta em vírgulas e, em último caso, em palavras.
        while len(frase) > limite:
            corte = frase.rfind(",", 0, limite)
            if corte < limite // 3:
                corte = frase.rfind(" ", 0, limite)
            if corte <= 0:
                corte = limite
            pedaco, frase = frase[: corte + 1].strip(), frase[corte + 1 :].strip()
            if atual:
                trechos.append(atual)
                atual = ""
            trechos.append(pedaco)
        if atual and len(atual) + 1 + len(frase) > limite:
            trechos.append(atual)
            atual = frase
        else:
            atual = f"{atual} {frase}".strip()
    if atual:
        trechos.append(atual)
    return [t for t in trechos if t]


def escolher_dispositivo() -> str:
    import torch

    if torch.backends.mps.is_available():
        return "mps"  # chip Apple (M1, M2, M3...)
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"  # Mac com Intel: funciona, só que mais devagar


def main() -> None:
    p = argparse.ArgumentParser(description="Fala qualquer texto com a sua voz clonada.")
    p.add_argument("texto", nargs="?", help="o texto a falar (ou use -a)")
    p.add_argument("-a", "--arquivo", help="ler o texto de um arquivo .txt")
    p.add_argument("-v", "--voz", default=str(VOZ_PADRAO),
                   help="gravação de referência da voz (padrão: voz/minha_voz.wav)")
    p.add_argument("-s", "--saida", help="arquivo .wav de saída (padrão: voz/saidas/<data>.wav)")
    p.add_argument("-l", "--idioma", default="pt", help="código do idioma (padrão: pt)")
    p.add_argument("--emocao", type=float, default=0.5,
                   help="expressividade de 0.25 (neutro) a 1.0 (bem expressivo); padrão 0.5")
    p.add_argument("--ritmo", type=float, default=0.5,
                   help="aderência ao ritmo da gravação, 0 a 1; abaixe para falar mais devagar")
    args = p.parse_args()

    if args.arquivo:
        texto = Path(args.arquivo).read_text(encoding="utf-8")
    elif args.texto:
        texto = args.texto
    else:
        p.error("passe um texto entre aspas ou um arquivo com -a")

    voz = Path(args.voz)
    if not voz.exists():
        sys.exit(f"Não achei a gravação da sua voz em {voz}.\n"
                 "Grave 10 a 30 segundos falando naturalmente e salve com esse nome.")

    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    import torch
    import torchaudio
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    dispositivo = escolher_dispositivo()
    print(f"Carregando o modelo ({dispositivo})...")
    modelo = ChatterboxMultilingualTTS.from_pretrained(device=dispositivo)
    modelo.prepare_conditionals(str(voz), exaggeration=args.emocao)

    trechos = dividir_texto(texto)
    pausa = torch.zeros(1, int(modelo.sr * 0.25))
    partes = []
    for i, trecho in enumerate(trechos, 1):
        print(f"[{i}/{len(trechos)}] {trecho}")
        wav = modelo.generate(trecho, language_id=args.idioma,
                              exaggeration=args.emocao, cfg_weight=args.ritmo)
        partes += [wav.cpu(), pausa]
    audio = torch.cat(partes[:-1], dim=1)

    if args.saida:
        saida = Path(args.saida)
    else:
        saida = PASTA / "saidas" / datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.wav")
    saida.parent.mkdir(parents=True, exist_ok=True)
    torchaudio.save(str(saida), audio, modelo.sr)
    print(f"\nPronto: {saida}")


if __name__ == "__main__":
    main()
