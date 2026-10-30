#!/usr/bin/env python
"""MCP-Server: macht die Suche für Claude als Werkzeug verfügbar (stdio).

Start (normalerweise startet Claude den Server selbst, siehe README.md):
    BRAIN_INDEX=index/current python mcp_server.py

Drei Werkzeuge: suchen, stelle, deckung. Sie rufen suche.py auf. Alles bleibt auf
dem eigenen Rechner. Nur Frage und Treffer gehen im Gespräch an Claude.
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))   # suche.py liegt neben dieser Datei

from mcp.server.fastmcp import FastMCP

# Schwere Pakete schon beim Start im Hauptthread laden. Unter Windows hing der
# erste Import sonst mitten in der ersten Suche (DLL-Laden in einem Worker-Thread).
import torch  # noqa: F401
import sentence_transformers  # noqa: F401

import suche as s

mcp = FastMCP("brain")


@mcp.tool()
async def suchen(frage: str, frage_en: str = "", k: int = 8, type: str = "", quelle: str = "",
           rerank: bool = False, quellen_deckel: int = 2) -> dict:
    """Durchsucht das Brain nach Textstellen und gibt Quelle, Seite und Wortlaut zurück.

    frage: die Frage auf Deutsch, als Satz oder mit Stichwörtern.
    frage_en: dieselbe Frage auf Englisch. Immer mitgeben, auch bei deutschen Quellen,
        weil englische Stichwörter bei englischen Quellen deutlich besser treffen.
    k: Zahl der Treffer (Standard 8).
    type: nur Quellen dieses Typs (zum Beispiel primary-source).
    quelle: nur Quellen, deren Titel dieses Wort enthält (an Wortgrenzen).
    rerank: Treffer mit dem Reranker neu ordnen (langsam ohne GPU).
    quellen_deckel: höchstens so viele Treffer je Quelle (0 schaltet ab).
    Das Feld 'luecken' nennt ungesehene Nachbarstellen, die mit 'stelle' geholt werden können.
    Keine Treffer heißt nicht, dass das Thema im Bestand fehlt: Frage anders formulieren.
    """
    # Modell laden und Rechnen in einem Thread, damit der Server auf Anfragen antwortbereit bleibt
    ergebnis = await asyncio.to_thread(s.suchen, frage, frage_en or None, k, type or None,
                                       quelle or None, rerank, quellen_deckel)
    antwort = {"treffer": ergebnis}
    if not frage_en:
        antwort["hinweis"] = "frage_en fehlt. Bitte dieselbe Frage auf Englisch mitgeben."
    if not ergebnis:
        antwort["hinweis"] = "Keine Treffer. Das heißt nicht, dass das Thema fehlt: Filter lockern, anders formulieren."
    return antwort


@mcp.tool()
async def stelle(nr: int, umgebung: int = 1) -> dict:
    """Holt Treffer 'nr' samt Nachbarstellen derselben Quelle, um am Stück zu lesen oder Lücken zu schließen."""
    return {"stellen": await asyncio.to_thread(s.stelle, nr, umgebung)}


@mcp.tool()
async def deckung() -> dict:
    """Zeigt, welche Quellen im Register stehen und wie viele Textstellen davon im Index sind."""
    return await asyncio.to_thread(s.deckung)


if __name__ == "__main__":
    if "BRAIN_INDEX" not in os.environ:
        print("Hinweis: BRAIN_INDEX nicht gesetzt, nehme index/current neben dem Skript.", file=sys.stderr)
    mcp.run()   # stdio
