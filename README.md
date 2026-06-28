# ConText Revival — DOS-Texteditor

> **DE:** Eine Python/Tkinter-Nachbildung des legendären Borland ConText (1985–1992)  
> **EN:** A Python/Tkinter recreation of the legendary Borland ConText DOS text editor (1985–1992)

<br>

```
╔═════════════════════════════════════════════════════════════════════════════════╗
║  Datei  Löschen  Block  Schrift  Format  Layout  Suchen  Extra  Drucken  Hilfe  ║
╠═════════════════════════════════════════════════════════════════════════════════╣
║                                                                                 ║
║  ConText — DOS-Texteditor Revival                          v1.0                 ║
║  Originalgetreues CGA-Farbschema · Deutschsprachige Oberfläche                  ║
║                                                                                 ║
╠═════════════════════════════════════════════════════════════════════════════════╣
║  Unbenannt  [unverändert]        Seite 1    Zeile 1    Spalte 1   Zeilen: 1     ║
╚═════════════════════════════════════════════════════════════════════════════════╝
```

<br>

---

## 🇩🇪 Deutsch

### Was ist ConText?

Das Original `CONTEXT.COM` war ein 64-KB-Texteditor für MS-DOS, entwickelt von **Borland International** (1985–1992) und in Borland Pascal/Assembler geschrieben. Dieses Projekt bringt ihn als moderne Python-Desktopanwendung zurück — mit originalgetreuem CGA-Farbschema, deutscher Benutzeroberfläche und erweitertem Funktionsumfang.

### Schnellstart (Windows EXE)

1. Unter **[Releases](../../releases)** die Datei `ConText.exe` herunterladen
2. Doppelklick — fertig, keine Installation nötig

### Features

| Kategorie | Details |
|---|---|
| 🎨 **Optik** | Originalgetreues CGA-Farbschema (Dunkelblau · Cyan · Weiß · Gelb) |
| 📄 **Datei** | Neu · Öffnen · Speichern · Speichern unter · Beenden mit Änderungsabfrage |
| 🔲 **Block** | Anfang/Ende markieren · Kopieren · Verschieben · Löschen · Laden/Speichern |
| 🔍 **Suchen** | Suchen · Weitersuchen (F3) · Ersetzen · Alle ersetzen |
| 📐 **Format** | Tabulator-Breite · Zeilenumbruch ein/aus |
| ✏️ **Extra** | Datum/Uhrzeit einfügen · Wortzählung · Makro |
| 🖨️ **Drucken** | Systemdrucker (Windows nativ) |
| 📊 **Statuszeile** | Dateiname · Seite · Zeile/Spalte · Zeichen- und Zeilenzähler |
| 🔢 **Zeilennummern** | Synchron scrollend, links im Editor |
| ↩️ **Undo/Redo** | Unbegrenzt |

### Tastenkürzel

| Taste | Aktion |
|---|---|
| `Ctrl+N` | Neue Datei |
| `Ctrl+O` | Datei öffnen |
| `Ctrl+S` | Speichern |
| `Ctrl+F` | Suchen |
| `F3` | Weitersuchen |
| `Ctrl+H` | Ersetzen |
| `Ctrl+G` | Gehe zu Zeile/Spalte |
| `Ctrl+W` | Zeilenumbruch ein/aus |
| `Ctrl+Y` | Aktuelle Zeile löschen |
| `Ctrl+A` | Alles auswählen |
| `Ctrl+Z` | Rückgängig |
| `Ctrl+M` | Makro |
| `Ctrl+P` | Drucken |
| `Ctrl++` / `Ctrl+-` | Schrift vergrößern / verkleinern |
| `Alt+X` | Beenden |

**Block-Operationen:**

| Taste | Aktion |
|---|---|
| `Ctrl+K, B` | Block-Anfang setzen |
| `Ctrl+K, K` | Block-Ende setzen |
| `Ctrl+K, C` | Block kopieren |
| `Ctrl+K, V` | Block verschieben |
| `Ctrl+K, Y` | Block löschen |

<br>

---

## 🇬🇧 English

### What is ConText?

The original `CONTEXT.COM` was a 64 KB MS-DOS text editor developed by **Borland International** (1985–1992), written in Borland Pascal/Assembler. This project brings it back as a modern Python desktop application — faithful to the original CGA color scheme, with a German UI and an expanded feature set.

### Quick Start (Windows EXE)

1. Download `ConText.exe` from **[Releases](../../releases)**
2. Double-click to run — no installation required

### Keyboard Shortcuts

| Key | Action |
|---|---|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save |
| `Ctrl+F` | Find |
| `F3` | Find next |
| `Ctrl+H` | Replace |
| `Ctrl+G` | Go to line/column |
| `Ctrl+W` | Toggle word wrap |
| `Ctrl+Y` | Delete current line |
| `Ctrl+A` | Select all |
| `Ctrl+Z` | Undo |
| `Ctrl+P` | Print |
| `Alt+X` | Exit |

<br>

---

## 🛠️ For Developers / Für Entwickler

### Requirements / Voraussetzungen

- Python 3.8 – 3.12
- Tkinter (included in standard Python / in Python enthalten)
- No external dependencies / Keine externen Abhängigkeiten

### Run from source / Aus Quellcode starten

```bash
git clone https://github.com/noeljoan/context-editor.git
cd context-editor

# Start editor / Editor starten
python context_editor.py

# Open a file directly / Datei direkt öffnen
python context_editor.py meinedatei.txt
```

### Build EXE (Windows) / EXE erstellen

```bash
pip install pyinstaller

pyinstaller --onefile --windowed --name "ConText" context_editor.py
# → dist/ConText.exe
```

> ⚠️ Python 3.13+ is not yet supported by PyInstaller. Use Python 3.12.  
> ⚠️ PyInstaller unterstützt Python 3.13+ noch nicht. Python 3.12 verwenden.

### Project structure / Projektstruktur

```
context-editor/
├── context_editor.py   # Main application (single file, no dependencies)
└── README.md
```

### Original vs. This version / Original vs. Nachbildung

| | Original (1985–1992) | This version / Diese Version |
|---|---|---|
| Language | Borland Pascal / x86 Assembler | Python 3 / Tkinter |
| Platform | MS-DOS | Windows · macOS · Linux |
| Size | 64 KB (.COM format) | ~18 KB |
| UI | CGA text mode 80×25 | CGA color scheme, scalable |
| Dependencies | None | None (stdlib only) |
| Encoding | CP437 (DOS) | UTF-8 |

<br>

---

## License / Lizenz

This project is an independent recreation for personal and educational use.  
Dieses Projekt ist eine unabhängige Nachbildung zum persönlichen Gebrauch und zu Bildungszwecken.

The original **ConText** is © 1985–1992 Borland International Inc.  
No original source code or binaries are included in this repository.  
Keine Quellcodes oder Binärdateien des Originals sind in diesem Repository enthalten.

<br>

---

<p align="center">
  Made by <a href="https://github.com/noeljoan">noeljoan</a> · Python · Tkinter · No dependencies · Single file
</p>
