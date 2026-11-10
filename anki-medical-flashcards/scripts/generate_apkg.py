#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Pacotes Anki (.apkg) para Estudo Médico Baseado em Evidências.
Suporta 4 arquiteturas cognitivas:
  1. atomic            -> Flashcard Atômico Puro (Estilo Woźniak / Matuschak)
  2. usmle_hybrid      -> Flashcard Híbrido USMLE Step 1 (Cloze + Campo Extra estilo AnKing/Zanki)
  3. clinical_vignette -> Flashcard Extenso de Mini-Vinheta Clínica (Estilo USMLE Step 2 CK / Yousmle)
  4. question_error    -> Transformação de Erro de Questão (Caderno de Erros c/ Análise de Distrator)
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


def build_deck(data: dict):
    """Monta o Deck a partir do dicionário JSON. Retorna (deck, counts)."""
    deck_name = data.get("deck_name", "Medicina::Flashcards Baseados em Evidencias")
    cards_data = data.get("cards", [])

    deck = genanki.Deck(deck_id=stable_id(deck_name), name=deck_name)
    counts = {"atomic": 0, "usmle_hybrid": 0, "clinical_vignette": 0, "question_error": 0}

    for idx, item in enumerate(cards_data, start=1):
        card_type = item.get("type", "atomic").strip().lower()
        tags = sanitize_tags(item.get("tags", []))
        source = _field(item, "source")
        year = sanitize_html_field(str(item.get("source_year", "") or ""))

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
                fields=[front, back, _field(item, "extra"), source, year, reverse_front, reverse_back],
                tags=tags + ["Modelo::1_Atomico"],
                guid=genanki.guid_for("atomic", front, back),
            )

        elif card_type == "usmle_hybrid":
            text = _field(item, "text")
            check_cloze_c1_only(text, idx)
            note = genanki.Note(
                model=USMLE_HYBRID_MODEL,
                fields=[text, _field(item, "extra"), source, year],
                tags=tags + ["Modelo::2_USMLE_Hibrido_Cloze"],
                guid=genanki.guid_for("usmle_hybrid", text),
            )

        elif card_type == "clinical_vignette":
            vignette = _field(item, "vignette")
            question = _field(item, "question", "Qual o diagnóstico mais provável e a conduta imediata?")
            note = genanki.Note(
                model=CLINICAL_VIGNETTE_MODEL,
                fields=[vignette, question, _field(item, "answer"), _field(item, "extra"), source, year],
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
                    prompt,
                    answer,
                    _field(item, "why_not_distractor"),
                    _field(item, "educational_objective"),
                    source,
                    year,
                ],
                tags=tags + ["Modelo::4_Erro_de_Questao"],
                guid=genanki.guid_for("question_error", prompt, answer),
            )

        else:
            raise ValueError(
                f"Tipo de card desconhecido no item #{idx}: '{card_type}'. "
                "Use 'atomic', 'usmle_hybrid', 'clinical_vignette' ou 'question_error'."
            )

        deck.add_note(note)
        counts[card_type] += 1

    return deck, counts


def build_apkg(input_json_path: str, output_apkg_path: str) -> dict:
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    deck, counts = build_deck(data)

    out_path = Path(output_apkg_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    genanki.Package(deck).write_to_file(str(out_path))

    return {
        "deck_name": deck.name,
        "output_file": str(out_path),
        "total_notes": sum(counts.values()),
        "total_cards": sum(len(n.cards) for n in deck.notes),
        "breakdown": counts,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Gera pacote .apkg do Anki com as 4 arquiteturas médicas baseadas em evidências."
    )
    parser.add_argument("--input", "-i", required=True, help="Caminho para o arquivo JSON de entrada.")
    parser.add_argument("--output", "-o", required=True, help="Caminho para o arquivo .apkg de saída.")
    args = parser.parse_args()

    summary = build_apkg(args.input, args.output)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
