# -*- coding: utf-8 -*-
"""Testes das regras do gerador. Rodar: python -m unittest discover -s tests -v (na pasta da skill)."""

import json
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import generate_apkg as g  # noqa: E402


def deck_com(*cards):
    for c in cards:
        c.setdefault("source", "Fonte de teste")
    return {"deck_name": "Teste::Regras", "cards": list(cards)}


class TestFonteObrigatoria(unittest.TestCase):
    def test_card_sem_fonte_e_recusado(self):
        for tipo, campos in [
            ("atomic", {"front": "P?", "back": "R"}),
            ("usmle_hybrid", {"text": "{{c1::X}}"}),
            ("clinical_vignette", {"vignette": "V", "question": "Q?", "answer": "A"}),
            ("question_error", {"prompt": "P?", "answer": "A"}),
        ]:
            card = {"type": tipo, **campos}
            with self.subTest(tipo=tipo), self.assertRaisesRegex(ValueError, "source"):
                g.build_deck({"deck_name": "T", "cards": [card]})

    def test_exemplo_oficial_tem_fonte_em_todos(self):
        exemplo = json.loads((SKILL_DIR / "examples" / "exemplo_medicina_4_modelos.json").read_text(encoding="utf-8"))
        for c in exemplo["cards"]:
            self.assertTrue(c.get("source", "").strip(), c)

    def test_exemplo_sem_material_de_prova_na_fonte(self):
        proibidos = ["first aid", "pathoma", "uworld", "amboss", "usmle", "sketchy"]
        exemplo = (SKILL_DIR / "examples" / "exemplo_medicina_4_modelos.json").read_text(encoding="utf-8")
        for c in json.loads(exemplo)["cards"]:
            for p in proibidos:
                self.assertNotIn(p, c.get("source", "").lower(), c.get("source"))


class TestClozeSoC1(unittest.TestCase):
    def test_c1_repetido_gera_um_card(self):
        deck, _ = g.build_deck(deck_com({"type": "usmle_hybrid", "text": "{{c1::A}} e {{c1::B}}"}))
        self.assertEqual(len(deck.notes[0].cards), 1)

    def test_c2_e_recusado(self):
        with self.assertRaisesRegex(ValueError, "c2"):
            g.build_deck(deck_com({"type": "usmle_hybrid", "text": "{{c1::A}} e {{c2::B}}"}))

    def test_sem_cloze_e_recusado(self):
        with self.assertRaises(ValueError):
            g.build_deck(deck_com({"type": "usmle_hybrid", "text": "sem lacuna"}))


class TestFonteEAno(unittest.TestCase):
    def test_todos_os_modelos_tem_source_e_year(self):
        for model in (g.ATOMIC_MODEL, g.USMLE_HYBRID_MODEL, g.CLINICAL_VIGNETTE_MODEL, g.QUESTION_ERROR_MODEL):
            nomes = [f["name"] for f in model.fields]
            self.assertIn("Source", nomes, model.name)
            self.assertIn("Year", nomes, model.name)
            for t in model.templates:
                self.assertIn("{{Source}}", t["afmt"], model.name)
                self.assertIn("{{Year}}", t["afmt"], model.name)

    def test_fonte_e_ano_vao_para_os_campos(self):
        cards = [
            {"type": "atomic", "front": "P?", "back": "R"},
            {"type": "usmle_hybrid", "text": "{{c1::X}}"},
            {"type": "clinical_vignette", "vignette": "V", "question": "Q?", "answer": "A"},
            {"type": "question_error", "prompt": "P?", "answer": "A"},
        ]
        for c in cards:
            c.update({"source": "Diretriz AHA/ASA", "source_year": 2026})
        deck, _ = g.build_deck(deck_com(*cards))
        for note in deck.notes:
            nomes = [f["name"] for f in note.model.fields]
            self.assertEqual(note.fields[nomes.index("Source")], "Diretriz AHA/ASA")
            self.assertEqual(note.fields[nomes.index("Year")], "2026")


class TestSentidoInverso(unittest.TestCase):
    def test_sem_inverso_gera_um_card(self):
        deck, _ = g.build_deck(deck_com({"type": "atomic", "front": "P?", "back": "R"}))
        self.assertEqual(len(deck.notes[0].cards), 1)

    def test_com_inverso_gera_dois_cards(self):
        deck, _ = g.build_deck(deck_com({
            "type": "atomic", "front": "P?", "back": "R",
            "reverse_front": "R inversa?", "reverse_back": "P",
        }))
        self.assertEqual(len(deck.notes[0].cards), 2)

    def test_inverso_incompleto_e_recusado(self):
        with self.assertRaises(ValueError):
            g.build_deck(deck_com({"type": "atomic", "front": "P?", "back": "R", "reverse_front": "só um lado"}))


class TestPacoteFinal(unittest.TestCase):
    def test_exemplo_oficial_gera_apkg_valido(self):
        exemplo = SKILL_DIR / "examples" / "exemplo_medicina_4_modelos.json"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "deck.apkg"
            resumo = g.build_apkg(str(exemplo), str(out))
            with zipfile.ZipFile(out) as z:
                z.extract("collection.anki2", tmp)
            con = sqlite3.connect(Path(tmp) / "collection.anki2")
            n_cards = con.execute("select count(*) from cards").fetchone()[0]
            con.close()
        total_json = len(json.loads(exemplo.read_text(encoding="utf-8"))["cards"])
        self.assertEqual(resumo["total_notes"], total_json)
        self.assertEqual(n_cards, resumo["total_cards"])


if __name__ == "__main__":
    unittest.main()
