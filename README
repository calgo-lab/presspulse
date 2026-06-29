# DLF-Presseschau Pipeline: Automated Ingestion, Classification & Sync

[![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=flat&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Transformers](https://img.shields.io/badge/%F0%9F%A4%97-Transformers-orange.svg?style=flat)](https://huggingface.co/docs/transformers/index)

Dieses Repository enthält die Kern-Pipeline für das universitäre SHK-Projekt `fipitest`. Das System automatisiert das **Web-Scraping**, die **strukturelle Vorverarbeitung (Parsing)**, die **NLP-Klassifizierung (Machine Learning)** sowie die **Verteilung** der täglichen *Internationalen Presseschau* des Deutschlandfunks (DLF).

Ziel der Pipeline ist es, die unstrukturierten Medienanalysen des DLF in semantisch angereicherte, maschinenlesbare Zeitreihendaten zu transformieren und diese über eine automatisierte GitHub-Synchronisation für nachgelagerte Anwendungen (z. B. Web-Frontends) bereitzustellen.

---

## Systemarchitektur & Datenfluss

Die Pipeline ist modular aufgebaut und trennt die Belange von Datengewinnung, Inferenz und I/O-Synchronisation strikt voneinander. Die Steuerung des gesamten Prozesses übernimmt zentral das Orchestrierungs-Skript `scheduler.py`.

Der operative Ablauf gliedert sich in vier chronologische Kernphasen:

* **1. Datengewinnung (Ingestion):** Das Skript `scraper.py` initiiert den Prozess, indem es die offizielle Übersichtsseite des Deutschlandfunks ansteuert. Es isoliert autonom den jüngsten relevanten Artikel-Link und lädt dessen HTML-Quelltext herunter. Falls die Struktur der Seite Abweichungen aufweist, sichert eine mehrstufige RegEx- und HTML-Fallback-Logik die korrekte Ermittlung des Veröffentlichungsdatums.
* **2. Strukturierung (Normalization):** Der in Phase 1 geladene HTML-Code wird an den DOM-Parser in `myparser.py` übergeben. Dieses Modul bricht den zusammenhängenden Fließtext der Presseschau auf, isoliert die einzelnen Pressestimmen und überführt sie in strukturierte Python-Dictionaries, die getrennte Felder für das Quellmedium, das Herkunftsland und das eigentliche Zitat enthalten.
* **3. Semantische Analyse (Inference):** Die strukturierten Textsegmente werden an `classifier.py` übergeben. Hier gelingt die thematische Einordnung über ein lokales Hugging Face Sprachmodell. Das Modul tokenisiert die Texte, berechnet über eine mathematische Softmax-Funktion die Wahrscheinlichkeitsverteilung über alle gelernten Themenklassen und ordnet jedem Beitrag das statistisch sicherste Label inklusive Score zu.
* **4. Archivierung & Synchronisation (Persistence):** Das Steuerungsskript `scheduler.py` übernimmt die Finalisierung. Es prüft, ob lokal bereits Daten für den aktuellen Tag vorliegen, führt alte und neue Datensätze inkrementell zusammen und speichert sie als komprimierte Gzip-JSON-Datei. Unmittelbar danach wird die Datei über die GitHub REST Content API direkt in das Cloud-Repository gespiegelt, wodurch nachgelagerte Systeme instantan Zugriff auf die aktualisierte Datenbasis erhalten.


##  Repository-Struktur


```text
├── data/2026/05/          # Lokales Datenarchiv (Struktur: /Jahr/Monat/Tag.json.gz)
├── k8s/
│   └── cronjob.yaml       # Kubernetes Manifest für den orchestrierten Cluster-Betrieb
├── .gitignore             # Git-Ausschlussprofile
├── classifier.py          # Inferenz-Engine (PyTorch & Hugging Face Transformers)
├── Dockerfile             # Multi-Stage Docker-Build für die Pipeline
├── index.html             # Einstiegspunkt für die Visualisierung / Prototyping
├── myparser.py            # DOM-Parser zur Extraktion strukturierter Beitrags-Objekte
├── presseschau.json       # Statische Testdaten für lokale Sandbox-Tests
├── requirements.txt       # Anwendungs-Abhängigkeiten mit fixierten Core-Paketen
├── scheduler.py           # Orchestrator, CLI-Schnittstelle und GitHub-Synchronisator
└── scraper.py             # Resilienter Web-Scraper mit automatischem Datums-Fallback