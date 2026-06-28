#!/usr/bin/env python3
"""
ConText Revival – DOS-Texteditor Nachbildung (Python/Tkinter)
Basiert auf dem originalen ConText von Borland (1985/1992)
mit deutschsprachiger Benutzeroberfläche
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import sys
import time

# ─── Farbpalette (CGA-Stil, wie im Original) ───────────────────────────────
BG_EDITOR   = "#000080"   # Dunkelblau – Editor-Hintergrund
FG_EDITOR   = "#FFFFFF"   # Weiß – Textfarbe
BG_MENU     = "#00AAAA"   # Cyan – Menüleiste
FG_MENU     = "#000000"   # Schwarz – Menütext
BG_STATUS   = "#00AAAA"   # Cyan – Statuszeile
FG_STATUS   = "#000000"
BG_SEL      = "#FFFF00"   # Gelb – Markierung
FG_SEL      = "#000000"
BG_DIALOG   = "#00AAAA"
FG_DIALOG   = "#000000"
BG_CURSOR   = "#FFFFFF"
FONT_MAIN   = ("Courier", 12, "normal")
FONT_MENU   = ("Courier", 11, "bold")
FONT_STATUS = ("Courier", 10, "normal")


class ConTextEditor:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ConText Revival –  DOS-Texteditor - Made by Noel Joan")
        self.root.configure(bg=BG_EDITOR)
        self.root.geometry("900x600")
        self.root.minsize(640, 400)

        self.current_file: str | None = None
        self.modified = False
        self.block_start: str | None = None
        self.block_end: str | None = None
        self.block_active = False
        self.clipboard_text = ""
        self.search_term = ""
        self.replace_term = ""
        self.macro_recording = False
        self.macro_keys: list = []

        self._build_ui()
        self._bind_keys()
        self._update_status()

    # ──────────────────────────────────────────────────────────────────────
    #  UI-Aufbau
    # ──────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Menüleiste (original: Text-Menüband oben) ──
        self.menubar = tk.Menu(
            self.root,
            bg=BG_MENU, fg=FG_MENU,
            activebackground="#FFFFFF", activeforeground="#000000",
            font=FONT_MENU, relief="flat", bd=0
        )
        self.root.config(menu=self.menubar)

        menus = [
            ("Datei",    self._menu_datei()),
            ("Löschen",  self._menu_loeschen()),
            ("Block",    self._menu_block()),
            ("Schrift",  self._menu_schrift()),
            ("Format",   self._menu_format()),
            ("Layout",   self._menu_layout()),
            ("Suchen",   self._menu_suchen()),
            ("Extra",    self._menu_extra()),
            ("Drucken",  self._menu_drucken()),
            ("Hilfe",    self._menu_hilfe()),
        ]

        for label, menu in menus:
            self.menubar.add_cascade(label=f" {label} ", menu=menu)

        # ── Editor-Rahmen ──
        editor_frame = tk.Frame(self.root, bg=BG_EDITOR, bd=0)
        editor_frame.pack(fill="both", expand=True)

        # Zeilennummern
        self.line_numbers = tk.Text(
            editor_frame,
            width=4, bg="#004080", fg="#88CCFF",
            font=FONT_MAIN, state="disabled",
            bd=0, highlightthickness=0,
            cursor="arrow", wrap="none",
            insertwidth=0
        )
        self.line_numbers.pack(side="left", fill="y")

        # Scrollbar
        scrollbar = tk.Scrollbar(editor_frame, orient="vertical",
                                  bg=BG_MENU, troughcolor=BG_EDITOR,
                                  width=12)
        scrollbar.pack(side="right", fill="y")

        # Text-Widget
        self.text = tk.Text(
            editor_frame,
            bg=BG_EDITOR, fg=FG_EDITOR,
            insertbackground=BG_CURSOR,
            selectbackground=BG_SEL, selectforeground=FG_SEL,
            font=FONT_MAIN,
            wrap="none", undo=True,
            bd=0, highlightthickness=1,
            highlightcolor="#00AAAA",
            highlightbackground=BG_EDITOR,
            yscrollcommand=self._on_scroll,
            cursor="xterm",
            tabs=("0.5c",),
            spacing1=0, spacing2=0, spacing3=0
        )
        self.text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self._scroll_both)

        hscrollbar = tk.Scrollbar(self.root, orient="horizontal",
                                   bg=BG_MENU, troughcolor=BG_EDITOR, width=10)
        hscrollbar.pack(side="bottom", fill="x")
        self.text.config(xscrollcommand=hscrollbar.set)
        hscrollbar.config(command=self.text.xview)

        # ── Statuszeile ──
        self.status_frame = tk.Frame(self.root, bg=BG_STATUS, height=22)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)

        self.status_left = tk.Label(
            self.status_frame, text="", bg=BG_STATUS, fg=FG_STATUS,
            font=FONT_STATUS, anchor="w", padx=6
        )
        self.status_left.pack(side="left")

        self.status_right = tk.Label(
            self.status_frame, text="", bg=BG_STATUS, fg=FG_STATUS,
            font=FONT_STATUS, anchor="e", padx=6
        )
        self.status_right.pack(side="right")

        self.status_mid = tk.Label(
            self.status_frame, text="", bg=BG_STATUS, fg=FG_STATUS,
            font=FONT_STATUS, anchor="center"
        )
        self.status_mid.pack(side="left", expand=True)

        # Block-Tag
        self.text.tag_config("block", background=BG_SEL, foreground=FG_SEL)

    def _scroll_both(self, *args):
        self.text.yview(*args)
        self._update_line_numbers()

    def _on_scroll(self, first, last):
        self.text.yview_moveto(first)
        self._update_line_numbers()

    # ──────────────────────────────────────────────────────────────────────
    #  Menü-Definitionen
    # ──────────────────────────────────────────────────────────────────────

    def _make_menu(self):
        m = tk.Menu(self.menubar, tearoff=0,
                    bg=BG_MENU, fg=FG_MENU,
                    activebackground="#FFFFFF", activeforeground="#000000",
                    font=FONT_MENU, relief="flat", bd=1)
        return m

    def _menu_datei(self):
        m = self._make_menu()
        m.add_command(label="Neu               Ctrl+N", command=self.datei_neu)
        m.add_command(label="Öffnen...         Ctrl+O", command=self.datei_oeffnen)
        m.add_separator()
        m.add_command(label="Speichern         Ctrl+S", command=self.datei_speichern)
        m.add_command(label="Speichern unter...",       command=self.datei_speichern_unter)
        m.add_separator()
        m.add_command(label="Beenden           Alt+X",  command=self.datei_beenden)
        return m

    def _menu_loeschen(self):
        m = self._make_menu()
        m.add_command(label="Zeile löschen     Ctrl+Y",  command=self.loeschen_zeile)
        m.add_command(label="Zeilenanfang      Ctrl+Q+S",command=self.gehe_zeilenanfang)
        m.add_command(label="Zeilenende        Ctrl+Q+D",command=self.gehe_zeilenende)
        m.add_separator()
        m.add_command(label="Alles auswählen   Ctrl+A",  command=self.alles_auswaehlen)
        return m

    def _menu_block(self):
        m = self._make_menu()
        m.add_command(label="Block-Anfang      Ctrl+K+B",  command=self.block_anfang)
        m.add_command(label="Block-Ende        Ctrl+K+K",  command=self.block_ende)
        m.add_separator()
        m.add_command(label="Block kopieren    Ctrl+K+C",  command=self.block_kopieren)
        m.add_command(label="Block verschieben Ctrl+K+V",  command=self.block_verschieben)
        m.add_command(label="Block löschen     Ctrl+K+Y",  command=self.block_loeschen)
        m.add_separator()
        m.add_command(label="Block speichern...",           command=self.block_speichern)
        m.add_command(label="Block laden...",               command=self.block_laden)
        return m

    def _menu_schrift(self):
        m = self._make_menu()
        m.add_command(label="Größer            Ctrl++",  command=lambda: self._schrift_groesse(+1))
        m.add_command(label="Kleiner           Ctrl+-",  command=lambda: self._schrift_groesse(-1))
        m.add_separator()
        m.add_command(label="Standard (12pt)",            command=lambda: self._schrift_setzen(12))
        return m

    def _menu_format(self):
        m = self._make_menu()
        m.add_command(label="Tabulator-Breite...",  command=self.format_tabulator)
        m.add_command(label="Einrücken            Tab",
                      command=lambda: self.text.insert("insert", "\t"))
        return m

    def _menu_layout(self):
        m = self._make_menu()
        m.add_command(label="Zeilenumbruch ein/aus  Ctrl+W", command=self.layout_umbruch)
        m.add_separator()
        m.add_command(label="Gehe zu Zeile...       Ctrl+G", command=self.gehe_zu_zeile)
        return m

    def _menu_suchen(self):
        m = self._make_menu()
        m.add_command(label="Suchen...          Ctrl+F",  command=self.suchen_dialog)
        m.add_command(label="Weitersuchen       F3",       command=self.suchen_weiter)
        m.add_separator()
        m.add_command(label="Ersetzen...        Ctrl+H",  command=self.ersetzen_dialog)
        return m

    def _menu_extra(self):
        m = self._make_menu()
        m.add_command(label="Makro definieren...  Ctrl+M", command=self.makro_definieren)
        m.add_separator()
        m.add_command(label="Wort-Zählung",               command=self.wortzaehlung)
        m.add_command(label="Datum/Uhrzeit einfügen",      command=self.datum_einfuegen)
        m.add_separator()
        m.add_command(label="DOS-Shell            Ctrl+Z", command=self.dos_shell)
        return m

    def _menu_drucken(self):
        m = self._make_menu()
        m.add_command(label="Drucken...         Ctrl+P",  command=self.drucken)
        return m

    def _menu_hilfe(self):
        m = self._make_menu()
        m.add_command(label="Tastenkürzel",  command=self.hilfe_tasten)
        m.add_command(label="Über ConText",  command=self.hilfe_ueber)
        return m

    # ──────────────────────────────────────────────────────────────────────
    #  Tastenbindungen
    # ──────────────────────────────────────────────────────────────────────

    def _bind_keys(self):
        t = self.text
        t.bind("<<Modified>>",       self._on_modified)
        t.bind("<KeyRelease>",       self._on_key)
        t.bind("<ButtonRelease-1>",  self._on_key)

        self.root.bind("<Control-n>", lambda e: self.datei_neu())
        self.root.bind("<Control-o>", lambda e: self.datei_oeffnen())
        self.root.bind("<Control-s>", lambda e: self.datei_speichern())
        self.root.bind("<Control-f>", lambda e: self.suchen_dialog())
        self.root.bind("<Control-h>", lambda e: self.ersetzen_dialog())
        self.root.bind("<Control-g>", lambda e: self.gehe_zu_zeile())
        self.root.bind("<Control-w>", lambda e: self.layout_umbruch())
        self.root.bind("<Control-y>", lambda e: self.loeschen_zeile())
        self.root.bind("<Control-a>", lambda e: self.alles_auswaehlen())
        self.root.bind("<Control-m>", lambda e: self.makro_definieren())
        self.root.bind("<Control-p>", lambda e: self.drucken())
        self.root.bind("<Control-z>", lambda e: self.dos_shell())
        self.root.bind("<F3>",        lambda e: self.suchen_weiter())
        self.root.bind("<Alt-x>",     lambda e: self.datei_beenden())
        self.root.bind("<Control-plus>",  lambda e: self._schrift_groesse(+1))
        self.root.bind("<Control-minus>", lambda e: self._schrift_groesse(-1))
        self.root.protocol("WM_DELETE_WINDOW", self.datei_beenden)

    # ──────────────────────────────────────────────────────────────────────
    #  Ereignis-Handler
    # ──────────────────────────────────────────────────────────────────────

    def _on_modified(self, event=None):
        if self.text.edit_modified():
            self.modified = True
            self._update_title()
            self.text.edit_modified(False)
        self._update_line_numbers()
        self._update_status()

    def _on_key(self, event=None):
        self._update_status()
        self._update_line_numbers()

    def _update_title(self):
        mod = " *" if self.modified else ""
        name = os.path.basename(self.current_file) if self.current_file else "Unbenannt"
        self.root.title(f"ConText  –  {name}{mod}")

    def _update_status(self):
        try:
            pos = self.text.index("insert")
            row, col = pos.split(".")
            total = int(self.text.index("end-1c").split(".")[0])
            content = self.text.get("1.0", "end-1c")
            chars = len(content)
            fname = self.current_file or "Kein Dokument"
            mod_str = "  [verändert]" if self.modified else ""
            self.status_left.config(text=f" {os.path.basename(fname)}{mod_str}")
            self.status_mid.config(text=f"Seite 1    Zeile {row}    Spalte {int(col)+1}")
            self.status_right.config(text=f"Zeichen: {chars}  Zeilen: {total} ")
        except Exception:
            pass

    def _update_line_numbers(self):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        total_lines = int(self.text.index("end-1c").split(".")[0])
        line_text = "\n".join(f"{i:3}" for i in range(1, total_lines + 1))
        self.line_numbers.insert("1.0", line_text)
        # Sync scroll
        self.line_numbers.yview_moveto(self.text.yview()[0])
        self.line_numbers.config(state="disabled")

    # ──────────────────────────────────────────────────────────────────────
    #  Datei-Operationen
    # ──────────────────────────────────────────────────────────────────────

    def datei_neu(self):
        if not self._check_modified():
            return
        self.text.delete("1.0", "end")
        self.current_file = None
        self.modified = False
        self._update_title()
        self._update_status()
        self._update_line_numbers()

    def datei_oeffnen(self):
        if not self._check_modified():
            return
        path = filedialog.askopenfilename(
            title="Text laden – Dateiname",
            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
        )
        if path:
            self._lade_datei(path)

    def _lade_datei(self, path: str):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                inhalt = f.read()
            self.text.delete("1.0", "end")
            self.text.insert("1.0", inhalt)
            self.current_file = path
            self.modified = False
            self._update_title()
            self._update_status()
            self._update_line_numbers()
        except Exception as e:
            messagebox.showerror("Fehler", f"Datei konnte nicht geladen werden:\n{e}")

    def datei_speichern(self):
        if self.current_file:
            self._speichern(self.current_file)
        else:
            self.datei_speichern_unter()

    def datei_speichern_unter(self):
        path = filedialog.asksaveasfilename(
            title="Text speichern – Dateiname",
            defaultextension=".txt",
            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
        )
        if path:
            self._speichern(path)

    def _speichern(self, path: str):
        try:
            inhalt = self.text.get("1.0", "end-1c")
            with open(path, "w", encoding="utf-8") as f:
                f.write(inhalt)
            self.current_file = path
            self.modified = False
            self._update_title()
            self._update_status()
            self._status_flash(f"Gespeichert: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Speichern fehlgeschlagen:\n{e}")

    def datei_beenden(self):
        if self._check_modified():
            self.root.destroy()

    def _check_modified(self) -> bool:
        if self.modified:
            antwort = messagebox.askyesnocancel(
                "Nicht gespeichert",
                "Der Text wurde geändert.\nÄnderungen speichern?"
            )
            if antwort is None:
                return False
            if antwort:
                self.datei_speichern()
        return True

    # ──────────────────────────────────────────────────────────────────────
    #  Löschen / Cursor
    # ──────────────────────────────────────────────────────────────────────

    def loeschen_zeile(self):
        self.text.delete("insert linestart", "insert lineend+1c")

    def gehe_zeilenanfang(self):
        self.text.mark_set("insert", "insert linestart")
        self.text.see("insert")

    def gehe_zeilenende(self):
        self.text.mark_set("insert", "insert lineend")
        self.text.see("insert")

    def alles_auswaehlen(self):
        self.text.tag_add("sel", "1.0", "end")

    # ──────────────────────────────────────────────────────────────────────
    #  Block-Operationen
    # ──────────────────────────────────────────────────────────────────────

    def block_anfang(self):
        self.block_start = self.text.index("insert")
        self.block_active = False
        self._status_flash("Block-Anfang gesetzt")

    def block_ende(self):
        if not self.block_start:
            messagebox.showwarning("Block", "Zuerst Block-Anfang setzen (Ctrl+K+B)")
            return
        self.block_end = self.text.index("insert")
        self.text.tag_remove("block", "1.0", "end")
        self.text.tag_add("block", self.block_start, self.block_end)
        self.block_active = True
        self._status_flash("Block markiert")

    def _get_block_text(self) -> str:
        if self.block_active and self.block_start and self.block_end:
            return self.text.get(self.block_start, self.block_end)
        # Fallback: Selektion
        try:
            return self.text.get("sel.first", "sel.last")
        except tk.TclError:
            return ""

    def block_kopieren(self):
        txt = self._get_block_text()
        if txt:
            self.clipboard_text = txt
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            # Kopie an Cursor-Position einfügen
            self.text.insert("insert", txt)
            self._status_flash("Block kopiert")

    def block_verschieben(self):
        txt = self._get_block_text()
        if txt and self.block_active:
            self.text.delete(self.block_start, self.block_end)
            self.text.insert("insert", txt)
            self.block_active = False
            self._status_flash("Block verschoben")

    def block_loeschen(self):
        if self.block_active and self.block_start and self.block_end:
            self.text.delete(self.block_start, self.block_end)
            self.text.tag_remove("block", "1.0", "end")
            self.block_active = False
            self._status_flash("Block gelöscht")

    def block_speichern(self):
        txt = self._get_block_text()
        if not txt:
            messagebox.showwarning("Block", "Kein Block markiert")
            return
        path = filedialog.asksaveasfilename(
            title="Block speichern – Dateiname",
            defaultextension=".txt",
            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            self._status_flash(f"Block gespeichert: {os.path.basename(path)}")

    def block_laden(self):
        path = filedialog.askopenfilename(
            title="Block laden – Dateiname",
            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
        )
        if path:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                txt = f.read()
            self.text.insert("insert", txt)
            self._status_flash(f"Block geladen: {os.path.basename(path)}")

    # ──────────────────────────────────────────────────────────────────────
    #  Schrift
    # ──────────────────────────────────────────────────────────────────────

    def _schrift_groesse(self, delta: int):
        current = self.text.cget("font")
        try:
            fam, size, *rest = str(current).split()
            new_size = max(6, min(32, int(size) + delta))
            self._schrift_setzen(new_size)
        except Exception:
            self._schrift_setzen(12 + delta)

    def _schrift_setzen(self, size: int):
        new_font = ("Courier", size, "normal")
        self.text.config(font=new_font)
        self.line_numbers.config(font=new_font)
        self._status_flash(f"Schriftgröße: {size}pt")

    # ──────────────────────────────────────────────────────────────────────
    #  Format / Layout
    # ──────────────────────────────────────────────────────────────────────

    def format_tabulator(self):
        val = simpledialog.askinteger(
            "Tabulator-Breite",
            "Anzahl der Leerzeichen pro Tabulator:",
            initialvalue=4, minvalue=1, maxvalue=16,
            parent=self.root
        )
        if val:
            tab_width = val * 7   # Pixel-Näherung
            self.text.config(tabs=(f"{tab_width}",))
            self._status_flash(f"Tabulator: {val} Zeichen")

    def layout_umbruch(self):
        current = self.text.cget("wrap")
        if current == "none":
            self.text.config(wrap="word")
            self._status_flash("Zeilenumbruch: EIN")
        else:
            self.text.config(wrap="none")
            self._status_flash("Zeilenumbruch: AUS")

    def gehe_zu_zeile(self):
        val = simpledialog.askstring(
            "Cursor-Position",
            "Cursor nach Zeile,Spalte:",
            initialvalue="1,1",
            parent=self.root
        )
        if val:
            try:
                parts = val.replace(" ", "").split(",")
                row = int(parts[0])
                col = int(parts[1]) - 1 if len(parts) > 1 else 0
                self.text.mark_set("insert", f"{row}.{col}")
                self.text.see("insert")
                self._update_status()
            except Exception:
                messagebox.showerror("Fehler", "Ungültige Zeile/Spalte-Angabe")

    # ──────────────────────────────────────────────────────────────────────
    #  Suchen / Ersetzen
    # ──────────────────────────────────────────────────────────────────────

    def suchen_dialog(self):
        self._suchen_fenster(ersetzen=False)

    def ersetzen_dialog(self):
        self._suchen_fenster(ersetzen=True)

    def _suchen_fenster(self, ersetzen: bool):
        win = tk.Toplevel(self.root)
        win.title("Ersetzen" if ersetzen else "Suchen")
        win.configure(bg=BG_DIALOG)
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Suchen:", bg=BG_DIALOG, fg=FG_DIALOG,
                 font=FONT_STATUS).grid(row=0, column=0, sticky="w", padx=8, pady=4)
        e_suchen = tk.Entry(win, width=35, font=FONT_MAIN)
        e_suchen.insert(0, self.search_term)
        e_suchen.grid(row=0, column=1, padx=8, pady=4)
        e_suchen.focus_set()

        e_ersetzen = None
        if ersetzen:
            tk.Label(win, text="Ersetzen durch:", bg=BG_DIALOG, fg=FG_DIALOG,
                     font=FONT_STATUS).grid(row=1, column=0, sticky="w", padx=8, pady=4)
            e_ersetzen = tk.Entry(win, width=35, font=FONT_MAIN)
            e_ersetzen.insert(0, self.replace_term)
            e_ersetzen.grid(row=1, column=1, padx=8, pady=4)

        btn_frame = tk.Frame(win, bg=BG_DIALOG)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=6)

        def do_suchen():
            self.search_term = e_suchen.get()
            self.suchen_weiter()

        def do_ersetzen():
            self.search_term = e_suchen.get()
            self.replace_term = e_ersetzen.get() if e_ersetzen else ""
            self._ersetzen_einmal()

        def do_alle():
            self.search_term = e_suchen.get()
            self.replace_term = e_ersetzen.get() if e_ersetzen else ""
            self._ersetzen_alle()
            win.destroy()

        tk.Button(btn_frame, text="Suchen", width=12, command=do_suchen,
                  bg=BG_MENU, font=FONT_STATUS).pack(side="left", padx=4)
        if ersetzen:
            tk.Button(btn_frame, text="Ersetzen", width=12, command=do_ersetzen,
                      bg=BG_MENU, font=FONT_STATUS).pack(side="left", padx=4)
            tk.Button(btn_frame, text="Alle ersetzen", width=14, command=do_alle,
                      bg=BG_MENU, font=FONT_STATUS).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Abbrechen", width=12, command=win.destroy,
                  bg=BG_MENU, font=FONT_STATUS).pack(side="left", padx=4)

    def suchen_weiter(self):
        if not self.search_term:
            self.suchen_dialog()
            return
        start = self.text.search(self.search_term, "insert+1c",
                                  stopindex="end", nocase=True)
        if not start:
            start = self.text.search(self.search_term, "1.0",
                                      stopindex="end", nocase=True)
        if start:
            end = f"{start}+{len(self.search_term)}c"
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", start, end)
            self.text.mark_set("insert", end)
            self.text.see(start)
            self._status_flash(f'Gefunden: "{self.search_term}"')
        else:
            self._status_flash(f'"{self.search_term}" nicht gefunden')

    def _ersetzen_einmal(self):
        try:
            sel_start = self.text.index("sel.first")
            sel_end = self.text.index("sel.last")
            sel_text = self.text.get(sel_start, sel_end)
            if sel_text.lower() == self.search_term.lower():
                self.text.delete(sel_start, sel_end)
                self.text.insert(sel_start, self.replace_term)
        except tk.TclError:
            pass
        self.suchen_weiter()

    def _ersetzen_alle(self):
        count = 0
        start = "1.0"
        while True:
            pos = self.text.search(self.search_term, start,
                                    stopindex="end", nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(self.search_term)}c"
            self.text.delete(pos, end)
            self.text.insert(pos, self.replace_term)
            start = f"{pos}+{len(self.replace_term)}c"
            count += 1
        self._status_flash(f"{count} Ersetzung(en) durchgeführt")

    # ──────────────────────────────────────────────────────────────────────
    #  Extra
    # ──────────────────────────────────────────────────────────────────────

    def makro_definieren(self):
        messagebox.showinfo(
            "Makro definieren",
            "Makro-Funktion: Drücken Sie eine Taste, um das Makro auszulösen.\n"
            "(In dieser Version: Datum/Uhrzeit-Einfügung als Demo-Makro)"
        )
        self.datum_einfuegen()

    def wortzaehlung(self):
        inhalt = self.text.get("1.0", "end-1c")
        woerter = len(inhalt.split())
        zeilen = inhalt.count("\n") + 1
        zeichen = len(inhalt)
        absaetze = inhalt.count("\n\n") + 1
        messagebox.showinfo(
            "Wort-Zählung",
            f"Zeichen:   {zeichen}\n"
            f"Wörter:    {woerter}\n"
            f"Zeilen:    {zeilen}\n"
            f"Absätze:   {absaetze}"
        )

    def datum_einfuegen(self):
        now = time.strftime("%d.%m.%Y  %H:%M:%S")
        self.text.insert("insert", now)
        self._status_flash(f"Datum/Uhrzeit eingefügt: {now}")

    def dos_shell(self):
        messagebox.showinfo(
            "DOS-Shell",
            "DOS-Shell: In dieser Python-Version nicht verfügbar.\n"
            "Verwenden Sie ein separates Terminal-Fenster."
        )

    # ──────────────────────────────────────────────────────────────────────
    #  Drucken
    # ──────────────────────────────────────────────────────────────────────

    def drucken(self):
        import platform
        inhalt = self.text.get("1.0", "end-1c")
        if platform.system() == "Windows":
            tmp = os.path.join(os.environ.get("TEMP", "."), "_context_print.txt")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(inhalt)
            os.startfile(tmp, "print")
        else:
            messagebox.showinfo(
                "Drucken",
                "Drucken: Bitte das Dokument zuerst speichern\n"
                "und dann über den Datei-Manager drucken."
            )

    # ──────────────────────────────────────────────────────────────────────
    #  Hilfe
    # ──────────────────────────────────────────────────────────────────────

    def hilfe_tasten(self):
        keys = (
            "TASTENKÜRZEL – ConText\n"
            "══════════════════════════════════\n"
            "Ctrl+N      Neue Datei\n"
            "Ctrl+O      Datei öffnen\n"
            "Ctrl+S      Speichern\n"
            "Ctrl+F      Suchen\n"
            "Ctrl+H      Ersetzen\n"
            "Ctrl+G      Gehe zu Zeile\n"
            "Ctrl+W      Zeilenumbruch ein/aus\n"
            "Ctrl+Y      Zeile löschen\n"
            "Ctrl+A      Alles auswählen\n"
            "Ctrl+Z      Rückgängig (Undo)\n"
            "Ctrl+M      Makro definieren\n"
            "Ctrl+P      Drucken\n"
            "F3          Weitersuchen\n"
            "Alt+X       Beenden\n"
            "Ctrl++/-    Schrift vergrößern/verkleinern\n"
            "══════════════════════════════════\n"
            "Block-Operationen:\n"
            "Ctrl+K+B    Block-Anfang\n"
            "Ctrl+K+K    Block-Ende\n"
            "Ctrl+K+C    Block kopieren\n"
            "Ctrl+K+V    Block verschieben\n"
            "Ctrl+K+Y    Block löschen\n"
        )
        messagebox.showinfo("Tastenkürzel", keys)

    def hilfe_ueber(self):
        messagebox.showinfo(
            "Über ConText",
            "ConText – DOS-Texteditor\n"
            "Python/Tkinter Nachbildung\n\n"
            "Original: Copyright © 1985–1992 BORLAND Inc.\n"
            "Nachbildung erstellt für: Noel Joan\n\n"
            "Originalformat: DOS .COM-Programm (64 KB)\n"
            "Compiler:       Borland Pascal/Assembler\n"
            "Erscheinungsjahr: 1985 / 1992"
        )

    # ──────────────────────────────────────────────────────────────────────
    #  Hilfsmethoden
    # ──────────────────────────────────────────────────────────────────────

    def _status_flash(self, msg: str):
        """Kurze Nachricht in der Statuszeile anzeigen"""
        old = self.status_mid.cget("text")
        self.status_mid.config(text=f"  ▶  {msg}  ◀", fg="#FF0000")
        self.root.after(2500, lambda: self.status_mid.config(
            text=old, fg=FG_STATUS))


# ──────────────────────────────────────────────────────────────────────────
#  Einstiegspunkt
# ──────────────────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()

    # Fenster-Icon (DOS-Stil)
    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    app = ConTextEditor(root)

    # Kommandozeilen-Argument: direkt eine Datei öffnen
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        app._lade_datei(sys.argv[1])

    root.mainloop()


if __name__ == "__main__":
    main()
