import base64
import html
import io
import logging
import re
from pathlib import Path
from uuid import uuid4

import bleach
from bleach.css_sanitizer import CSSSanitizer
from xhtml2pdf import pisa
from PIL import Image

from repositories.processos_repository import salvar_documento_editorial as persistir_documento_editorial


PASTA_PDFS = Path(__file__).resolve().parent.parent / "uploads" / "documentos_editoriais"
server_logger = logging.getLogger("uvicorn.error")
TAMANHO_MAXIMO_HTML = 10 * 1024 * 1024
TAGS_PERMITIDAS = {
    "p", "br", "strong", "b", "em", "i", "u", "s", "h1", "h2", "h3", "h4",
    "ul", "ol", "li", "blockquote", "pre", "code", "span", "div", "img", "hr"
}
css_sanitizer = CSSSanitizer(allowed_css_properties={
    "text-align", "color", "background-color", "font-size", "font-weight",
    "font-style", "text-decoration"
})


class ErroDocumentoEditorial(Exception):
    pass


def _atributo_permitido(tag, atributo, valor):
    if atributo == "style":
        return True
    if tag == "img" and atributo in {"alt", "width", "height"}:
        return True
    if tag == "img" and atributo == "src":
        imagem = re.fullmatch(r"data:image/(png|jpeg|gif|webp);base64,([A-Za-z0-9+/]+=*)", valor or "")
        if not imagem or len(valor) > 8 * 1024 * 1024:
            return False
        try:
            dados = base64.b64decode(imagem.group(2), validate=True)
        except (ValueError, base64.binascii.Error):
            return False
        mime = imagem.group(1)
        assinaturas = {
            "png": dados.startswith(b"\x89PNG\r\n\x1a\n"),
            "jpeg": dados.startswith(b"\xff\xd8\xff"),
            "gif": dados.startswith((b"GIF87a", b"GIF89a")),
            "webp": len(dados) >= 12 and dados[:4] == b"RIFF" and dados[8:12] == b"WEBP"
        }
        return assinaturas.get(mime, False)
    return False


def _sanitizar_html(conteudo):
    if len(conteudo.encode("utf-8")) > TAMANHO_MAXIMO_HTML:
        raise ErroDocumentoEditorial("O documento excede o limite de 10 MB.")
    limpo = bleach.clean(
        conteudo,
        tags=TAGS_PERMITIDAS,
        attributes=_atributo_permitido,
        protocols={"data"},
        strip=True,
        css_sanitizer=css_sanitizer
    )
    if not re.sub(r"<[^>]*>", "", limpo).strip() and "<img" not in limpo:
        raise ErroDocumentoEditorial("Escreva um conteúdo antes de salvar o documento.")
    return limpo


def _preparar_imagens_para_pdf(conteudo):
    def ajustar_largura(match):
        tag = match.group(0)
        src = re.search(r'\bsrc="data:image/(png|jpeg|gif|webp);base64,([A-Za-z0-9+/]+=*)"', tag, re.I)
        if not src:
            return tag
        dados = base64.b64decode(src.group(2))
        try:
            with Image.open(io.BytesIO(dados)) as imagem:
                largura, altura = imagem.size
        except Exception as exc:
            raise ErroDocumentoEditorial("Não foi possível ler uma das imagens. Insira-a novamente.") from exc
        if largura < 1 or altura < 1:
            raise ErroDocumentoEditorial("Uma das imagens está vazia ou inválida.")
        largura_pdf = min(largura, 500)
        altura_pdf = max(1, round(altura * largura_pdf / largura))
        tag = re.sub(r'\swidth="[^"]*"', "", tag, flags=re.I)
        tag = re.sub(r'\sheight="[^"]*"', "", tag, flags=re.I)
        return tag[:-1] + f' width="{largura_pdf}" height="{altura_pdf}">'

    preparado = re.sub(r"<img\b[^>]*>", ajustar_largura, conteudo, flags=re.I)
    return preparado


def salvar_documento_editorial(processo_id, documento_id, nome, conteudo, user_id):
    nome = nome.strip()
    if not nome or len(nome) > 200:
        raise ErroDocumentoEditorial("Informe um título de até 200 caracteres.")
    imagens_recebidas = len(re.findall(r"<img\b", conteudo, flags=re.I))
    conteudo = _sanitizar_html(conteudo)
    imagens_validas = len(re.findall(r'<img\b[^>]*\bsrc="data:image/(?:png|jpeg|gif|webp);base64,', conteudo, flags=re.I))
    if imagens_recebidas != imagens_validas:
        server_logger.warning(
            "Processo %s: imagens recebidas=%s, imagens válidas após sanitização=%s",
            processo_id, imagens_recebidas, imagens_validas
        )
        raise ErroDocumentoEditorial("Uma imagem não foi aceita. Use PNG, JPEG, GIF ou WebP e insira-a pelo botão do editor.")
    conteudo_pdf = _preparar_imagens_para_pdf(conteudo)
    fonte = (
        "<!doctype html><html><head><meta charset='utf-8'><style>"
        "@page { size: A4; margin: 2cm; } body { font-family: Helvetica, sans-serif; "
        "font-size: 11pt; line-height: 1.45; color: #172b3a; } h1 { color: #245f73; } "
        "img { max-width: 100%; height: auto; } blockquote { border-left: 3px solid #31859b; "
        "padding-left: 12px; color: #52666d; } </style></head><body>"
        f"<h1>{html.escape(nome)}</h1>{conteudo_pdf}</body></html>"
    )
    pdf = io.BytesIO()
    try:
        resultado = pisa.CreatePDF(fonte, dest=pdf, encoding="utf-8", raise_exception=True)
        if resultado.err:
            raise ErroDocumentoEditorial("Não foi possível converter o documento para PDF.")
    except ErroDocumentoEditorial:
        raise
    except Exception as exc:
        raise ErroDocumentoEditorial("Não foi possível gerar o PDF. Revise o texto e as imagens.") from exc
    bytes_pdf = pdf.getvalue()
    imagens_no_pdf = len(re.findall(rb"/Subtype\s*/Image", bytes_pdf))
    server_logger.info(
        "Processo %s: imagens recebidas=%s, imagens válidas=%s, referências de imagem no PDF=%s",
        processo_id, imagens_recebidas, imagens_validas, imagens_no_pdf
    )
    if imagens_validas and imagens_no_pdf < 1:
        raise ErroDocumentoEditorial("O PDF não contém a imagem. Tente inserir uma imagem PNG ou JPEG menor.")

    PASTA_PDFS.mkdir(parents=True, exist_ok=True)
    caminho_pdf = PASTA_PDFS / f"{uuid4().hex}.pdf"
    caminho_pdf.write_bytes(bytes_pdf)
    try:
        editorial_id, pdf_id, caminho_antigo = persistir_documento_editorial(
            user_id, processo_id, documento_id, nome, conteudo,
            str(caminho_pdf), len(bytes_pdf)
        )
        if caminho_antigo and Path(caminho_antigo) != caminho_pdf:
            try:
                antigo = Path(caminho_antigo)
                if antigo.parent.resolve() == PASTA_PDFS.resolve():
                    antigo.unlink(missing_ok=True)
            except OSError:
                pass
        return {"id": editorial_id, "pdf_id": pdf_id, "nome": nome,
                "imagens": imagens_validas, "imagens_no_pdf": imagens_no_pdf}
    except Exception:
        caminho_pdf.unlink(missing_ok=True)
        raise
