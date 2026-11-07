/* Interface strings shared by every page: Spanish. {name} = placeholder. */
YB.strings("es", {
  "brand.title": "Presupuesto de Ereván",
  "brand.subtitle": "maquetas de visualización",
  "nav.index": "Herramientas y maquetas",
  "nav.overview": "De un vistazo",
  "nav.treemap": "A dónde va el dinero",
  "nav.flow": "Flujo del dinero",
  "nav.execution": "Plan y ejecución",
  "nav.districts": "Distritos",
  "nav.receipt": "Recibo de impuestos",
  "ui.pages": "Maquetas",
  "ui.language": "Idioma",
  "ui.show_table": "Mostrar tabla",
  "ui.hide_table": "Ocultar tabla",
  "foot.data": "Datos: Alcaldía de Ereván, sección de Finanzas (decisiones presupuestarias e informes de ejecución del formulario Հ-9), recopilados en DuckDB por opendataam/arm-yerevan-budget. Importes nominales en AMD.",
  "foot.mockup": "Maqueta, no es una publicación oficial. Datos a {date}.",
  "foot.translation": "El presupuesto se publica solo en armenio; los nombres y la interfaz son traducciones realizadas con ayuda de traducción automática.",

  /* numbers: {n} is the number already formatted for the language */
  "fmt.na": "n/d",
  "fmt.amd_bn": "{n}\u00a0mil\u00a0M\u00a0AMD",
  "fmt.amd_m": "{n}\u00a0M\u00a0AMD",
  "fmt.amd_k": "{n}\u00a0mil\u00a0AMD",
  "fmt.bn": "{n}\u00a0mil\u00a0M",
  "fmt.m": "{n}\u00a0M",
  "fmt.k": "{n}\u00a0mil",
  "fmt.pct": "{n}\u00a0%",

  /* execution status */
  "status.good": "Según el plan",
  "status.warning": "Leve retraso",
  "status.serious": "Con retraso",
  "status.critical": "Muy retrasado",

  /* short names of the functional sections (first level of the functional classification) */
  "section.01": "Servicios públicos generales",
  "section.02": "Defensa",
  "section.03": "Orden público y seguridad",
  "section.04": "Asuntos económicos",
  "section.05": "Protección del medio ambiente",
  "section.06": "Vivienda y servicios comunitarios",
  "section.07": "Salud",
  "section.08": "Recreación, cultura y religión",
  "section.09": "Educación",
  "section.10": "Protección social",
  "section.11": "Fondos de reserva",

  /* groups of the economic classification (data.js econ_groups) */
  "econ.wages": "Remuneración de los empleados",
  "econ.goods": "Bienes y servicios",
  "econ.subsidies": "Subsidios a organizaciones municipales",
  "econ.other_current": "Donaciones, prestaciones sociales y otros gastos corrientes",
  "econ.capital": "Inversión de capital (activos fijos)",
  "econ.asset_sales": "Venta de terrenos y bienes (deducción)",

  /* revenue groups (data.js revenue[].groups) */
  "rev.real_estate_tax": "Impuesto sobre bienes inmuebles",
  "rev.vehicle_tax": "Impuesto sobre la propiedad de vehículos",
  "rev.local_duties": "Tasas locales (permisos)",
  "rev.local_fees": "Cargos locales (residuos, estacionamiento, etc.)",
  "rev.delegated": "Fondos estatales para competencias delegadas",
  "rev.grants": "Donaciones del presupuesto del Estado",
  "rev.state_duties": "Tasas estatales",
  "rev.other": "Pagos por servicios, alquileres, multas, otros",

  /* labels of data.js nodes */
  "data.not_itemised": "Sin desglose por programa",
});
