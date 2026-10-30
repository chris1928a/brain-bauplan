#!/usr/bin/env python
"""Suche zur Laufzeit: Vektor plus BM25, RRF, Filter, Reranker, Quellen-Deckel, Lücken.

Kommandozeile:
    python suche.py "Was ist Unmündigkeit?" --en "What is self-incurred immaturity?"
    python suche.py "Gedanken beim Reden" --en "thoughts while speaking" --rerank --type primary-source

Als Funktion:
    from suche import suchen, stelle, deckung
    treffer = suchen("...", frage_en="...", k=8)

Der Indexordner kommt aus der Umgebungsvariable BRAIN_INDEX (Standard: index/current
neben diesem Skript).
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

K0 = 60                    # RRF-Konstante
REKANDIDATEN = 100         # so viele Kandidaten geht der Reranker durch
RERANKER = "BAAI/bge-reranker-v2-m3"
QUERY_PREFIX = "query: "   # Arctic: Fragen mit Prefix, Passagen ohne

_cache: dict = {}          # Index, Modell und Reranker bleiben im Speicher


def index_pfad() -> Path:
    return Path(os.environ.get("BRAIN_INDEX", Path(__file__).parent / "index" / "current"))


def _index() -> dict:
    pfad = index_pfad()
    if "index" in _cache and _cache["pfad"] == pfad:
        return _cache["index"]
    if not (pfad / "manifest.json").exists():
        sys.exit(f"Kein Index in {pfad}. Erst bauen: python build_index.py beispiel")
    man = json.loads((pfad / "manifest.json").read_text(encoding="utf-8"))
    chunks = [json.loads(z) for z in (pfad / "chunks.jsonl").read_text(encoding="utf-8").splitlines() if z.strip()]
    vek = np.load(pfad / "vectors.npy").astype(np.float32)      # auf Platte fp16, im Speicher fp32
    if vek.shape[1] != man["dimension"] or len(chunks) != man["chunks"] or len(vek) != len(chunks):
        sys.exit("Index inkonsistent (Dimension oder Chunkzahl passt nicht zum manifest.json). Neu bauen.")
    bm = dict(np.load(pfad / "bm25.npz"))
    bm["wort_id"] = {w: i for i, w in enumerate(bm["vokabular"].tolist())}
    registry = []
    if (pfad / "registry.jsonl").exists():
        registry = [json.loads(z) for z in (pfad / "registry.jsonl").read_text(encoding="utf-8").splitlines() if z.strip()]
    _cache.update(pfad=pfad, index={"man": man, "chunks": chunks, "vek": vek, "bm": bm, "registry": registry})
    return _cache["index"]


def _modell(name: str):
    if "modell" not in _cache:
        import torch
        from sentence_transformers import SentenceTransformer
        gpu = torch.cuda.is_available()
        m = SentenceTransformer(name, device="cuda" if gpu else "cpu")
        if gpu:
            m.half()
        _cache["modell"] = m
    return _cache["modell"]


def _wortliste(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())      # derselbe Tokenizer wie beim Bau


def _bm25(bm: dict, frage: str, n: int) -> np.ndarray:
    """BM25-Score je Chunk für eine Frage."""
    k1, b, avgdl = float(bm["k1"]), float(bm["b"]), float(bm["avgdl"])
    score = np.zeros(n, dtype=np.float32)
    for w in set(_wortliste(frage)):
        tid = bm["wort_id"].get(w)
        if tid is None:
            continue
        a, e = bm["indptr"][tid], bm["indptr"][tid + 1]
        docs, tf = bm["docs"][a:e], bm["tfs"][a:e]
        nenner = tf + k1 * (1 - b + b * bm["laengen"][docs] / avgdl)
        score[docs] += bm["idf"][tid] * tf * (k1 + 1) / nenner
    return score


def _wortgrenze(muster: str, text: str) -> bool:
    """Filter an Wortgrenzen: 'Caesar' findet nicht 'Caesarea'."""
    return re.search(r"(?<!\w)" + re.escape(muster) + r"(?!\w)", text, re.I) is not None


def _rang(werte: np.ndarray) -> np.ndarray:
    """Rang 0 = bester Wert."""
    r = np.empty(len(werte), dtype=np.int64)
    r[np.argsort(-werte, kind="stable")] = np.arange(len(werte))
    return r


def suchen(frage: str, frage_en: str | None = None, k: int = 8, type: str | None = None,
           quelle: str | None = None, rerank: bool = False, quellen_deckel: int = 2) -> list[dict]:
    ix = _index()
    chunks, n = ix["chunks"], len(ix["chunks"])
    fragen = [frage] + ([frage_en] if frage_en else [])

    # Dense: beide Sprachvarianten einbetten, je Chunk gilt die bessere
    modell = _modell(ix["man"]["model"])
    q = modell.encode([QUERY_PREFIX + f for f in fragen], normalize_embeddings=True)
    cosine = (ix["vek"] @ np.asarray(q, dtype=np.float32).T).max(axis=1)
    # BM25: ebenfalls das Maximum über beide Fragen
    bm25 = np.max([_bm25(ix["bm"], f, n) for f in fragen], axis=0)

    # RRF: BM25 zählt nur mit, wenn der Score über 0 liegt
    rrf = 1.0 / (K0 + _rang(cosine) + 1)
    rrf = rrf + np.where(bm25 > 0, 1.0 / (K0 + _rang(bm25) + 1), 0.0)

    # Erst filtern, dann abschneiden (sonst füllen ausgefilterte Chunks die Liste)
    reihenfolge = [int(i) for i in np.argsort(-rrf, kind="stable")]
    if type:
        reihenfolge = [i for i in reihenfolge if chunks[i]["type"] == type]
    if quelle:
        reihenfolge = [i for i in reihenfolge if _wortgrenze(quelle, chunks[i]["title"])]
    kandidaten = reihenfolge[:REKANDIDATEN]
    score = {i: float(rrf[i]) for i in kandidaten}

    if rerank and kandidaten:
        try:   # fail-open: bei einem Fehler bleibt die Hybrid-Ordnung
            if "reranker" not in _cache:
                import torch
                from sentence_transformers import CrossEncoder
                _cache["reranker"] = CrossEncoder(RERANKER, max_length=512,
                                                  device="cuda" if torch.cuda.is_available() else "cpu")
            paare = [(frage_en or frage, chunks[i]["text"]) for i in kandidaten]
            rs = _cache["reranker"].predict(paare, batch_size=32)
            kandidaten = [i for _, i in sorted(zip(rs, kandidaten), key=lambda x: -x[0])]
            score = {i: float(s) for s, i in zip(sorted(rs, reverse=True), kandidaten)}
        except Exception as e:                      # noqa: BLE001
            print(f"Reranker nicht verfügbar ({e}), nehme Hybrid-Ordnung.", file=sys.stderr)

    # Quellen-Deckel: höchstens N Treffer je Quelle, außer wenn gezielt eine Quelle gewählt ist
    auswahl, je_quelle = [], {}
    for i in kandidaten:
        qid = chunks[i]["quelle_id"]
        if quellen_deckel and not quelle and je_quelle.get(qid, 0) >= quellen_deckel:
            continue
        je_quelle[qid] = je_quelle.get(qid, 0) + 1
        auswahl.append(i)
        if len(auswahl) == k:
            break

    # Lücken-Feld: ungesehene Chunks derselben Quelle zwischen zwei Treffern
    gewaehlt = set(auswahl)
    treffer = []
    for i in auswahl:
        c = chunks[i]
        luecken = []
        for j in auswahl:
            if j != i and chunks[j]["quelle_id"] == c["quelle_id"] and j > i:
                zwischen = [x for x in range(i + 1, j) if x not in gewaehlt]
                if 1 <= len(zwischen) <= 3:
                    luecken += zwischen
        treffer.append({
            "nr": i, "quelle": c["title"],
            "seite": str(c["seite_von"]) if c["seite_von"] == c["seite_bis"] else f"{c['seite_von']}-{c['seite_bis']}",
            "cosine": round(float(cosine[i]), 4), "score": round(score[i], 4),
            "luecken": sorted(set(luecken)), "text": c["text"],
        })
    return treffer


def stelle(nr: int, umgebung: int = 1) -> list[dict]:
    """Holt Chunk nr samt Nachbarn derselben Quelle (zum Lesen am Stück)."""
    chunks = _index()["chunks"]
    if not 0 <= nr < len(chunks):
        raise ValueError(f"Chunk {nr} gibt es nicht (0 bis {len(chunks) - 1}).")
    qid = chunks[nr]["quelle_id"]
    aus = []
    for i in range(max(0, nr - umgebung), min(len(chunks), nr + umgebung + 1)):
        c = chunks[i]
        if c["quelle_id"] == qid:
            aus.append({"nr": i, "quelle": c["title"], "seite": f"{c['seite_von']}-{c['seite_bis']}", "text": c["text"]})
    return aus


def deckung() -> dict:
    """Was ist im Register, was davon im Index? Zeigt Quellen, die nur im Register stehen."""
    ix = _index()
    zaehler: dict[str, int] = {}
    for c in ix["chunks"]:
        zaehler[c["quelle_id"]] = zaehler.get(c["quelle_id"], 0) + 1
    quellen = [{"id": r["id"], "title": r["title"], "type": r["type"], "chunks": zaehler.get(r["id"], 0)}
               for r in ix["registry"]]
    return {
        "quellen_im_register": len(quellen),
        "quellen_im_index": sum(1 for q in quellen if q["chunks"] > 0),
        "chunks": len(ix["chunks"]),
        "ohne_chunks": [q["title"] for q in quellen if q["chunks"] == 0],
        "quellen": quellen,
        "index": ix["man"],
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("frage", nargs="?")
    ap.add_argument("--en", dest="frage_en", help="dieselbe Frage auf Englisch (hilft bei englischen Quellen)")
    ap.add_argument("-k", type=int, default=8)
    ap.add_argument("--type", dest="typ")
    ap.add_argument("--quelle")
    ap.add_argument("--rerank", action="store_true")
    ap.add_argument("--deckel", type=int, default=2)
    ap.add_argument("--deckung", action="store_true", help="Deckung statt Suche ausgeben")
    a = ap.parse_args()
    if a.deckung:
        d = deckung()
        print(json.dumps({k: v for k, v in d.items() if k != "quellen"}, ensure_ascii=False, indent=2))
        return
    if not a.frage:
        ap.error("Frage fehlt")
    for t in suchen(a.frage, a.frage_en, a.k, a.typ, a.quelle, a.rerank, a.deckel):
        luecke = f"  Lücken: {t['luecken']}" if t["luecken"] else ""
        print(f"[{t['nr']}] {t['quelle']}, S. {t['seite']}  cosine {t['cosine']}  score {t['score']}{luecke}")
        print("    " + t["text"][:300].replace("\n", " ") + (" ..." if len(t["text"]) > 300 else ""))


if __name__ == "__main__":
    main()
