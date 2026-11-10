#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Pacotes Anki (.apkg) para Estudo Médico Baseado em Evidências.
Suporta 4 arquiteturas cognitivas:
  1. atomic            -> Flashcard Atômico Puro (Estilo Woźniak / Matuschak)
  2. usmle_hybrid      -> Flashcard Híbrido USMLE Step 1 (Cloze + Campo Extra estilo AnKing/Zanki)
  3. clinical_vignette -> Flashcard Extenso de Mini-Vinheta Clínica (Estilo USMLE Step 2 CK / Yousmle)
  4. question_error    -> Transformação de Erro de Questão (Caderno de Erros c/ Análise de Distrator)
  5. image_occlusion   -> Oclusão de Imagem pré-desenhada (uma área coberta por card)
Todos aceitam imagem e áudio opcionais (image_front/back, audio_front/back).
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

try:
    import genanki
except ImportError:
    print("Instalando dependência 'genanki'...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "genanki", "--quiet"])
    import genanki


SHARED_CSS = """
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 18px;
    line-height: 1.55;
    color: #1e293b;
    background-color: #f8fafc;
    text-align: left;
    max-width: 780px;
    margin: 20px auto;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.nightMode.card, .night_mode .card {
    color: #e2e8f0;
    background-color: #1e293b;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.35);
}

.badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 4px 10px;
    border-radius: 999px;
    margin-bottom: 14px;
}

.badge-atomic {
    background-color: #dbeafe;
    color: #1d4ed8;
}
.nightMode .badge-atomic, .night_mode .badge-atomic {
    background-color: #1e3a8a;
    color: #93c5fd;
}

.badge-hybrid {
    background-color: #ede9fe;
    color: #6d28d9;
}
.nightMode .badge-hybrid, .night_mode .badge-hybrid {
    background-color: #4c1d95;
    color: #c4b5fd;
}

.badge-vignette {
    background-color: #fef3c7;
    color: #b45309;
}
.nightMode .badge-vignette, .night_mode .badge-vignette {
    background-color: #78350f;
    color: #fcd34d;
}

.badge-error {
    background-color: #fee2e2;
    color: #b91c1c;
}
.nightMode .badge-error, .night_mode .badge-error {
    background-color: #7f1d1d;
    color: #fca5a5;
}

.prompt-text {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 12px;
}

.vignette-box {
    font-size: 17px;
    background-color: #ffffff;
    border-left: 4px solid #f59e0b;
    padding: 14px 18px;
    border-radius: 6px;
    margin-bottom: 14px;
}
.nightMode .vignette-box, .night_mode .vignette-box {
    background-color: #0f172a;
    border-left-color: #fbbf24;
}

.answer-box {
    font-size: 20px;
    font-weight: 700;
    color: #047857;
    background-color: #ecfdf5;
    border-left: 4px solid #10b981;
    padding: 12px 16px;
    border-radius: 6px;
    margin-top: 12px;
    margin-bottom: 14px;
}
.nightMode .answer-box, .night_mode .answer-box {
    color: #6ee7b7;
    background-color: #064e3b;
    border-left-color: #34d399;
}

.extra-box {
    font-size: 15px;
    background-color: #f1f5f9;
    border-left: 4px solid #64748b;
    padding: 12px 16px;
    border-radius: 6px;
    margin-top: 14px;
}
.nightMode .extra-box, .night_mode .extra-box {
    background-color: #0f172a;
    border-left-color: #94a3b8;
}

.distractor-box {
    font-size: 15px;
    background-color: #fff1f2;
    border-left: 4px solid #f43f5e;
    padding: 12px 16px;
    border-radius: 6px;
    margin-top: 12px;
}
.nightMode .distractor-box, .night_mode .distractor-box {
    background-color: #311018;
    border-left-color: #fb7185;
}

.objective-box {
    font-size: 15px;
    background-color: #eff6ff;
    border-left: 4px solid #3b82f6;
    padding: 12px 16px;
    border-radius: 6px;
    margin-top: 12px;
}
.nightMode .objective-box, .night_mode .objective-box {
    background-color: #172554;
    border-left-color: #60a5fa;
}

.section-label {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    opacity: 0.75;
    margin-bottom: 4px;
}

.cloze {
    font-weight: 700;
    color: #2563eb;
}
.nightMode .cloze, .night_mode .cloze {
    color: #60a5fa;
}

.source-line {
    font-size: 12px;
    opacity: 0.65;
    margin-top: 10px;
}

hr#answer {
    border: none;
    border-top: 1px solid #cbd5e1;
    margin: 16px 0;
}
.nightMode hr#answer, .night_mode hr#answer {
    border-top-color: #334155;
}
"""


def stable_id(name: str) -> int:
    """Gera um ID numérico determinístico de 31 bits para Deck ou Model no Anki."""
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()
    return (int(digest[:8], 16) & 0x3FFFFFFF) + 1000000000


# Rodapé de fonte + ano da diretriz, comum a todos os modelos (aparece só no verso).
SOURCE_FOOTER = (
    '{{#Source}}<div class="source-line">📚 Fonte: {{Source}}'
    '{{#Year}} ({{Year}}){{/Year}}</div>{{/Source}}'
)

# v2: modelos ganharam os campos Source e Year (e o atômico, o sentido inverso).
# IDs novos evitam conflito com os Note Types v1 já importados no Anki.

# 1. Modelo Atômico Puro (Woźniak / Matuschak)
ATOMIC_MODEL = genanki.Model(
    model_id=stable_id("Antigravity_Med_Atomic_v2"),
    name="Medicina - 1. Atômico Puro (Woźniak/Matuschak) v2",
    fields=[
        {"name": "Front"},
        {"name": "Back"},
        {"name": "Extra"},
        {"name": "Source"},
        {"name": "Year"},
        {"name": "ReverseFront"},
        {"name": "ReverseBack"},
    ],
    templates=[
        {
            "name": "Card Atômico",
            "qfmt": (
                '<div class="badge badge-atomic">Residência • Card Atômico</div>'
                '<div class="prompt-text">{{Front}}</div>'
            ),
            "afmt": (
                '{{FrontSide}}<hr id="answer">'
                '<div class="answer-box">{{Back}}</div>'
                '{{#Extra}}<div class="extra-box">'
                '<div class="section-label">Nota Conceitual / Mecanismo</div>'
                '{{Extra}}</div>{{/Extra}}'
                + SOURCE_FOOTER
            ),
        },
        {
            # Segundo sentido opcional: só gera card quando ReverseFront está preenchido.
            "name": "Card Atômico (Sentido Inverso)",
            "qfmt": (
                '{{#ReverseFront}}'
                '<div class="badge badge-atomic">Residência • Card Atômico (Inverso)</div>'
                '<div class="prompt-text">{{ReverseFront}}</div>'
                '{{/ReverseFront}}'
            ),
            "afmt": (
                '{{FrontSide}}<hr id="answer">'
                '<div class="answer-box">{{ReverseBack}}</div>'
                '{{#Extra}}<div class="extra-box">'
                '<div class="section-label">Nota Conceitual / Mecanismo</div>'
                '{{Extra}}</div>{{/Extra}}'
                + SOURCE_FOOTER
            ),
        },
    ],
    css=SHARED_CSS,
)

# 2. Modelo Híbrido USMLE Step 1 (Estilo AnKing / Zanki - Cloze Nativo)
USMLE_HYBRID_MODEL = genanki.Model(
    model_id=stable_id("Antigravity_Med_USMLE_Hybrid_Cloze_v2"),
    name="Medicina - 2. Híbrido USMLE Step 1 (AnKing Cloze + Extra) v2",
    fields=[
        {"name": "Text"},
        {"name": "Extra"},
        {"name": "Source"},
        {"name": "Year"},
    ],
    templates=[
        {
            "name": "Cloze Híbrido USMLE",
            "qfmt": (
                '<div class="badge badge-hybrid">Residência • Cloze</div>'
                '<div class="prompt-text">{{cloze:Text}}</div>'
            ),
            "afmt": (
                '<div class="badge badge-hybrid">Residência • Cloze</div>'
                '<div class="prompt-text">{{cloze:Text}}</div>'
                '<hr id="answer">'
                '{{#Extra}}<div class="extra-box">'
                '<div class="section-label">Extra • Fisiopatologia & Diagnóstico Diferencial (One-Stop-Shop)</div>'
                '{{Extra}}</div>{{/Extra}}'
                + SOURCE_FOOTER
            ),
        }
    ],
    css=SHARED_CSS,
    model_type=genanki.Model.CLOZE,
)

# 3. Modelo Extenso de Mini-Vinheta Clínica (Estilo USMLE Step 2 CK / Cheesy Dorian / Yousmle)
CLINICAL_VIGNETTE_MODEL = genanki.Model(
    model_id=stable_id("Antigravity_Med_Clinical_Vignette_v2"),
    name="Medicina - 3. Mini-Vinheta Clínica (USMLE Step 2 CK / Yousmle) v2",
    fields=[
        {"name": "Vignette"},
        {"name": "Question"},
        {"name": "Answer"},
        {"name": "Extra"},
        {"name": "Source"},
        {"name": "Year"},
    ],
    templates=[
        {
            "name": "Card de Vinheta Clínica",
            "qfmt": (
                '<div class="badge badge-vignette">Residência • Vinheta Clínica</div>'
                '<div class="vignette-box">{{Vignette}}</div>'
                '<div class="prompt-text">{{Question}}</div>'
            ),
            "afmt": (
                '{{FrontSide}}<hr id="answer">'
                '<div class="answer-box">{{Answer}}</div>'
                '{{#Extra}}<div class="extra-box">'
                '<div class="section-label">Discriminadores Clínicos & Algoritmo de Conduta</div>'
                '{{Extra}}</div>{{/Extra}}'
                + SOURCE_FOOTER
            ),
        }
    ],
    css=SHARED_CSS,
)

# 4. Modelo de Transformação de Erro de Questão (Caderno de Erros Inteligente)
QUESTION_ERROR_MODEL = genanki.Model(
    model_id=stable_id("Antigravity_Med_Question_Error_v2"),
    name="Medicina - 4. Caderno de Erros de Questão (Análise de Distrator) v2",
    fields=[
        {"name": "ErrorType"},
        {"name": "Prompt"},
        {"name": "Answer"},
        {"name": "WhyNotDistractor"},
        {"name": "EducationalObjective"},
        {"name": "Source"},
        {"name": "Year"},
    ],
    templates=[
        {
            "name": "Card de Erro de Questão",
            "qfmt": (
                '<div class="badge badge-error">Residência • Caderno de Erros • {{ErrorType}}</div>'
                '<div class="prompt-text">{{Prompt}}</div>'
            ),
            "afmt": (
                '{{FrontSide}}<hr id="answer">'
                '<div class="answer-box">{{Answer}}</div>'
                '{{#WhyNotDistractor}}<div class="distractor-box">'
                '<div class="section-label">⚠️ Análise do Distrator (Por que a outra opção estava errada?)</div>'
                '{{WhyNotDistractor}}</div>{{/WhyNotDistractor}}'
                '{{#EducationalObjective}}<div class="objective-box">'
                '<div class="section-label">🎯 Objetivo Educacional (Regra Geral de Prova)</div>'
                '{{EducationalObjective}}</div>{{/EducationalObjective}}'
                + SOURCE_FOOTER
            ),
        }
    ],
    css=SHARED_CSS,
)


import re

VALID_HTML_TAG_RE = re.compile(
    r"</?(?:b|i|u|br|ul|ol|li|div|span|p|strong|em|table|thead|tbody|tr|td|th|sup|sub|hr|code|pre)(?:\s+[^>]*)?>",
    re.IGNORECASE,
)


def sanitize_html_field(text: str) -> str:
    """Escapa símbolos matemáticos '<' e '>' soltos para não serem interpretados como tags HTML pelo Anki, preservando tags HTML válidas."""
    if not text:
        return ""
    placeholders = []

    def _save_tag(match):
        placeholders.append(match.group(0))
        return f"__HTML_TAG_{len(placeholders) - 1}__"

    temp = VALID_HTML_TAG_RE.sub(_save_tag, str(text))
    temp = temp.replace("<", "&lt;").replace(">", "&gt;")
    for idx, tag in enumerate(placeholders):
        temp = temp.replace(f"__HTML_TAG_{idx}__", tag)
    return temp


def sanitize_tags(tags_list):
    """Formata tags do Anki substituindo espaços por underscores."""
    if not tags_list:
        return []
    return [str(t).strip().replace(" ", "_") for t in tags_list if str(t).strip()]


CLOZE_INDEX_RE = re.compile(r"\{\{c(\d+)::")


def check_cloze_c1_only(text: str, idx: int) -> None:
    """Regra da skill: só {{c1::...}} (1 nota = 1 card). Recusa c2, c3 etc."""
    indices = CLOZE_INDEX_RE.findall(text)
    if not indices:
        raise ValueError(
            f"Card #{idx} do tipo 'usmle_hybrid' precisa conter ao menos uma marcação Cloze (ex.: {{{{c1::resposta}}}})."
        )
    outros = sorted({i for i in indices if i != "1"}, key=int)
    if outros:
        raise ValueError(
            f"Card #{idx} do tipo 'usmle_hybrid' usa c{', c'.join(outros)}. "
            "Use apenas {{c1::...}} (o mesmo índice para todos os trechos ocultos)."
        )


def _field(item: dict, key: str, default: str = "") -> str:
    return sanitize_html_field(item.get(key, default))


# ---------------------------------------------------------------------------
# Mídia: imagens, áudio e oclusão de imagem pré-desenhada
# ---------------------------------------------------------------------------

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
AUDIO_EXTS = {".mp3", ".ogg", ".wav", ".m4a", ".flac"}
MAX_IMAGE_SIDE = 1200  # px: leve para sincronizar com o celular
IMG_STYLE = "max-width:100%;height:auto;border-radius:6px;margin:10px 0;"


def _pil():
    try:
        from PIL import Image, ImageDraw, ImageOps
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Imagens precisam da biblioteca Pillow (pip install pillow).") from exc
    return Image, ImageDraw, ImageOps


class MediaCollector:
    """Copia/converte mídia para uma pasta temporária com nomes neutros (hash),
    para o nome do arquivo nunca entregar a resposta e não colidir no Anki."""

    def __init__(self, base_dir, work_dir):
        self.base_dir = Path(base_dir)
        self.work_dir = Path(work_dir)
        self.paths = []

    def resolve(self, rel, idx):
        p = Path(rel)
        if not p.is_absolute():
            p = self.base_dir / p
        if not p.is_file():
            raise ValueError(f"Card #{idx}: arquivo de mídia não encontrado: {p}")
        return p

    def _store(self, data: bytes, ext: str) -> str:
        name = f"med_{hashlib.sha1(data).hexdigest()[:16]}{ext}"
        out = self.work_dir / name
        if not out.exists():
            out.write_bytes(data)
            self.paths.append(str(out))
        return name

    def _store_image(self, img) -> str:
        import io
        Image, _, _ = _pil()
        img = img.copy()
        img.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            fundo = Image.new("RGB", img.size, "white")
            fundo.paste(img, mask=img.split()[-1])
            img = fundo
        else:
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=85, optimize=True)
        return self._store(buf.getvalue(), ".jpg")

    def open_image(self, rel, idx):
        Image, _, ImageOps = _pil()
        p = self.resolve(rel, idx)
        if p.suffix.lower() not in IMAGE_EXTS:
            raise ValueError(f"Card #{idx}: formato de imagem não suportado: {p.name}")
        return ImageOps.exif_transpose(Image.open(p))

    def image_tag(self, rel, idx) -> str:
        return self.image_tag_from_pil(self.open_image(rel, idx))

    def image_tag_from_pil(self, img) -> str:
        return f'<img src="{self._store_image(img)}" style="{IMG_STYLE}">'

    def sound_tag(self, rel, idx) -> str:
        p = self.resolve(rel, idx)
        ext = p.suffix.lower()
        if ext not in AUDIO_EXTS:
            raise ValueError(f"Card #{idx}: formato de áudio não suportado: {p.name}")
        return f"[sound:{self._store(p.read_bytes(), ext)}]"


def media_html(item, media, idx, side):
    """Monta o HTML de imagem/áudio de um lado do card ('front' ou 'back')."""
    parts = []
    for kind in ("image", "audio"):
        rel = item.get(f"{kind}_{side}")
        if not rel:
            continue
        if media is None:
            raise ValueError(f"Card #{idx}: mídia exige a pasta do JSON (use build_apkg).")
        parts.append(media.image_tag(rel, idx) if kind == "image" else media.sound_tag(rel, idx))
    if side == "back" and item.get("media_credit"):
        parts.append(
            '<div style="font-size:11px;opacity:0.6;">Crédito da mídia: '
            f"{sanitize_html_field(item['media_credit'])}</div>"
        )
    return "".join(parts)


def _join(text, extra_html, sep="<br>"):
    if not extra_html:
        return text
    return f"{text}{sep}{extra_html}" if text else extra_html


def _check_box(box, idx):
    if not (isinstance(box, (list, tuple)) and len(box) == 4):
        raise ValueError(f"Card #{idx}: 'box' deve ser [x, y, largura, altura] em frações de 0 a 1.")
    x, y, w, h = (float(v) for v in box)
    if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > 1.0001 or y + h > 1.0001:
        raise ValueError(f"Card #{idx}: 'box' {box} fora da imagem (use frações de 0 a 1).")
    return x, y, w, h


def _px(box, size):
    x, y, w, h = box
    W, H = size
    return [round(x * W), round(y * H), round((x + w) * W), round((y + h) * H)]


def draw_occlusion(img, boxes, target, mode, revealed):
    """Frente: alvo coberto (laranja); em 'hide_all' as outras áreas ficam cinza.
    Verso: alvo revelado com contorno vermelho."""
    _, ImageDraw, _ = _pil()
    out = img.convert("RGB").copy()
    d = ImageDraw.Draw(out)
    esp = max(3, out.size[0] // 250)
    for i, b in enumerate(boxes):
        r = _px(b, out.size)
        if i == target:
            if revealed:
                d.rectangle(r, outline="#dc2626", width=esp)
            else:
                d.rectangle(r, fill="#f59e0b", outline="#7c2d12", width=esp)
        elif mode == "hide_all":
            d.rectangle(r, fill="#94a3b8", outline="#334155", width=max(1, esp // 2))
    return out


def preview_occlusions(data, base_dir, out_dir):
    """Gera PNGs com todas as áreas numeradas, para conferir antes do .apkg."""
    _, ImageDraw, _ = _pil()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    media = MediaCollector(base_dir, out_dir)
    saidas = []
    for idx, item in enumerate(data.get("cards", []), start=1):
        if item.get("type") != "image_occlusion":
            continue
        img = media.open_image(item["image"], idx).convert("RGB")
        d = ImageDraw.Draw(img)
        esp = max(3, img.size[0] // 250)
        for n, occ in enumerate(item.get("occlusions", []), start=1):
            r = _px(_check_box(occ.get("box"), idx), img.size)
            d.rectangle(r, outline="#dc2626", width=esp)
            d.rectangle([r[0], r[1], r[0] + 28, r[1] + 22], fill="#dc2626")
            d.text((r[0] + 6, r[1] + 4), str(n), fill="white")
        p = out_dir / f"previa_card{idx}.png"
        img.save(p)
        saidas.append(str(p))
    return saidas


IMAGE_OCCLUSION_MODEL = genanki.Model(
    model_id=stable_id("Antigravity_Med_Image_Occlusion_v1"),
    name="Medicina - 5. Oclusão de Imagem (pré-desenhada) v1",
    fields=[
        {"name": "Header"},
        {"name": "ImageFront"},
        {"name": "ImageBack"},
        {"name": "Answer"},
        {"name": "Extra"},
        {"name": "Source"},
        {"name": "Year"},
    ],
    templates=[
        {
            "name": "Card de Oclusão",
            "qfmt": (
                '<div class="badge badge-occlusion">Residência • Oclusão de Imagem</div>'
                '{{#Header}}<div class="prompt-text">{{Header}}</div>{{/Header}}'
                "{{ImageFront}}"
            ),
            "afmt": (
                '<div class="badge badge-occlusion">Residência • Oclusão de Imagem</div>'
                '{{#Header}}<div class="prompt-text">{{Header}}</div>{{/Header}}'
                "{{ImageBack}}"
                '<div class="answer-box">{{Answer}}</div>'
                '{{#Extra}}<div class="extra-box">{{Extra}}</div>{{/Extra}}'
                + SOURCE_FOOTER
            ),
        }
    ],
    css=SHARED_CSS
    + """
.badge-occlusion { background-color: #ccfbf1; color: #0f766e; }
.nightMode .badge-occlusion, .night_mode .badge-occlusion { background-color: #134e4a; color: #5eead4; }
""",
)


def occlusion_notes(item, media, idx, source, year, tags):
    """Um card por área ocluída."""
    if media is None:
        raise ValueError(f"Card #{idx}: oclusão exige a pasta do JSON (use build_apkg).")
    occs = item.get("occlusions") or []
    if not occs:
        raise ValueError(f"Card #{idx} (image_occlusion): informe 'occlusions'.")
    mode = item.get("mode", "hide_one")
    if mode not in ("hide_one", "hide_all"):
        raise ValueError(f"Card #{idx}: 'mode' deve ser 'hide_one' ou 'hide_all'.")
    if not item.get("image"):
        raise ValueError(f"Card #{idx} (image_occlusion): informe 'image'.")
    img = media.open_image(item["image"], idx)
    boxes = [_check_box(o.get("box"), idx) for o in occs]
    header = _field(item, "header", "Qual estrutura está coberta?")
    credit = media_html({"media_credit": item.get("media_credit", "")}, media, idx, "back")
    img_id = hashlib.sha1(img.convert("RGB").tobytes()).hexdigest()[:16]
    notes = []
    for i, occ in enumerate(occs):
        answer = _field(occ, "answer")
        if not answer:
            raise ValueError(f"Card #{idx}: a área {i + 1} está sem 'answer'.")
        front = media.image_tag_from_pil(draw_occlusion(img, boxes, i, mode, revealed=False))
        back = media.image_tag_from_pil(draw_occlusion(img, boxes, i, mode, revealed=True))
        extra = _join(_field(occ, "extra") or _field(item, "extra"), credit, "")
        notes.append(
            genanki.Note(
                model=IMAGE_OCCLUSION_MODEL,
                fields=[header, front, back, answer, extra, source, year],
                tags=tags + ["Modelo::5_Oclusao_de_Imagem"],
                guid=genanki.guid_for("image_occlusion", img_id, answer, str(boxes[i])),
            )
        )
    return notes


def build_deck(data: dict, media: "MediaCollector | None" = None):
    """Monta o Deck a partir do dicionário JSON. Retorna (deck, counts).
    `media` é necessário quando algum card usa imagem, áudio ou oclusão."""
    deck_name = data.get("deck_name", "Medicina::Flashcards Baseados em Evidencias")
    cards_data = data.get("cards", [])

    deck = genanki.Deck(deck_id=stable_id(deck_name), name=deck_name)
    counts = {
        "atomic": 0,
        "usmle_hybrid": 0,
        "clinical_vignette": 0,
        "question_error": 0,
        "image_occlusion": 0,
    }

    for idx, item in enumerate(cards_data, start=1):
        card_type = item.get("type", "atomic").strip().lower()
        tags = sanitize_tags(item.get("tags", []))
        source = _field(item, "source").strip()
        year = sanitize_html_field(str(item.get("source_year", "") or ""))
        if not source:
            raise ValueError(
                f"Card #{idx} ({card_type}) está sem 'source'. Todo card precisa citar "
                "diretriz, artigo ou livro-texto (nunca o material da aula nem material de prova)."
            )

        if card_type == "image_occlusion":
            for note in occlusion_notes(item, media, idx, source, year, tags):
                deck.add_note(note)
                counts["image_occlusion"] += 1
            continue

        # Imagem/áudio opcionais: frente vai junto da pergunta; verso vai no Extra.
        mfront = media_html(item, media, idx, "front")
        mback = media_html(item, media, idx, "back")

        if card_type == "atomic":
            front = _field(item, "front")
            back = _field(item, "back")
            reverse_front = _field(item, "reverse_front")
            reverse_back = _field(item, "reverse_back")
            if bool(reverse_front) != bool(reverse_back):
                raise ValueError(
                    f"Card #{idx} do tipo 'atomic': 'reverse_front' e 'reverse_back' devem vir juntos."
                )
            note = genanki.Note(
                model=ATOMIC_MODEL,
                fields=[
                    _join(front, mfront),
                    back,
                    _join(_field(item, "extra"), mback),
                    source,
                    year,
                    reverse_front,
                    reverse_back,
                ],
                tags=tags + ["Modelo::1_Atomico"],
                guid=genanki.guid_for("atomic", front, back),
            )

        elif card_type == "usmle_hybrid":
            text = _field(item, "text")
            check_cloze_c1_only(text, idx)
            note = genanki.Note(
                model=USMLE_HYBRID_MODEL,
                fields=[_join(text, mfront), _join(_field(item, "extra"), mback), source, year],
                tags=tags + ["Modelo::2_USMLE_Hibrido_Cloze"],
                guid=genanki.guid_for("usmle_hybrid", text),
            )

        elif card_type == "clinical_vignette":
            vignette = _field(item, "vignette")
            question = _field(item, "question", "Qual o diagnóstico mais provável e a conduta imediata?")
            note = genanki.Note(
                model=CLINICAL_VIGNETTE_MODEL,
                fields=[
                    _join(vignette, mfront),
                    question,
                    _field(item, "answer"),
                    _join(_field(item, "extra"), mback),
                    source,
                    year,
                ],
                tags=tags + ["Modelo::3_Vinheta_Clinica_Step2CK"],
                guid=genanki.guid_for("clinical_vignette", vignette, question),
            )

        elif card_type == "question_error":
            prompt = _field(item, "prompt")
            answer = _field(item, "answer")
            note = genanki.Note(
                model=QUESTION_ERROR_MODEL,
                fields=[
                    _field(item, "error_type", "Análise de Erro de Questão"),
                    _join(prompt, mfront),
                    answer,
                    _field(item, "why_not_distractor"),
                    _join(_field(item, "educational_objective"), mback),
                    source,
                    year,
                ],
                tags=tags + ["Modelo::4_Erro_de_Questao"],
                guid=genanki.guid_for("question_error", prompt, answer),
            )

        else:
            raise ValueError(
                f"Tipo de card desconhecido no item #{idx}: '{card_type}'. Use 'atomic', "
                "'usmle_hybrid', 'clinical_vignette', 'question_error' ou 'image_occlusion'."
            )

        deck.add_note(note)
        counts[card_type] += 1

    return deck, counts


def build_apkg(input_json_path: str, output_apkg_path: str) -> dict:
    import tempfile

    input_path = Path(input_json_path).resolve()
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    out_path = Path(output_apkg_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        media = MediaCollector(input_path.parent, tmp)
        deck, counts = build_deck(data, media)
        package = genanki.Package(deck)
        package.media_files = media.paths
        package.write_to_file(str(out_path))

    return {
        "deck_name": deck.name,
        "output_file": str(out_path),
        "total_notes": sum(counts.values()),
        "total_cards": sum(len(n.cards) for n in deck.notes),
        "media_files": len(media.paths),
        "breakdown": counts,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Gera pacote .apkg do Anki com os modelos médicos baseados em evidências."
    )
    parser.add_argument("--input", "-i", required=True, help="Caminho para o arquivo JSON de entrada.")
    parser.add_argument("--output", "-o", help="Caminho para o arquivo .apkg de saída.")
    parser.add_argument(
        "--preview-occlusions",
        metavar="PASTA",
        help="Só gera PNGs com as áreas de oclusão numeradas (para conferir antes do .apkg).",
    )
    args = parser.parse_args()

    if args.preview_occlusions:
        input_path = Path(args.input).resolve()
        data = json.loads(input_path.read_text(encoding="utf-8"))
        saidas = preview_occlusions(data, input_path.parent, args.preview_occlusions)
        print(json.dumps({"previas": saidas}, ensure_ascii=False, indent=2))
        return
    if not args.output:
        parser.error("informe --output (ou use --preview-occlusions).")

    summary = build_apkg(args.input, args.output)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
