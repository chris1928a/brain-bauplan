#!/usr/bin/env python
"""Goldset-Lauf: stellt jede Frage aus fragen.jsonl und misst, wo die erwartete Quelle landet.

    python goldset.py                       # beispiel/fragen.jsonl
    python goldset.py meine-fragen.jsonl --rerank

Zeile in fragen.jsonl: {"id", "frage", "frage_en", "erwartet_quelle_substring"}.
Ein Treffer zählt, wenn der Quellentitel den Teilstring enthält (Groß/Klein egal).
Ausgabe: hit@1, hit@8, MRR (Mean Reciprocal Rank: Mittel aus 1/Rang des ersten richtigen Treffers).
"""
import argparse
import json
import sys
import time
from pathlib import Path

import suche

K = 8


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fragen", nargs="?", type=Path, default=Path(__file__).parent / "beispiel" / "fragen.jsonl")
    ap.add_argument("--rerank", action="store_true")
    a = ap.parse_args()

    fragen = [json.loads(z) for z in a.fragen.read_text(encoding="utf-8").splitlines() if z.strip()]
    raenge = []
    t0 = time.time()
    for f in fragen:
        # quellen_deckel=0: der Rang soll die reine Ordnung zeigen, nicht den Deckel
        treffer = suche.suchen(f["frage"], f.get("frage_en"), k=K, rerank=a.rerank, quellen_deckel=0)
        rang = next((i + 1 for i, t in enumerate(treffer)
                     if f["erwartet_quelle_substring"].lower() in t["quelle"].lower()), None)
        raenge.append(rang)
        print(f"{f['id']}: Rang {rang if rang else 'nicht in den Top ' + str(K)}  | {f['frage']}")

    n = len(raenge)
    hit1 = sum(1 for r in raenge if r == 1) / n
    hit8 = sum(1 for r in raenge if r) / n
    mrr = sum(1 / r for r in raenge if r) / n
    print(f"\nFragen: {n}  hit@1: {hit1:.3f}  hit@{K}: {hit8:.3f}  MRR: {mrr:.3f}  ({time.time() - t0:.1f} s)")


if __name__ == "__main__":
    main()
