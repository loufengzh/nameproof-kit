# Nameproof Kit

Kurze Produktidee → begründete Namensvorschläge → vorläufiger Prüfbericht mit Quellen und sichtbaren Lücken. Python 3.10+, ohne Laufzeitabhängigkeiten. Vollständige Schemata: [English README](../README.md).

## Mit dem KI-Agenten installieren

Öffnen Sie das Projekt in Ihrem Coding-Agenten und fügen Sie Folgendes ein:

```text
Richte https://github.com/loufengzh/nameproof-kit in diesem Projekt ein.
Lies README und docs/INSTALL.md. Installiere den nameproof-Skill für
meinen Agenten und halte den Python-CLI-Checkout verfügbar. Verwende
nur Projektdateien; frage vor dem Ersetzen vorhandener Dateien. Führe
den Offline-Smoke-Test aus und zeige Pfade und Ergebnis. Keine
API-Schlüssel, MCP-Konfiguration, Logo-Anbieter oder Bezahldienste.
```

Für Claude Code, Codex, Cursor, Antigravity und Grok Build (gewöhnlicher Grok Chat garantiert keine lokale Ausführung). Git, Python 3.10+ sowie Datei- und Terminalzugriff werden benötigt. [Genaue Befehle je Agent und Variante ohne Node](INSTALL.md). Keine pip-Installation nötig; Skill und CLI-Checkout behalten. Installation und Offline-CLI sind geprüft, die automatische Erkennung in allen Apps nicht.

## Schnellstart

Im Stammverzeichnis des Repositorys:

```sh
python -m nameproof propose --brief examples/brief.json
python -m nameproof report --brief examples/brief.json --candidates examples/candidates.json --format markdown
python -m nameproof domain example.com --live
python -m nameproof screen --name QuillNest --countries US,EU,VN --classes 9,42
python -m nameproof logo-brief --name QuillNest --brief examples/brief.json
python -m unittest discover -s tests -v
```

Optional lokal installieren: `python -m pip install .`. Eine Veröffentlichung auf PyPI wird nicht behauptet. Standardmäßig offline; `--live` übermittelt die abgefragten Domains an öffentliche IANA/RDAP-Dienste. Keine Käufe oder Markenanmeldungen.

## Funktionen und Grenzen

- Die lokale Ideenbasis nutzt englische Schlüsselwörter und Metaphern. Für kreative mehrsprachige Vorschläge verwenden Sie das Modell Ihres Agenten und übergeben mit `--candidates` eine Liste mit `name` und `rationale`. Der Schreibkomfortwert misst weder inhaltliche Eignung noch Markterfolg oder Rechtssicherheit.
- Das Briefing enthält `idea`, `audience`, `tone`, `keywords`, `countries`, `nice_classes`, `tlds`, `max_length`, `avoid`. Standardländer und -klassen sind ausdrücklich genannte Annahmen. Die Maximallänge ist ein harter Filter; `avoid` schließt normalisierte Teilzeichenfolgen aus.
- RDAP zeigt vorhandene Registrierung, fehlenden Datensatz oder unbekannten Status. Ein fehlender Datensatz bedeutet keine Kaufverfügbarkeit. Quelle, Zeit, Fehler und Ratenbegrenzung bleiben sichtbar. Importierte Registrar-Auskünfte sind unbestätigte Nutzerdaten; älter als 15 Minuten oder mehr als 30 Sekunden in der Zukunft aktualisieren sie den Kaufstatus nicht. Widersprüche werden gemeldet.
- Markenabgleich erfolgt nur gegen tatsächlich übergebene Datensätze. Offizielle manuelle Suchpläne: USA, EU, Großbritannien, Vietnam, China, Deutschland, Russland und Singapur. Unternehmensregister, Internetnutzung und Markenrechte sind getrennte Prüfungen. Ohne Daten ist nichts geprüft; kein Treffer in einer Teilmenge ist keine Freigabe.
- Unicode-Textähnlichkeit ersetzt keine phonetische, begriffliche, bildliche oder transliterierte Prüfung und keine Prüfung sonstiger Rechte. Andere Nizza-Klassen oder inaktive Datensätze schließen Risiken nicht automatisch aus. EU- und deutsche Rechte werden gegenseitig berücksichtigt; weitere nationale EU-Rechte bleiben eine Lücke.
- Konservative eingebaute IDNA-Unterstützung lehnt Umwandlungen ab, die die Schreibweise ändern. Gegebenenfalls die genaue ASCII/Punycode-Form beim Register bestätigen. Keine vollständige IDNA2008-Implementierung.
- `logo-brief` erstellt einen Auftrag, kein Bild. Der gewählte op7418/logo-generator-skill ist versionsgebunden verlinkt, nicht eingebunden oder automatisch ausgeführt. Datenübermittlung, kostenpflichtige Aufrufe und Bildanzahl benötigen eine separate Entscheidung: [LOGO.md](LOGO.md).

## Agenten einbinden

Den gesamten Ordner `skills/nameproof` in das Projekt-Skill-Verzeichnis kopieren und den CLI-Checkout zugänglich halten. Offizielle Formate für Claude Code, Codex, Cursor, Antigravity und Grok Build stehen in [HARNESSES.md](HARNESSES.md). Das ist dokumentierte Formatkompatibilität, keine Ende-zu-Ende-Zertifizierung aller Produkte. Grok Chat ist kein lokales CLI.

`python -m nameproof mcp` stellt vier Werkzeuge über stdio JSON-RPC bereit: Namen, Domains, Markendatensätze und Logo-Briefing. Kein HTTP-Port wird geöffnet; Live-Abfragen müssen ausdrücklich aktiviert werden.

Markendaten benötigen `mark,jurisdiction,classes,source_url,observed_at,record_id,status`; eine URL bestätigt keine Echtheit. WIPO untersagt automatische Abfragen; dieses Tool betreibt kein Scraping. Siehe [Quellen und Alternativen](SOURCES.md). Vor einer folgenreichen Namensnutzung fachkundige Prüfung der relevanten Rechtsgebiete und Registrar-Bestätigung einholen.

MIT gilt nur für den Originalcode dieses Repositorys. CI prüft Python 3.10–3.13; Netzwerktests verwenden simulierte Antworten, echte Beobachtungen werden gesondert ausgewiesen.

## Gewählte Logo-Anweisungen abrufen

`python -m nameproof logo-source --output /path/to/new-directory --fetch` lädt drei Textdateien der festgelegten Version und prüft SHA-256. Das Zielverzeichnis muss neu sein; keine Überschreibung, Skill-Installation oder Skriptausführung. `UPSTREAM_SKILL.md` und Designreferenzen ausdrücklich lesen und mit dem Agenten eigene SVG-Konzepte erstellen. Kostenpflichtige Bilder bleiben separat genehmigungspflichtig. Ohne `--fetch` wird nur das Manifest ausgegeben. Siehe [Beispiel](WALKTHROUGH.md).
