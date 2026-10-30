#!/usr/bin/env python
"""Baut den Index: Quellen lesen, in Chunks schneiden, einbetten, BM25 rechnen.

Aufruf:
    python build_index.py beispiel                      # Quellordner mit .txt und .pdf
    python build_index.py meine-buecher --ziel index    # Index landet in index/current

Ablauf (Details stehen in den Kapiteln):
  1. Je Datei eine Registerzeile (registry.jsonl).
  2. PDF-Text per PyMuPDF mit Seitenmarkern "--- PAGE n ---".
  3. Absatzweise Chunks bis 480 Token des Modell-Tokenizers, ohne Overlap.
  4. Optionaler Kontextsatz (kontexte.jsonl) wird vor den Text gestellt.
  5. Embedding (normalisiert) und BM25 (eigene Implementierung).
  6. Alles landet in einem Ordner build-<Zeitstempel>. Erst am Ende wird er in
     "current" umbenannt. In current wird nie direkt geschrieben.
Inkrementell: Chunks, deren Text unverändert ist, übernehmen ihren Vektor aus
dem bisherigen current (Schlüssel: sha256 des einzubettenden Textes).
"""
import argparse
import hashlib
import json
import math
import re
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

MODELL = "Snowflake/snowflake-arctic-embed-l-v2.0"
TOKEN_CAP = 480          # lässt Platz für Sonder-Token und Kontextsatz (Modellgrenze 512)
K1, B = 1.5, 0.75        # BM25-Parameter
SEITE = re.compile(r"^--- PAGE (\d+) ---[ \t]*$", re.M)
KOPFZEILE = re.compile(r"^(Titel|Autor|Jahr|Typ|Lizenz|Quelle|Hinweis):\s*(.*)$")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def wortliste(text: str) -> list[str]:
    """Tokenizer für BM25: Wörter, klein geschrieben, keine Stoppwörter, keine Stammformen."""
    return re.findall(r"\w+", text.lower())


# ---------------------------------------------------------------- Quellen lesen

def pdf_zu_text(pfad: Path) -> tuple[str, dict]:
    """Text je Seite mit Marker. Ohne Marker gäbe es später keine Seitenzahl im Treffer."""
    import pymupdf
    seiten = []
    with pymupdf.open(pfad) as doc:
        meta = {"titel": (doc.metadata or {}).get("title", ""),
                "autor": (doc.metadata or {}).get("author", "")}
        for nr, seite in enumerate(doc, start=1):
            t = seite.get_text()
            t = re.sub(r"-\n(?=[a-zäöüß])", "", t)   # Trennstriche am Zeilenende zusammenziehen
            seiten.append(f"--- PAGE {nr} ---\n{t}")
    return "\n\n".join(seiten), meta


def kopf_trennen(text: str) -> tuple[dict, str]:
    """Trennt einen Kopf aus Zeilen 'Titel: ...' vom Text. Rückgabe: (Felder, Rumpf)."""
    m = SEITE.search(text)
    if m:
        kopf, rumpf = text[: m.start()], text[m.start():]
    else:  # kein Marker: Kopf = führender Block aus Schlüssel-Zeilen, Rest ist Seite 1
        zeilen = text.split("\n")
        n = 0
        while n < len(zeilen) and KOPFZEILE.match(zeilen[n]):
            n += 1
        kopf, rumpf = "\n".join(zeilen[:n]), "--- PAGE 1 ---\n" + "\n".join(zeilen[n:])
    felder = {}
    for z in kopf.split("\n"):
        k = KOPFZEILE.match(z.strip())
        if k:
            felder[k.group(1).lower()] = k.group(2).strip()
    return felder, rumpf


def slug(s: str) -> str:
    s = s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def quellen_lesen(ordner: Path) -> list[tuple[dict, str]]:
    """Liest alle .txt und .pdf. Rückgabe: Liste aus (Registerzeile, Rumpftext mit Seitenmarkern)."""
    ergebnis = []
    for pfad in sorted(ordner.iterdir()):
        if pfad.suffix.lower() not in (".txt", ".pdf"):
            continue
        pdfmeta = {}
        if pfad.suffix.lower() == ".pdf":
            text, pdfmeta = pdf_zu_text(pfad)
        else:
            text = pfad.read_text(encoding="utf-8").replace("\r\n", "\n")
        felder, rumpf = kopf_trennen(text)
        titel = felder.get("titel") or pdfmeta.get("titel") or pfad.stem
        autor = felder.get("autor") or pdfmeta.get("autor") or "unbekannt"
        jahr = felder.get("jahr", "")
        zeile = {
            "id": slug(pfad.stem),
            # Zitierform: "Autor Jahr - Titel"
            "title": f"{autor} {jahr} - {titel}" if jahr else f"{autor} - {titel}",
            "author": autor,
            # type beschreibt die Rolle der Quelle, nicht das Dateiformat
            "type": felder.get("typ", "primary-source"),
            "lizenz": felder.get("lizenz", "unbekannt"),
            "provenienz": felder.get("quelle", "lokale Kopie"),
            "datei": pfad.name,
        }
        ergebnis.append((zeile, rumpf))
    return ergebnis


# ---------------------------------------------------------------- Chunking

def chunks_schneiden(rumpf: str, tok, cap: int = TOKEN_CAP) -> list[dict]:
    """Absatzweise packen bis cap Token. Kein Overlap. Seiten werden mitgeführt."""
    teile = SEITE.split(rumpf)           # ['', '1', text1, '2', text2, ...]
    absaetze = []
    for i in range(1, len(teile) - 1, 2):
        seite = int(teile[i])
        for p in re.split(r"\n\s*\n", teile[i + 1]):
            p = re.sub(r"[ \t]*\n[ \t]*", " ", p.strip())
            if p:
                absaetze.append((seite, p))

    def tokenzahl(t):
        return len(tok(t, add_special_tokens=False)["input_ids"])

    chunks, aktuell, n_akt = [], [], 0

    def abschliessen():
        nonlocal aktuell, n_akt
        if aktuell:
            chunks.append({"text": "\n\n".join(p for _, p in aktuell),
                           "seite_von": min(s for s, _ in aktuell),
                           "seite_bis": max(s for s, _ in aktuell)})
        aktuell, n_akt = [], 0

    for seite, p in absaetze:
        n = tokenzahl(p)
        if n > cap:                       # übergroßer Absatz: an der Zeichenposition des cap-ten Tokens schneiden
            abschliessen()
            rest = p
            while tokenzahl(rest) > cap:
                offs = tok(rest, add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"]
                schnitt = offs[cap - 1][1]
                chunks.append({"text": rest[:schnitt].strip(), "seite_von": seite, "seite_bis": seite})
                rest = rest[schnitt:].strip()
            if rest:
                aktuell, n_akt = [(seite, rest)], tokenzahl(rest)
            continue
        if n_akt + n > cap:
            abschliessen()
        aktuell.append((seite, p))
        n_akt += n
    abschliessen()
    return chunks


# ---------------------------------------------------------------- BM25

def bm25_bauen(texte: list[str]) -> dict:
    """Invertierter Index als flache Arrays (CSR über die Begriffe).

    IDF: log((n - df + 0.5) / (df + 0.5) + 1), k1 = 1,5, b = 0,75.
    """
    n = len(texte)
    vokabular: dict[str, int] = {}
    posting: dict[int, list[tuple[int, int]]] = {}
    laengen = np.zeros(n, dtype=np.float32)
    for d, t in enumerate(texte):
        woerter = wortliste(t)
        laengen[d] = len(woerter)
        for w, tf in Counter(woerter).items():
            tid = vokabular.setdefault(w, len(vokabular))
            posting.setdefault(tid, []).append((d, tf))
    v = len(vokabular)
    indptr = np.zeros(v + 1, dtype=np.int64)
    for tid in range(v):
        indptr[tid + 1] = indptr[tid] + len(posting[tid])
    docs = np.zeros(indptr[-1], dtype=np.int32)
    tfs = np.zeros(indptr[-1], dtype=np.float32)
    idf = np.zeros(v, dtype=np.float32)
    for tid in range(v):
        p = posting[tid]
        docs[indptr[tid]:indptr[tid + 1]] = [d for d, _ in p]
        tfs[indptr[tid]:indptr[tid + 1]] = [f for _, f in p]
        idf[tid] = math.log((n - len(p) + 0.5) / (len(p) + 0.5) + 1)
    worte = np.array(sorted(vokabular, key=vokabular.get))   # Position = Begriffs-ID
    return {"indptr": indptr, "docs": docs, "tfs": tfs, "idf": idf, "laengen": laengen,
            "avgdl": np.float32(laengen.mean() if n else 0), "vokabular": worte,
            "k1": np.float32(K1), "b": np.float32(B)}


# ---------------------------------------------------------------- Embedding

def modell_laden():
    import torch
    from sentence_transformers import SentenceTransformer
    gpu = torch.cuda.is_available()
    m = SentenceTransformer(MODELL, device="cuda" if gpu else "cpu")
    m.max_seq_length = 512
    if gpu:
        m.half()                          # fp16 auf der GPU, fp32 auf der CPU
    return m


def alten_index_laden(pfad: Path) -> dict[str, np.ndarray]:
    """Vektoren des bisherigen Index, Schlüssel = sha256 des eingebetteten Textes."""
    try:
        man = json.loads((pfad / "manifest.json").read_text(encoding="utf-8"))
        if man["model"] != MODELL:
            print("Modell hat gewechselt: kompletter Neuaufbau.")
            return {}
        vek = np.load(pfad / "vectors.npy")
        zeilen = [json.loads(z) for z in (pfad / "chunks.jsonl").read_text(encoding="utf-8").splitlines()]
        return {z["embed_hash"]: vek[i] for i, z in enumerate(zeilen)}
    except (OSError, KeyError, ValueError):
        return {}


# ---------------------------------------------------------------- Hauptprogramm

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("quellordner", type=Path)
    ap.add_argument("--ziel", type=Path, default=Path(__file__).parent / "index",
                    help="Ordner, in dem build-<Zeitstempel> und current liegen")
    ap.add_argument("--kontexte", type=Path, default=None,
                    help="kontexte.jsonl mit {hash, kontext}; Standard: <quellordner>/kontexte.jsonl")
    args = ap.parse_args()
    t0 = time.time()

    kontext_pfad = args.kontexte or args.quellordner / "kontexte.jsonl"
    kontexte = {}
    if kontext_pfad.exists():
        for z in kontext_pfad.read_text(encoding="utf-8").splitlines():
            if z.strip():
                j = json.loads(z)
                kontexte[j["hash"]] = j["kontext"]
        print(f"{len(kontexte)} Kontextsätze geladen.")

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODELL)
    tok.model_max_length = 10**9          # lange Absätze sollen keine Warnung auslösen

    quellen = quellen_lesen(args.quellordner)
    if not quellen:
        sys.exit(f"Keine .txt oder .pdf in {args.quellordner} gefunden.")

    register, chunk_zeilen = [], []
    for zeile, rumpf in quellen:
        register.append(zeile)
        vorher = len(chunk_zeilen)
        for pos, c in enumerate(chunks_schneiden(rumpf, tok)):
            ctx = kontexte.get(sha256(c["text"]), "")
            embed_text = f"{ctx}\n\n{c['text']}" if ctx else c["text"]
            chunk_zeilen.append({
                "quelle_id": zeile["id"], "title": zeile["title"], "author": zeile["author"],
                "type": zeile["type"], "position": pos,
                "seite_von": c["seite_von"], "seite_bis": c["seite_bis"],
                "text": c["text"], "kontext": ctx, "embed_hash": sha256(embed_text),
            })
        print(f"{zeile['id']}: {len(chunk_zeilen) - vorher} Chunks")

    # Inkrementell: vorhandene Vektoren wiederverwenden
    ziel = args.ziel
    ziel.mkdir(parents=True, exist_ok=True)
    alt = alten_index_laden(ziel / "current")
    neu_idx = [i for i, z in enumerate(chunk_zeilen) if z["embed_hash"] not in alt]
    print(f"{len(chunk_zeilen)} Chunks, davon {len(neu_idx)} neu einzubetten, "
          f"{len(chunk_zeilen) - len(neu_idx)} wiederverwendet.")

    vek = None
    if neu_idx:
        modell = modell_laden()
        texte = [(chunk_zeilen[i]["kontext"] + "\n\n" if chunk_zeilen[i]["kontext"] else "") + chunk_zeilen[i]["text"]
                 for i in neu_idx]                      # Passage-Prefix des Modells ist leer
        e = modell.encode(texte, batch_size=32, normalize_embeddings=True, show_progress_bar=True)
        vek = np.zeros((len(chunk_zeilen), e.shape[1]), dtype=np.float16)
        for i, v in zip(neu_idx, e):
            vek[i] = v
    else:
        vek = np.zeros((len(chunk_zeilen), len(next(iter(alt.values())))), dtype=np.float16)
    for i, z in enumerate(chunk_zeilen):
        if z["embed_hash"] in alt:
            vek[i] = alt[z["embed_hash"]]

    # BM25 über Kontextsatz plus Text ("contextual BM25"); gespeichert wird der Originaltext
    bm = bm25_bauen([(z["kontext"] + "\n\n" if z["kontext"] else "") + z["text"] for z in chunk_zeilen])

    # In einen Build-Ordner schreiben, nie direkt nach current
    stempel = time.strftime("%Y%m%d-%H%M%S")
    build = ziel / f"build-{stempel}"
    build.mkdir()
    np.save(build / "vectors.npy", vek)
    np.savez(build / "bm25.npz", **bm)
    (build / "chunks.jsonl").write_text(
        "\n".join(json.dumps(z, ensure_ascii=False) for z in chunk_zeilen) + "\n", encoding="utf-8")
    (build / "registry.jsonl").write_text(
        "\n".join(json.dumps(z, ensure_ascii=False) for z in register) + "\n", encoding="utf-8")
    (build / "manifest.json").write_text(json.dumps({
        "model": MODELL, "dimension": int(vek.shape[1]), "token_cap": TOKEN_CAP,
        "chunks": len(chunk_zeilen), "gebaut": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }, indent=2), encoding="utf-8")

    # Umschalten: alten Stand zur Seite legen, Build wird current
    cur = ziel / "current"
    if cur.exists():
        cur.rename(ziel / f"build-vorher-{stempel}")
    build.rename(cur)
    print(f"Fertig in {time.time() - t0:.0f} s: {cur}")


if __name__ == "__main__":
    main()
