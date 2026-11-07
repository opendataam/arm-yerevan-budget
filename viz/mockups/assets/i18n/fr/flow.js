/* Interface strings of flow.html: French. {name} = placeholder; values with <b> are HTML. */
YB.strings("fr", {
  "flow.title": "Flux financiers du budget d'Erevan",
  "flow.h1": "Des recettes aux dépenses",
  "flow.lede": "Suivez l'argent\u00a0: d'où vient le budget de la ville, et quelles fonctions et quels services il finance. La largeur des bandes est proportionnelle aux montants.",
  "flow.pattern": "<b>Modèle\u00a0:</b> vue d'accueil en flux (Sankey), comme dans Open Budget Oakland / Sacramento, Civio Presupuesto et le Data Lab d'USAspending",
  "flow.f_year": "Année",
  "flow.year_actual": "{year} (exécution)",
  "flow.year_approved": "{year} (approuvé)",
  "flow.revenue_actual": "Recettes, exécution effective",
  "flow.revenue_approved": "Recettes, budget approuvé",
  "flow.spending_actual": "Dépenses, exécution effective",
  "flow.spending_approved": "Dépenses, budget approuvé",
  "flow.surplus": "Excédent",
  "flow.deficit": "Déficit",
  "flow.col_sources": "Sources",
  "flow.col_budget": "Budget",
  "flow.col_functions": "Fonctions",
  "flow.col_services": "Principaux services",
  "flow.chart_aria": "Diagramme de Sankey des sources de recettes, via le budget de la ville, vers les fonctions et les services",

  /* names of the nodes of the diagram */
  "flow.hub": "Budget de la ville {year}",
  "flow.asset_sales": "Vente de terrains et de biens",
  "flow.deficit_financing": "Financement du déficit",
  /* {name} = the function, {lname} = the same name in lower case */
  "flow.other_in_section": "Autres ({lname})",
  "flow.other_functions": "Autres fonctions",
  "flow.unspent": "Non dépensé (excédent)",

  /* short names of some sub-functions (functional classification codes 01.1.1 etc.) */
  "flow.short_01_1_1": "Organes exécutifs et administration",
  "flow.short_04_1_1": "Affaires économiques générales",
  "flow.short_04_5_5": "Métro, ascenseurs et autres transports",
  "flow.short_04_9_1": "Affaires économiques n.c.a.",
  "flow.short_05_6_1": "Protection de l'environnement n.c.a.",
  "flow.short_09_6_1": "Services annexes à l'enseignement",
  "flow.short_06_6_1": "Logement et équipements collectifs n.c.a.",

  "flow.tip_edge": "{from} → {to}",
  "flow.tip_share": "{pct} du total",
  "flow.col_from": "Origine",
  "flow.col_to": "Destination",
  "flow.col_amd": "AMD",
  /* {source} = flow.source_report or flow.source_decision */
  "flow.read_note": "<b>Comment lire\u00a0:</b> {source} Les ventes de terrains et de biens ({asset}) figurent dans les documents sources comme des dépenses négatives\u202f; elles sont ici présentées comme une source, si bien que «\u00a0Affaires économiques\u00a0» apparaît en montant brut. Les «\u00a0Fonds de l'État pour les compétences déléguées\u00a0» financent les tâches que l'État confie à la ville, comme le métro et les écoles.",
  "flow.source_report": "Rapport annuel d'exécution {year}.",
  "flow.source_decision": "Décision budgétaire du Conseil des anciens pour {year}.",
  "flow.other_note": "<b>Autres fonctions</b> regroupe la santé, la défense, l'ordre public et les fonds de réserve.",
});
