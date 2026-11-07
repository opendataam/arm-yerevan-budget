/* Interface strings shared by every page: French. {name} = placeholder. */
YB.strings("fr", {
  "brand.title": "Budget d'Erevan",
  "brand.subtitle": "maquettes de visualisation",
  "nav.index": "Outils et maquettes",
  "nav.overview": "En bref",
  "nav.treemap": "Où va l'argent",
  "nav.flow": "Flux financiers",
  "nav.execution": "Plan et exécution",
  "nav.districts": "Districts",
  "nav.receipt": "Reçu fiscal",
  "ui.pages": "Maquettes",
  "ui.language": "Langue",
  "ui.show_table": "Afficher le tableau",
  "ui.hide_table": "Masquer le tableau",
  "foot.data": "Données\u00a0: mairie d'Erevan, rubrique Finances (décisions budgétaires et rapports d'exécution du formulaire Հ-9), rassemblées dans DuckDB par opendataam/arm-yerevan-budget. Montants nominaux en AMD.",
  "foot.mockup": "Maquette, pas une publication officielle. Données au {date}.",
  "foot.translation": "Le budget est publié uniquement en arménien\u202f; les noms et l'interface sont traduits avec l'aide de la traduction automatique.",

  /* numbers: {n} is the number already formatted for the language */
  "fmt.na": "n.d.",
  "fmt.amd_bn": "{n}\u00a0Md\u00a0AMD",
  "fmt.amd_m": "{n}\u00a0M\u00a0AMD",
  "fmt.amd_k": "{n}\u00a0k\u00a0AMD",
  "fmt.bn": "{n}\u00a0Md",
  "fmt.m": "{n}\u00a0M",
  "fmt.k": "{n}\u00a0k",
  "fmt.pct": "{n}\u202f%",

  /* execution status */
  "status.good": "Conforme au plan",
  "status.warning": "Léger retard",
  "status.serious": "En retard",
  "status.critical": "Très en retard",

  /* short names of the functional sections (first level of the functional classification) */
  "section.01": "Services généraux",
  "section.02": "Défense",
  "section.03": "Ordre et sécurité publics",
  "section.04": "Affaires économiques",
  "section.05": "Protection de l'environnement",
  "section.06": "Logement et équipements collectifs",
  "section.07": "Santé",
  "section.08": "Loisirs, culture et culte",
  "section.09": "Enseignement",
  "section.10": "Protection sociale",
  "section.11": "Fonds de réserve",

  /* groups of the economic classification (data.js econ_groups) */
  "econ.wages": "Rémunération des salariés",
  "econ.goods": "Biens et services",
  "econ.subsidies": "Subventions aux organisations municipales",
  "econ.other_current": "Dons, prestations sociales et autres dépenses courantes",
  "econ.capital": "Investissements (actifs fixes)",
  "econ.asset_sales": "Vente de terrains et de biens (en déduction)",

  /* revenue groups (data.js revenue[].groups) */
  "rev.real_estate_tax": "Impôt sur les biens immobiliers",
  "rev.vehicle_tax": "Impôt sur les véhicules",
  "rev.local_duties": "Droits locaux (autorisations)",
  "rev.local_fees": "Redevances locales (déchets, stationnement, etc.)",
  "rev.delegated": "Fonds de l'État pour les compétences déléguées",
  "rev.grants": "Dotations du budget de l'État",
  "rev.state_duties": "Droits d'État",
  "rev.other": "Paiements de services, loyers, amendes, autres",

  /* labels of data.js nodes */
  "data.not_itemised": "Non ventilé par programme",
});
