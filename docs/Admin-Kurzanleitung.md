# TipTop Admin: Kurzanleitung

Für Mostafa Khodr und das Team. Stand: 27. November 2026. Der Admin ist unter `/admin/` der Website erreichbar
(bis zum Livegang nur auf dem Entwicklungsrechner).

## Anmelden

- Benutzername und Passwort eingeben. Inhaber und Filialleitung bestätigen danach mit dem Code aus der
  Authenticator-App auf dem Handy (beim ersten Anmelden richten Sie die App ein; dabei gibt es Notfallcodes, bitte
  sicher aufbewahren).
- **Passwort vergessen?** Auf der Anmeldeseite „Passwort vergessen?“ anklicken und die
  E-Mail-Adresse Ihres Kontos eingeben. Sie bekommen einen Link, mit dem Sie ein neues Passwort setzen. Pro Stunde
  gehen höchstens fünf solcher E-Mails raus.
- Passwort ändern: oben rechts „Passwort ändern“.

## Anfragen bearbeiten

**Anfragen und Ankauf → Anfragen** zeigt alles, was über die Website reinkommt: Rückrufe, Reparaturanfragen,
Ankauf mit Fotos und Widerrufe. Neue Anfragen stehen oben.

- **Status setzen:** Anfrage öffnen, Status wählen (Neu, Kontaktiert, Gebucht, In Reparatur, Abholbereit,
  Abgeholt, Verloren mit Grund), speichern. Mehrere auf einmal: anhaken, oben eine Aktion wählen.
- **Kunden per WhatsApp informieren:** In der Liste stehen bei jeder Anfrage mit Telefonnummer zwei grüne Knöpfe,
  „In Bearbeitung“ und „Abholbereit“. Ein Klick öffnet WhatsApp mit dem fertigen Text in der Sprache des Kunden
  („Dein Gerät ist in Bearbeitung.“ / „Dein Gerät ist fertig und kann abgeholt werden.“). Sie müssen nur noch auf
  Senden tippen. Die Texte ändern Sie unter **Inhalte und Medien → Seitentexte** (`wa_status_progress`, `wa_status_ready`).
- **Ankauf mit Fotos:** Die Fotos sehen Sie in der Anfrage. Sie werden nach 30 Tagen automatisch gelöscht, wenn
  kein Ankaufvertrag dazu angelegt wird.

## Preise

- **Preisliste (alle Modelle auf einen Blick):** **Katalog und Preise → Preise → Preisliste (Tabelle)**. Geräteart
  oben wählen (Smartphone, Tablet, Laptop, Konsole), Preise in der Tabelle ändern, unten „Geänderte Preise
  speichern“. Geänderte Felder werden blau. Leeres Feld = „Preis auf Anfrage“, „–“ = gibt es bei diesem Gerät
  nicht. Mit „Alle Reparaturen“ sehen Sie jede Spalte.
- **Ihre Preisliste auf einmal einspielen:** **Preise → Import** (CSV oder Excel). Am einfachsten zuerst
  **Export** herunterladen, in Excel ausfüllen und wieder importieren. Sie sehen vorher eine Vorschau.
- **Ein Gerät einzeln:** **Preise → Preisübersicht (bearbeiten)**, Gerät links wählen.
- Jede Änderung steht in der Historie und lässt sich zurücknehmen. Wenn die echten Preise drin sind: unter
  **Website und Einstellungen → Einstellungen** „Preise sind Platzhalter“ ausschalten.

## Geräte

**Katalog und Preise → Geräte**

- **Neues Gerät:** „Gerät hinzufügen“, Kategorie, Marke, Modellname und Preisstufe wählen. Darunter:
  - **Schalter** Face ID, Touch ID und Kopfhörerbuchse: was das Gerät hat. Reparaturen wie „Face ID Reparatur“
    erscheinen nur bei Geräten mit dem passenden Schalter.
  - **Reparaturen:** Haken setzen bei allem, was Sie für dieses Gerät anbieten. Leer lassen = alle Reparaturen,
    die es für diese Geräteart gibt. Ein Haken bei einer Reparatur einer anderen Geräteart fügt sie nur für dieses
    Gerät hinzu.
  - Beim Speichern werden Startpreise aus der Preisstufe berechnet; danach in der Preisliste anpassen. Das Gerät
    hat sofort eine eigene Seite auf der Website.
- **Gerät ausblenden:** „Aktiv“ ausschalten (Historie bleibt). **Gerät löschen:** Gerät öffnen, unten „Löschen“
  (nur Inhaber). Dabei werden seine Preise mit gelöscht.

## Reparaturarten

**Katalog und Preise → Reparaturarten**

- **Neue Reparatur oder Kombination** (z. B. „Backcover + Display“): „Reparaturart hinzufügen“, Name Deutsch
  und Englisch, Symbol, dann unten:
  - **Für welche Geräte?** eine Zeile je Geräteart (bei Konsolen je Konsolentyp). Unter „Bedingung“ können Sie
    sie auf Geräte mit Face ID, Touch ID oder Kopfhörerbuchse beschränken.
  - **Grundpreise:** ein Preis je Geräteart. Daraus berechnet die Website beim Speichern Startpreise für alle
    passenden Geräte.
- **Premium und Original:** Haken = zwei Preise (Premium-Teil und Original-Teil). Ausschalten macht den
  Premium-Preis zum einzigen Preis; Einschalten übernimmt den bisherigen Preis für beide Teile.
- **Reparatur nur bei einer Geräteart entfernen** (z. B. bei Tablets): Reparaturart öffnen, die Zeile dieser
  Geräteart unter „Für welche Geräte?“ löschen.
- **Ganz löschen** (z. B. „Fehlerdiagnose“): Reparaturart öffnen, „Löschen“. Ihre Preise werden mit gelöscht.
  Ohne Fehlerdiagnose verschwindet auch der Knopf „Nicht sicher?“ im Preisrechner.

## Fotos und Film

- **Fotos:** **Inhalte und Medien → Mediathek**. Ein Foto ersetzen: Eintrag öffnen (z. B. `shop-moabit`, `rep-display`,
  `before`), neues Bild hochladen, speichern. Die Website erzeugt Handy- und Desktopgrößen selbst. Bitte bei
  echten Fotos „KI-generiert“ ausschalten.
- **Film:** **Website und Einstellungen → Einstellungen**: „Video im Kopfbereich“ (4:5, stumm, für Computer) und „Film für Handys und
  Tablets“ (9:16 mit Ton, hinter dem Knopf „Film ansehen“). Wenn Sie den Computer-Film austauschen, bitte auch das
  erste Bild ersetzen (Mediathek, Eintrag `hero-film`), sonst springt das Bild beim Start.

## Texte, Öffnungszeiten, Rechtstexte

- **Inhalte und Medien → Seitentexte:** alle Texte der Website in Deutsch und Englisch.
- **Filialen und Öffnungszeiten** (gleichnamiger Bereich): normale Zeiten, Sonderöffnungszeiten (z. B. Heiligabend) und Feiertage. Die
  Anzeige „Jetzt geöffnet“ richtet sich danach.
- **Rechtstexte und Einwilligungen → Rechtstexte:** bitte nur nach Rücksprache mit Ihrem Anwalt ändern. Jede Fassung wird gespeichert.
