"""Servidor local de voz para o Jarvis (ou qualquer app no Mac).

Carrega o modelo uma vez e responde com áudio WAV na sua voz. Imita a API de
texto-para-fala do ElevenLabs, então um app que hoje usa o ElevenLabs só precisa
trocar o endereço de https://api.elevenlabs.io por http://localhost:5005.

Rotas:
    GET  /                              -> status
    POST /falar                         -> {"texto": "...", "emocao": 0.5, "ritmo": 0.5, "idioma": "pt"}
    POST /v1/text-to-speech/<voz>       -> {"text": "..."}  (formato ElevenLabs)
    POST /v1/text-to-speech/<voz>/stream

Iniciar:  ./voz/servidor        (porta padrão 5005; use --porta para mudar)
"""

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import falar

TRAVA = threading.Lock()  # o modelo gera um áudio por vez
ESTADO = {"modelo": None, "padrao": {}}


class Handler(BaseHTTPRequestHandler):
    def _responder(self, codigo: int, corpo: bytes, tipo: str) -> None:
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(corpo)

    def _json(self, codigo: int, dados: dict) -> None:
        self._responder(codigo, json.dumps(dados, ensure_ascii=False).encode(), "application/json")

    def do_OPTIONS(self) -> None:  # permite chamadas de páginas web (CORS)
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path.rstrip("/") in ("", "/status"):
            self._json(200, {"ok": True, "voz": "pronta"})
        else:
            self._json(404, {"erro": "rota não encontrada"})

    def do_POST(self) -> None:
        caminho = self.path.split("?")[0].rstrip("/")
        eleven = caminho.startswith("/v1/text-to-speech/")
        if caminho != "/falar" and not eleven:
            return self._json(404, {"erro": "rota não encontrada"})
        try:
            tamanho = int(self.headers.get("Content-Length") or 0)
            dados = json.loads(self.rfile.read(tamanho) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._json(400, {"erro": "JSON inválido"})

        padrao = ESTADO["padrao"]
        if eleven:
            texto = dados.get("text", "")
            ajustes = dados.get("voice_settings") or {}
            emocao = float(ajustes.get("style", padrao["emocao"]) or padrao["emocao"])
            ritmo = padrao["ritmo"]
            idioma = dados.get("language_code") or padrao["idioma"]
        else:
            texto = dados.get("texto") or dados.get("text", "")
            emocao = float(dados.get("emocao", padrao["emocao"]))
            ritmo = float(dados.get("ritmo", padrao["ritmo"]))
            idioma = dados.get("idioma", padrao["idioma"])

        if not str(texto).strip():
            return self._json(400, {"erro": "texto vazio"})
        try:
            with TRAVA:
                modelo = ESTADO["modelo"]
                audio = falar.gerar(modelo, str(texto), idioma, emocao, ritmo, mostrar=False)
                wav = falar.para_wav(audio, modelo.sr)
        except Exception as e:  # devolve o erro ao app em vez de derrubar o servidor
            return self._json(500, {"erro": str(e)})
        self._responder(200, wav, "audio/wav")

    def log_message(self, formato, *args) -> None:
        print("[servidor]", formato % args)


def main() -> None:
    p = argparse.ArgumentParser(description="Servidor local da sua voz.")
    p.add_argument("--porta", type=int, default=5005)
    p.add_argument("-v", "--voz", default=str(falar.VOZ_PADRAO))
    p.add_argument("-l", "--idioma", default="pt")
    p.add_argument("--emocao", type=float, default=0.5)
    p.add_argument("--ritmo", type=float, default=0.5)
    args = p.parse_args()

    if not Path(args.voz).exists():
        raise SystemExit(f"Não achei a gravação da sua voz em {args.voz}.")

    ESTADO["padrao"] = {"idioma": args.idioma, "emocao": args.emocao, "ritmo": args.ritmo}
    ESTADO["modelo"] = falar.carregar_modelo(args.voz, args.emocao)

    # Só aceita conexões do próprio Mac.
    servidor = ThreadingHTTPServer(("127.0.0.1", args.porta), Handler)
    print(f"Voz pronta em http://localhost:{args.porta}  (Ctrl+C para parar)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
