/* Interface strings shared by every page: Portuguese (Brazil). {name} = placeholder. */
YB.strings("pt", {
  "brand.title": "Orçamento de Erevan",
  "brand.subtitle": "protótipos de visualização",
  "nav.index": "Ferramentas e protótipos",
  "nav.overview": "Visão geral",
  "nav.treemap": "Para onde vai o dinheiro",
  "nav.flow": "Fluxo do dinheiro",
  "nav.execution": "Previsto x realizado",
  "nav.districts": "Distritos",
  "nav.receipt": "Recibo de impostos",
  "ui.pages": "Protótipos",
  "ui.language": "Idioma",
  "ui.show_table": "Mostrar tabela",
  "ui.hide_table": "Ocultar tabela",
  "foot.data": "Dados: Prefeitura de Erevan, seção de Finanças (decisões orçamentárias e relatórios de execução do formulário Հ-9), reunidos em DuckDB por opendataam/arm-yerevan-budget. Valores nominais em AMD.",
  "foot.mockup": "Protótipo, não é uma publicação oficial. Dados extraídos em {date}.",
  "foot.translation": "O orçamento é publicado apenas em armênio; os nomes e a interface são traduções assistidas por máquina.",

  /* numbers: {n} is the number already formatted for the language */
  "fmt.na": "n/d",
  "fmt.amd_bn": "AMD {n} bi",
  "fmt.amd_m": "AMD {n} mi",
  "fmt.amd_k": "AMD {n} mil",
  "fmt.bn": "{n} bi",
  "fmt.m": "{n} mi",
  "fmt.k": "{n} mil",
  "fmt.pct": "{n}%",

  /* execution status */
  "status.good": "Dentro do plano",
  "status.warning": "Abaixo do ritmo",
  "status.serious": "Atrasado",
  "status.critical": "Muito atrasado",

  /* short names of the functional sections (first level of the functional classification) */
  "section.01": "Serviços públicos gerais",
  "section.02": "Defesa",
  "section.03": "Ordem pública e segurança",
  "section.04": "Assuntos econômicos",
  "section.05": "Proteção do meio ambiente",
  "section.06": "Habitação e serviços comunitários",
  "section.07": "Saúde",
  "section.08": "Lazer, cultura e religião",
  "section.09": "Educação",
  "section.10": "Proteção social",
  "section.11": "Fundos de reserva",

  /* groups of the economic classification (data.js econ_groups) */
  "econ.wages": "Remuneração dos empregados",
  "econ.goods": "Bens e serviços",
  "econ.subsidies": "Subsídios a organizações municipais",
  "econ.other_current": "Doações, benefícios sociais e outras despesas correntes",
  "econ.capital": "Investimentos de capital (ativos fixos)",
  "econ.asset_sales": "Venda de terrenos e imóveis (dedução)",

  /* revenue groups (data.js revenue[].groups) */
  "rev.real_estate_tax": "Imposto sobre bens imóveis",
  "rev.vehicle_tax": "Imposto sobre a propriedade de veículos",
  "rev.local_duties": "Taxas locais (autorizações)",
  "rev.local_fees": "Tarifas locais (lixo, estacionamento etc.)",
  "rev.delegated": "Recursos do Estado para competências delegadas",
  "rev.grants": "Doações do orçamento do Estado",
  "rev.state_duties": "Taxas estatais",
  "rev.other": "Pagamentos por serviços, aluguéis, multas, outros",

  /* labels of data.js nodes */
  "data.not_itemised": "Sem detalhamento por programa",
});
