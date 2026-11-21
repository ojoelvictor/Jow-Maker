# Área do Cliente: como usar

Página onde seus clientes entram com um **código de acesso** para ver e baixar as fotos e os vídeos do trabalho deles.

- Endereço da página: `seusite.com/area-do-cliente/`
- Link direto para o cliente (ele já entra sem digitar nada): `seusite.com/area-do-cliente/?c=CODIGO`
- Galeria de exemplo: código **`demo`**

---

## Como entregar um trabalho novo (passo a passo)

### 1. Suba os arquivos no Google Drive
1. Crie uma pasta para o cliente (ex.: `Ana e Pedro - Casamento`).
2. Coloque dentro dela as fotos e os vídeos finais.
3. Clique com o botão direito na pasta → **Compartilhar** → em "Acesso geral" escolha **"Qualquer pessoa com o link"** (como Leitor).
   Os arquivos que estão dentro da pasta passam a ter o mesmo acesso.

### 2. Copie os links
- **Link da pasta**: botão direito na pasta → *Compartilhar* → *Copiar link*. Esse link vira o botão **"Baixar tudo"** (o Drive entrega um .zip com tudo).
- **Link de cada arquivo**: botão direito no arquivo → *Compartilhar* → *Copiar link*.
  Para copiar vários de uma vez: selecione os arquivos, clique com o botão direito → *Compartilhar* → *Copiar links*.

### 3. Crie o arquivo da galeria
1. Na pasta `area-do-cliente/galerias/`, faça uma cópia de `_modelo.json`.
2. Dê ao arquivo o nome do **código de acesso** do cliente, por exemplo `ana-pedro-7x9k.json`.
   - Use só letras minúsculas, números e hífen.
   - Coloque alguns caracteres aleatórios no final (`-7x9k`) para ninguém adivinhar o código.
3. Preencha os campos:

```json
{
  "cliente": "Ana & Pedro",
  "evento": "Casamento",
  "data": "2026-10-12",
  "local": "Volta Redonda, RJ",
  "mensagem": "Foi uma honra registrar esse dia!",
  "capa": "LINK DA FOTO DE CAPA NO DRIVE",
  "baixarTudo": "LINK DA PASTA NO DRIVE",
  "expira": "2027-01-12",
  "arquivos": [
    { "tipo": "foto",  "nome": "Foto 01", "link": "LINK DA FOTO" },
    { "tipo": "foto",  "nome": "Foto 02", "link": "LINK DA FOTO" },
    { "tipo": "video", "nome": "Filme do casamento", "link": "LINK DO VÍDEO" }
  ]
}
```

| Campo | O que é | Obrigatório? |
|---|---|---|
| `cliente` | Nome que aparece em destaque. A última palavra fica laranja e em itálico | Sim |
| `evento` | Texto pequeno acima do nome (Casamento, Ensaio, 15 anos…) | Não |
| `data` | Data no formato `AAAA-MM-DD` | Não |
| `local` | Cidade ou local do evento | Não |
| `mensagem` | Recado para o cliente | Não |
| `capa` | Foto de fundo do topo. Se ficar vazio, usa a primeira foto | Não |
| `baixarTudo` | Link da pasta do Drive para o botão "Baixar tudo" | Não (recomendado) |
| `expira` | A galeria sai do ar depois desta data (`AAAA-MM-DD`). Deixe `""` para nunca expirar | Não |
| `arquivos` | Lista das fotos e dos vídeos, na ordem em que vão aparecer | Sim |

Em cada arquivo:
- `tipo`: `"foto"` ou `"video"`
- `nome`: nome exibido (opcional)
- `link`: link do Google Drive, ou qualquer link direto de imagem ou `.mp4`
- `capa`: (só para vídeo, opcional) imagem de miniatura do vídeo

> ⚠️ Cuidado com as vírgulas: todo item da lista leva vírgula no final, **menos o último**.
> Para conferir se o arquivo está certo, cole o conteúdo em https://jsonlint.com.

### 4. Publique e envie para o cliente
Salve o arquivo no GitHub (commit). Depois, envie ao cliente:

> Oi, Ana! Suas fotos estão prontas 🎉
> Acesse: https://SEUSITE/area-do-cliente/?c=ana-pedro-7x9k

---

## Dúvidas comuns

**A miniatura aparece como "Prévia indisponível".**
O arquivo no Drive não está como "Qualquer pessoa com o link". Arrume o compartilhamento.

**O vídeo grande não abre direto no download.**
Para vídeos grandes, o Google Drive mostra uma tela avisando que "não foi possível verificar vírus". É só o cliente clicar em **"Fazer o download assim mesmo"**. Isso é normal.

**Como tirar uma galeria do ar?**
Apague o arquivo `.json` do cliente, ou coloque uma data passada no campo `expira`.

**Privacidade.**
O código funciona como uma senha de link, do mesmo jeito que um link do Drive. Quem tem o código vê a galeria. Se o repositório do GitHub for **público**, os arquivos `.json` também podem ser lidos lá. Para trabalhos sensíveis, deixe o repositório privado e publique o site pela Netlify ou pela Vercel, ou mande o link do Drive direto para o cliente.
