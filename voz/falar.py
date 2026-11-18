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


def carregar_modelo(voz: str, emocao: float = 0.5):
    """Carrega o Chatterbox e prepara a sua voz. Demora; faça uma vez só."""
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    dispositivo = escolher_dispositivo()
    print(f"Carregando o modelo ({dispositivo})...")
    modelo = ChatterboxMultilingualTTS.from_pretrained(device=dispositivo)
    modelo.prepare_conditionals(str(voz), exaggeration=emocao)
    return modelo


def gerar(modelo, texto: str, idioma: str = "pt", emocao: float = 0.5,
          ritmo: float = 0.5, mostrar: bool = True):
    """Fala o texto (de qualquer tamanho) e devolve um tensor [1, amostras]."""
    import torch

    trechos = dividir_texto(texto)
    if not trechos:
        raise ValueError("texto vazio")
    pausa = torch.zeros(1, int(modelo.sr * 0.25))
    partes = []
    for i, trecho in enumerate(trechos, 1):
        if mostrar:
            print(f"[{i}/{len(trechos)}] {trecho}")
        wav = modelo.generate(trecho, language_id=idioma,
                              exaggeration=emocao, cfg_weight=ritmo)
        partes += [wav.cpu(), pausa]
    return torch.cat(partes[:-1], dim=1)


def para_wav(audio, taxa: int) -> bytes:
    """Converte o tensor em bytes de um arquivo WAV 16-bit mono."""
    import io
    import wave

    import numpy as np

    amostras = (audio.squeeze(0).clamp(-1, 1).numpy() * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taxa)
        w.writeframes(amostras.tobytes())
    return buf.getvalue()


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

    modelo = carregar_modelo(voz, args.emocao)
    audio = gerar(modelo, texto, args.idioma, args.emocao, args.ritmo)

    if args.saida:
        saida = Path(args.saida)
    else:
        saida = PASTA / "saidas" / datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.wav")
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_bytes(para_wav(audio, modelo.sr))
    print(f"\nPronto: {saida}")


if __name__ == "__main__":
    main()
