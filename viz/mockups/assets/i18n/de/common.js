/* Interface strings shared by every page: German. {name} = placeholder. */
YB.strings("de", {
  "brand.title": "Haushalt Jerewan",
  "brand.subtitle": "Visualisierungs-Mock-ups",
  "nav.index": "Werkzeuge und Mock-ups",
  "nav.overview": "Auf einen Blick",
  "nav.treemap": "Wohin das Geld fließt",
  "nav.flow": "Geldfluss",
  "nav.execution": "Plan vs. Ist",
  "nav.districts": "Bezirke",
  "nav.receipt": "Steuerquittung",
  "ui.pages": "Mock-ups",
  "ui.language": "Sprache",
  "ui.show_table": "Tabelle anzeigen",
  "ui.hide_table": "Tabelle ausblenden",
  "foot.data": "Daten: Stadtverwaltung Jerewan, Abteilung Finanzen (Haushaltsbeschlüsse und Vollzugsberichte nach Formular Հ-9), in DuckDB zusammengeführt von opendataam/arm-yerevan-budget. Beträge nominal in AMD.",
  "foot.mockup": "Mock-up, keine amtliche Veröffentlichung. Datenstand {date}.",
  "foot.translation": "Der Haushalt wird nur auf Armenisch veröffentlicht; Namen und Oberfläche sind maschinengestützte Übersetzungen.",

  /* numbers: {n} is the number already formatted for the language */
  "fmt.na": "k. A.",
  "fmt.amd_bn": "{n} Mrd. AMD",
  "fmt.amd_m": "{n} Mio. AMD",
  "fmt.amd_k": "{n} Tsd. AMD",
  "fmt.bn": "{n} Mrd.",
  "fmt.m": "{n} Mio.",
  "fmt.k": "{n} Tsd.",
  "fmt.pct": "{n} %",

  /* execution status */
  "status.good": "Im Plan",
  "status.warning": "Leicht zurück",
  "status.serious": "Im Rückstand",
  "status.critical": "Weit zurück",

  /* short names of the functional sections (first level of the functional classification) */
  "section.01": "Allgemeine öffentliche Verwaltung",
  "section.02": "Verteidigung",
  "section.03": "Öffentliche Ordnung und Sicherheit",
  "section.04": "Wirtschaftliche Angelegenheiten",
  "section.05": "Umweltschutz",
  "section.06": "Wohnungsbau und kommunale Einrichtungen",
  "section.07": "Gesundheitswesen",
  "section.08": "Freizeit, Kultur und Religion",
  "section.09": "Bildungswesen",
  "section.10": "Soziale Sicherung",
  "section.11": "Reservefonds",

  /* groups of the economic classification (data.js econ_groups) */
  "econ.wages": "Arbeitnehmerentgelt",
  "econ.goods": "Waren und Dienstleistungen",
  "econ.subsidies": "Subventionen an städtische Einrichtungen",
  "econ.other_current": "Zuschüsse, Sozialleistungen und sonstige laufende Ausgaben",
  "econ.capital": "Investitionen (Anlagegüter)",
  "econ.asset_sales": "Verkauf von Grundstücken und Immobilien (verrechnet)",

  /* revenue groups (data.js revenue[].groups) */
  "rev.real_estate_tax": "Immobiliensteuer",
  "rev.vehicle_tax": "Vermögensteuer auf Fahrzeuge",
  "rev.local_duties": "Örtliche Abgaben (Genehmigungen)",
  "rev.local_fees": "Örtliche Gebühren (Abfall, Parken usw.)",
  "rev.delegated": "Staatsmittel für übertragene Befugnisse",
  "rev.grants": "Zuschüsse aus dem Staatshaushalt",
  "rev.state_duties": "Staatsgebühren",
  "rev.other": "Entgelte für Leistungen, Mieten, Bußgelder, Sonstiges",

  /* labels of data.js nodes */
  "data.not_itemised": "Nicht nach Programmen aufgeschlüsselt",
});
