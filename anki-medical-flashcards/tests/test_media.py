# -*- coding: utf-8 -*-
"""Testes de imagem, áudio e oclusão de imagem."""

import json
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import generate_apkg as g  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.work = self.dir / "work"
        self.work.mkdir()
        Image.new("RGB", (2400, 1600), "white").save(self.dir / "rx_torax.png")
        (self.dir / "sopro.mp3").write_bytes(b"ID3fake-audio")
        self.media = g.MediaCollector(self.dir, self.work)

    def tearDown(self):
        self._tmp.cleanup()

    def build(self, *cards):
        for c in cards:
            c.setdefault("source", "Fonte de teste")
        return g.build_deck({"deck_name": "T", "cards": list(cards)}, self.media)


class TestImagemEAudio(Base):
    def test_imagem_na_frente_vira_img_com_nome_neutro(self):
        deck, _ = self.build({"type": "atomic", "front": "Qual o achado?", "back": "R", "image_front": "rx_torax.png"})
        front = deck.notes[0].fields[0]
        self.assertIn('<img src="med_', front)
        self.assertNotIn("rx_torax", front)  # nome do arquivo não entrega a resposta
        self.assertEqual(len(self.media.paths), 1)

    def test_imagem_e_reduzida_para_celular(self):
        self.build({"type": "atomic", "front": "P?", "back": "R", "image_front": "rx_torax.png"})
        with Image.open(self.media.paths[0]) as im:
            self.assertLessEqual(max(im.size), g.MAX_IMAGE_SIDE)

    def test_imagem_no_verso_vai_para_extra_com_credito(self):
        deck, _ = self.build({
            "type": "clinical_vignette", "vignette": "V", "question": "Q?", "answer": "A",
            "image_back": "rx_torax.png", "media_credit": "Wikimedia Commons, CC BY 4.0",
        })
        extra = deck.notes[0].fields[3]
        self.assertIn("<img", extra)
        self.assertIn("CC BY 4.0", extra)
        self.assertNotIn("<img", deck.notes[0].fields[0])

    def test_audio_vira_tag_sound(self):
        deck, _ = self.build({"type": "atomic", "front": "Qual o sopro?", "back": "R", "audio_front": "sopro.mp3"})
        self.assertRegex(deck.notes[0].fields[0], r"\[sound:med_[0-9a-f]+\.mp3\]")

    def test_arquivo_inexistente_e_recusado(self):
        with self.assertRaisesRegex(ValueError, "não encontrado"):
            self.build({"type": "atomic", "front": "P?", "back": "R", "image_front": "nao_existe.png"})

    def test_formato_errado_e_recusado(self):
        (self.dir / "x.txt").write_text("oi")
        with self.assertRaisesRegex(ValueError, "não suportado"):
            self.build({"type": "atomic", "front": "P?", "back": "R", "audio_front": "x.txt"})


class TestOclusao(Base):
    def card(self, **kw):
        c = {
            "type": "image_occlusion",
            "image": "rx_torax.png",
            "header": "Qual estrutura está coberta?",
            "occlusions": [
                {"answer": "Arco aórtico", "box": [0.4, 0.1, 0.2, 0.1]},
                {"answer": "Seio costofrênico direito", "box": [0.1, 0.8, 0.15, 0.1]},
            ],
        }
        c.update(kw)
        return c

    def test_um_card_por_area(self):
        deck, counts = self.build(self.card())
        self.assertEqual(counts["image_occlusion"], 2)
        self.assertEqual([n.fields[3] for n in deck.notes], ["Arco aórtico", "Seio costofrênico direito"])

    def test_frente_cobre_alvo_e_verso_revela(self):
        deck, _ = self.build(self.card())
        nomes = {Path(p).name: p for p in self.media.paths}
        f = deck.notes[0].fields[1].split('"')[1]
        b = deck.notes[0].fields[2].split('"')[1]
        self.assertNotEqual(f, b)
        with Image.open(nomes[f]) as im:  # centro da área 1, imagem reduzida a 1200x800
            self.assertNotEqual(im.convert("RGB").getpixel((600, 120)), (255, 255, 255))
        with Image.open(nomes[b]) as im:
            r, gg, bb = im.convert("RGB").getpixel((600, 120))
            self.assertGreater(min(r, gg, bb), 240)  # revelada: continua branca

    def test_hide_one_mostra_outras_areas_e_hide_all_esconde(self):
        def pixel_area2(mode):
            self.media = g.MediaCollector(self.dir, self.work)
            deck, _ = self.build(self.card(mode=mode))
            nomes = {Path(p).name: p for p in self.media.paths}
            f = deck.notes[0].fields[1].split('"')[1]
            with Image.open(nomes[f]) as im:
                return im.convert("RGB").getpixel((210, 680))
        self.assertGreater(min(pixel_area2("hide_one")), 240)
        self.assertLess(min(pixel_area2("hide_all")), 240)

    def test_box_fora_da_imagem_e_recusado(self):
        with self.assertRaisesRegex(ValueError, "fora da imagem"):
            self.build(self.card(occlusions=[{"answer": "X", "box": [0.9, 0.9, 0.3, 0.3]}]))

    def test_area_sem_resposta_e_recusada(self):
        with self.assertRaisesRegex(ValueError, "answer"):
            self.build(self.card(occlusions=[{"box": [0.1, 0.1, 0.1, 0.1]}]))

    def test_previa_numerada(self):
        saidas = g.preview_occlusions({"cards": [self.card()]}, self.dir, self.dir / "prev")
        self.assertEqual(len(saidas), 1)
        self.assertTrue(Path(saidas[0]).is_file())


class TestPacoteComMidia(Base):
    def test_apkg_contem_arquivos_de_midia(self):
        cards = [
            {"type": "atomic", "front": "P?", "back": "R", "image_front": "rx_torax.png", "source": "S"},
            {"type": "atomic", "front": "Som?", "back": "R2", "audio_front": "sopro.mp3", "source": "S"},
            {"type": "image_occlusion", "image": "rx_torax.png", "source": "S",
             "occlusions": [{"answer": "A", "box": [0.1, 0.1, 0.2, 0.2]}]},
        ]
        jp = self.dir / "cards.json"
        jp.write_text(json.dumps({"deck_name": "T", "cards": cards}), encoding="utf-8")
        out = self.dir / "deck.apkg"
        resumo = g.build_apkg(str(jp), str(out))
        self.assertEqual(resumo["media_files"], 4)  # 1 imagem + 1 áudio + frente/verso da oclusão
        with zipfile.ZipFile(out) as z:
            mapa = json.loads(z.read("media"))
            self.assertEqual(len(mapa), 4)
            for k in mapa:
                self.assertIn(k, z.namelist())
            z.extract("collection.anki2", self.dir)
        con = sqlite3.connect(self.dir / "collection.anki2")
        flds = " ".join(r[0] for r in con.execute("select flds from notes"))
        con.close()
        for nome in mapa.values():
            self.assertIn(nome, flds)


if __name__ == "__main__":
    unittest.main()
