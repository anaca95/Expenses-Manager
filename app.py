from datetime import datetime
from pathlib import Path
from uuid import uuid4
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
import gspread
import unicodedata
import re
from dash import (
    Dash,
    Input,
    Output,
    State,
    callback,
    ctx,
    dash_table,
    dcc,
    html,
    no_update,
)



gc = gspread.service_account(r"C:\Users\anaca\Documents\DOOWON SYSTEM\API_Key.json")
PDF_BASE_PATH = r"C:\Users\anaca\Documents\Vertical"
spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1ccJ671pRqG2UAy54-QHjBnMcTdmm55pNgYcLvJrtA04/edit?usp=sharing")
IMAGE_folder = Path(r"C:\Users\anaca\Documents\Vertical")
FOLHA_EVENTOS = "DESPESAS"

# ============================================================
# APP CONFIGURATION
# ============================================================

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
)

app.title = "Registros de Despesas"



# ============================================================
# MAIN APP LAYOUT
# ============================================================

app.layout = dbc.Container(
    [
        # Controls the selected URL/page
        dcc.Location(
            id="url",
            refresh=False,
        ),


        dbc.Row(
            [
                # --------------------------------------------
                # LEFT-SIDE MENU
                # --------------------------------------------
                dbc.Col(
                    html.Aside(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        "S",
                                        className="logo",
                                    ),

                                    html.Div(
                                        [
                                            html.H4("SISTEMA"),
                                            html.P("DESPESAS DOMÉSTICAS"),
                                        ]
                                    ),
                                ],
                                className="brand",
                            ),

                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        "INÍCIO",
                                        href="/",
                                        id="home-link",
                                    ),
                                    dbc.NavLink(
                                        "CADASTRO FISCAL",
                                        href="/cadastroFiscal",
                                        active="exact",
                                    ),
                                ],
                                vertical=True,
                                pills=True,
                                className="sidebar-nav",
                            ),
                        ],
                        className="sidebar",
                    ),

                    width=2,
                    className="sidebar-column",
                ),

                # --------------------------------------------
                # PAGE CONTENT
                # --------------------------------------------
                dbc.Col(
                    html.Main(
                        id="page-content",
                        className="page-content",
                    ),

                    width=10,
                ),
            ],
            className="g-0",
        ),
    ],

    fluid=True,
    className="app-container",
)


TIPO_DESPESAS = ["HIGIENE PESSOAL", "ALIMENTAÇÃO", "FARMÁCIA", "LIMPEZA", "VESTUÁRIO E ACESSÓRIOS","DELIVERY", "OUTROS"]

# ============================================================
# PAGE NAVIGATION
# ============================================================

@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if pathname in ("/", "/main"):
        return html.Div(
    [
        html.H2("OVERVIEW DAS DESPESAS"),
        home_month_filter(),

        html.Br(),

        html.H3("Gastos por item"),

        dcc.Dropdown(
            id="expense-type-selector",
            options=[
                {"label": "🍽️ Alimentação", "value": "ALIMENTACAO"},
                {"label": "💊 Farmácia", "value": "FARMACIA"},
                {"label": "🧴 Higiene pessoal", "value": "HIGIENE PESSOAL"},
                {"label": "🧴 Vestuário e acessórios", "value": "VESTUÁRIO E ACESSÓRIOS"},
                {"label": "📦 Delivery", "value": "DELIVERY"},
                {"label": "📦 Outros", "value": "OUTROS"},
            ],
            value="ALIMENTACAO",
            clearable=False,
            placeholder="Selecione um tipo de despesa",
        ),

        html.Div(
            id="expense-items-cards",
            className="expense-cards-container",
        ),

        html.Hr(),
        html.H3("Previsão: dias úteis × fim de semana"),
        html.P(
            "Estimativa baseada na frequência e no valor dos gastos "
            "da categoria selecionada."
        ),

        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        id="weekday-forecast-card",
                        className="card p-3 h-100",
                    ),
                    md=4,
                ),
                dbc.Col(
                    html.Div(
                        id="weekend-forecast-card",
                        className="card p-3 h-100",
                    ),
                    md=4,
                ),
                dbc.Col(
                    html.Div(
                        id="monthly-forecast-card",
                        className="card p-3 h-100",
                    ),
                    md=4,
                ),
            ],
            className="g-3 mb-3",
        ),

        dcc.Graph(id="weekday-weekend-forecast"),
        html.Small(
            id="forecast-method-note",
            className="text-muted",
        ),
    ],
    className="expense-summary-section",
)

    if pathname == "/cadastroFiscal":
        return html.Div(
            [
                html.H2("CADASTRO DE ITENS"),
                # Add input fields
                html.Div([
                    html.Label("CADASTRO DE ITENS"),
                    html.Br(),
                ]),
                    html.Div([
                    dcc.Input(
                        id="nome-do-item",
                        placeholder="INSIRA O NOME DO ITEM",
                        style={"width": "60%"},
                    )]),


                html.Div([
                    html.Label("QUANTIDADE"),
                    html.Br()]),
                    html.Div([
                    dcc.Input(
                        id="qtd-item",
                        type="number",
                        style={"width": "300px"},
                    )]),

                html.Div([
                    html.Label("PREÇO"),
                    html.Br()]),
                html.Div([
                    dcc.Input(
                        id="preco-item",
                        type="number",
                        style={"width": "60%"},
                    )]),


                html.Div(
                    [
                        html.Label("TIPO DA DESPESA"),
                        html.Br(),
                    ]),

                        html.Div([
                        dcc.Dropdown(
                            id="despesas-dropdown",
                            options=[
                                {
                                    "label": evento,
                                    "value": evento,
                                }
                                for evento in TIPO_DESPESAS
                            ],
                            placeholder="SELECIONE",
                            clearable=True,
                            searchable=False,
                            style={"width": "60%"},
                        )]),

                html.Br(),
                html.Div([
                    html.Button(
                        "REGISTRAR ITEM",
                        id="register-button",
                        n_clicks=0,
                        disabled=False,

                    ),
                ]),
                html.Br(),
                html.Div(
                    [
                        dcc.Loading(
                            id="loading-table1",
                            type="default",
                            overlay_style={
                                "visibility": "visible",
                                "filter": "blur(2px)",
                            },
                            children=[
                                dash_table.DataTable(
                                    id="dash_table1",
                                    columns=[],
                                    data=[],
                                    page_size=15,
                                    sort_action="native",
                                    filter_action="native",
                                    style_table={
                                        "overflowX": "auto",
                                        "width": "100%",
                                    },
                                    style_header={
                                        "backgroundColor": "#0f4c81",
                                        "color": "#ffffff",
                                        "fontWeight": "700",
                                        "border": "none",
                                        "padding": "12px",
                                        "textAlign": "center",
                                    },
                                    style_cell={
                                        "backgroundColor": "#ffffff",
                                        "color": "#334155",
                                        "border": "1px solid #e2e8f0",
                                        "padding": "10px",
                                        "textAlign": "center",
                                        "fontFamily": (
                                            "Segoe UI, sans-serif"
                                        ),
                                        "fontSize": "13px",
                                        "minWidth": "110px",
                                        "width": "110px",
                                        "maxWidth": "220px",
                                        "whiteSpace": "normal",
                                    },

                                ),
                            ],
                        ),
                    ],
                    # className="apontamento-table-body",
                ),

                html.Div(
                    [
                        html.P("Total gasto", id="total-mensal-label"),
                        html.H3("R$ 0,00", id="total-mensal"),
                    ],
                    className="card",
                ),
                dcc.Dropdown(
                    id="grafico-expense-filter",
                    options=[
                        {"label": "Todas as despesas", "value": "TODAS"},
                        {"label": "🍽️ Alimentação", "value": "ALIMENTACAO"},
                        {"label": "💊 Farmácia", "value": "FARMACIA"},
                        {"label": "🧴 Higiene pessoal", "value": "HIGIENE PESSOAL"},
                        {"label": "📦 Outros", "value": "OUTROS"},
                    ],
                    value="TODAS",
                    clearable=False,
                    placeholder="Selecione o tipo de despesa",
                    className="expense-plot-filter",
                ),

                html.Label("Mês do resumo e dos gráficos", htmlFor="grafico-month-filter"),
                dcc.Dropdown(
                    id="grafico-month-filter",
                    options=[{"label": "Todos os meses", "value": "TODOS"}],
                    value="TODOS",
                    clearable=False,
                    className="expense-plot-filter",
                ),
                dcc.Graph(id="grafico-data"),
                dcc.Graph(id="grafico-despesas"),


            ],
            className="card",
        )




# ============================================================
# REGISTER, CLEAR FIELDS AND CLEAR TABLE
# ============================================================

############### ABA 1 ###########################
@callback(Output("home-link", "active"), Input("url", "pathname"))
def highlight_home(pathname):
    return pathname in ("/", "/main")


def date_matches_month(value, selected_month):
    if not selected_month or selected_month == "TODOS":
        return True
    date = pd.to_datetime(value, dayfirst=True, errors="coerce")
    return pd.notna(date) and date.strftime("%Y-%m") == selected_month


def home_month_filter():
    values = spreadsheet.worksheet(FOLHA_EVENTOS).get("A1:E")
    data = [{"DATA": row[0]} for row in values[1:] if row]
    current_month = datetime.now().strftime("%Y-%m")
    options, _ = update_plot_months(data, current_month)
    if not any(option["value"] == current_month for option in options):
        options.insert(1, {"label": datetime.now().strftime("%m/%Y"), "value": current_month})
    return html.Div([
        html.Label("Mês do resumo", htmlFor="home-month-filter"),
        dcc.Dropdown(id="home-month-filter", options=options,
                     value=current_month, clearable=False),
    ], className="mb-3")


@callback(
    Output("total-mensal", "children"),
    Output("total-mensal-label", "children"),
    Input("dash_table1", "data"),
    Input("grafico-month-filter", "value"),
)
def update_month_total(data, selected_month):
    total = 0.0
    for row in data or []:
        if date_matches_month(row.get("DATA", ""), selected_month):
            try:
                total += parse_currency(row.get("PREÇO"))
            except (ValueError, TypeError):
                continue
    label = (
        f"Total gasto em {selected_month[5:]}/{selected_month[:4]}"
        if selected_month and selected_month != "TODOS"
        else "Total gasto em todos os meses"
    )
    return format_brl(total), label


def normalize_text(value):
    value = str(value or "").strip().upper()

    return "".join(
        character
        for character in unicodedata.normalize("NFD", value)
        if unicodedata.category(character) != "Mn"
    )


def format_brl(value):
    return (
        f"R$ {value:,.2f}"
        .replace(",", "_")
        .replace(".", ",")
        .replace("_", ".")
    )


# Aliases are matched at the start of the item name, on whole words.
# Add variations to the tuples below; the longest matching alias wins.
ITEM_ALIASES = {
    "COXINHA": ("COXINHA DE FRANGO", "COXINHA"),
    "FAROFA": ("FAROFA", "FAROFA ESPECIAL"),
    "SALADA": ("SALADA","SALADA MIX", "SALADA MIX VERAO", "SALADA MIX PRIMAVERA"),
    "ARROZ": ("ARROZ","ARROZ A GREGA", "ARROZ INTEGRAL"),
    "FEIJÃO": ("FEIJAO",),
    "PÃO": ("PAO FRANCES", "BISNAGUINHA", "BISNAGUINHAS"),
    "CERVEJA": ("CERVEJA",),
    "REFRIGERANTE": ("REFRIGERANTE", "COCA COLA", "SUKITA", "REFRIG 2L"),
    "FRANGO": ("FILE DE FRANGO", "FILE DE PEITO", "PEITO DE FRANGO", "PEITO FRANGO", "FRANGO", "PARMEGIANA DE FRANGO"),
    "PEITO DE FRANGO (FATIADOS)": ("PEITO DE FRANGO FATIADO", "PEITO FRANGO FATIADO", "PEITO DE FRANGO FATIADOS", "PEITO FRANGO FATIADOS", "FRANGO FATIADO", "FRANGO FATIADOS"),
    "PEIXE": ("FILE DE MERLUZA", "MERLUZA"),
    "MACARRÃO INSTANTÂNEO": ("MACARRAO NISSIN", "MACARRAO INSTANTANEO", "MIOJO"),
    "MACARRÃO": ("MACARRAO","MACARRAO A BOLONHESA"),
    "MASSAS": ("CANELONE", "LASANHA", "NHOQUE", "PANQUECA"),
    "MANDIOCA": ("MANDIOCA", "PURE DE MANDIOCA", "MANDIOCA FRITA"),
    "BATATA": ("BATATA FRITA", "BATATA RUSTICA"),
    "BATATA-DOCE": ("BATATA DOCE",),
    "CUSCUZ": ("CUSCUZ", "CUSCUZ FRANGO"),
    "LEGUMES SALTEADOS": ("LEGUMES SALTEADOS",),
    "LANCHE": ("LANCHE",),
    "PIZZA": ("PIZZA",),
    "BANANA": ("BANANA",),
    "OVOS": ("OVO", "OVOS"),
    "BISCOITO": ("BISCOITO", "BISCOITOS"),
    "LEITE": ("LEITE INTEGRAL", "LEITE DESNATADO", "LEITE SEMIDESNATADO"),
    "BEBIDA LÁCTEA": ("BEBIDA LACTEA",),
    "ACHOCOLATADO PRONTO": ("TODDYNHO", "NESCAU 1L", "NESCAU 1 L"),
    "ACHOCOLATADO": ("ACHOC NESCAU", "ACHOCOLATADO"),
    "IOGURTE": ("IOGURTE",),
    "QUEIJO FATIADO": ("MUSSARELA FATIADA", "MUCARELA FATIADA", "QUEIJO FATIADO", "QUEIJO"),
    "CEREAL MATINAL": ("CEREAL MAT", "CEREAL MATINAL", "CER NESTLE", "SUCRILHOS"),
    "BARRA DE CEREAL": ("BARRA CEREAL", "BARRA DE CEREAL"),
    "MOLHO DE TOMATE": ("MOLHO TOMATE", "MOLHO DE TOMATE"),
    "CAFÉ": ("PO DE CAFE", "CAFE EM PO"),
    "AÇÚCAR": ("ACUCAR",),
    "SHAMPOO": ("SHAMPOO", "SH JJ BABY"),
    "DESODORANTE": ("DESODORANTE",),
    "SABONETE": ("SABONETE",),
    "PASTA DE DENTE": ("SENSODYNE", "PASTA DE DENTE", "CREME DENTAL"),
    "PROTETOR DIÁRIO": ("CAREFREE", "ABS CAREFREE"),
    "LENÇO DE PAPEL": ("LENCO DE PAPEL", "LENCOS PAPEL", "LENCOS DE PAPEL"),
    "HIDRATANTE CORPORAL": ("LOC HID NEUTROGENA", "LOCAO HIDRATANTE NEUTROGENA"),
    "ESMALTE": ("ESMALTE", "ESMALTES"),
    "WHEY": ("SUPER WHEY", "WHEY"),
    "WHEY BARRA": ("BARRA WHEY", "BARRA DE WHEY", "WHEY BARRA"),
    "CREATINA": ("CREATINA",),
    "PILHA": ("PILHA", "PILHAS"),
    "LÂMPADA": ("LAMP", "LAMPADA"),
    "TÊNIS": ("TENIS",),
    "COPO DESCARTÁVEL": ("COPO DESCARTAVEL", "COPOS DESCARTAVEIS"),
}


def normalize_item_alias(value):
    # Ignore accents, punctuation and repeated whitespace only for matching.
    return " ".join(re.sub(r"[^A-Z0-9]+", " ", normalize_text(value)).split())


def get_item_group(item_name):
    name = normalize_item_alias(item_name)
    best_group = None
    best_length = -1
    for group_name, aliases in ITEM_ALIASES.items():
        for alias in (group_name, *aliases):
            key = normalize_item_alias(alias)
            if (name == key or name.startswith(key + " ")) and len(key) > best_length:
                best_group = group_name
                best_length = len(key)
    return best_group or " ".join(str(item_name or "").strip().split())


def get_item_emoji(item_name):
    name = normalize_text(item_name)

    emoji_rules = [
        # Drinks
        ("CERVEJA", "🍺"),
        ("REFRIGERANTE", "🥤"),
        ("COCA COLA", "🥤"),
        ("SUKITA", "🥤"),
        ("AGUA DE COCO", "🥥"),
        ("AGUA MINERAL", "💧"),
        ("SUCO DE UVA", "🍇"),
        ("LEITE", "🥛"),
        ("BEBIDA LACTEA", "🥛"),
        ("IOGURTE", "🥣"),
        ("ACHOC", "🍫"),
        ("NESCAU", "🍫"),

        # Bakery and snacks
        ("PAO FRANCES", "🥖"),
        ("BISNAGUINHA", "🍞"),
        ("BISCOITO", "🍪"),
        ("COXINHA", "🥟"),
        ("LANCHE", "🥪"),
        ("PIZZA", "🍕"),
        ("CANELONE", "🍝"),

        # Fruit and vegetables
        ("BANANA", "🍌"),
        ("SALADA", "🥗"),
        ("BATATA", "🥔"),
        ("MANDIOCA", "🥔"),
        ("PURE", "🥔"),
        ("REFOGADO", "🥘"),

        # Meat, fish and eggs
        ("FILE DE MERLUZA", "🐟"),
        ("MERLUZA", "🐟"),
        ("PEIXE", "🐟"),
        ("CUSCUZ FRANGO", "🌽"),
        ("MAIONESE FRANGO", "🥗"),
        ("PEITO DE FRANGO", "🍗"),
        ("FILE DE FRANGO", "🍗"),
        ("FILE DE PEITO", "🍗"),
        ("FRANGO", "🍗"),
        ("OVOS", "🥚"),

        # Grains and prepared food
        ("MACARRAO", "🍝"),
        ("ARROZ", "🍚"),
        ("FEIJAO", "🫘"),
        ("FAROFA", "🥣"),
        ("CUSCUZ", "🌽"),
        ("CEREAL", "🥣"),
        ("CER NESTLE", "🥣"),
        ("NESFIT", "🥣"),

        # Dairy
        ("MUSSARELA", "🧀"),
        ("CREME DE RICOTA", "🧀"),
        ("REQUEIJAO", "🧀"),
        ("RICOTA", "🧀"),
        ("QUEIJO", "🧀"),

        # Pantry
        ("ACUCAR", "🧂"),

        # Supplements and medicines
        ("SUPER WHEY", "💪"),
        ("BARRA WHEY", "💪"),
        ("WHEY", "💪"),
        ("CREATINA", "💪"),
        ("DIPIRONA", "💊"),
        ("TORSILAX", "💊"),
        ("LUFTAL", "💊"),

        # Hygiene and personal care
        ("PAPEL HIGIENICO", "🧻"),
        ("SENSODYNE", "🪥"),
        ("SABONETE", "🧼"),
        ("SHAMPOO", "🧴"),
        ("DESODORANTE", "🧴"),
        ("CAREFREE", "🩹"),
        ("KERATON", "💇"),
        ("POMADA CAPICILIN", "💇"),
        ("ESMALTE", "💅"),

        # Clothing and household
        ("TENIS", "👟"),
        ("PILHA", "🔋"),
        ("LAMP", "💡"),
        ("LED", "💡"),
    ]

    for keyword, emoji in emoji_rules:
        if keyword in name:
            return emoji

    return "🛒"




@callback(
    Output("expense-items-cards", "children"),
    Input("expense-type-selector", "value"),
    Input("home-month-filter", "value"),
)
def display_expenses_by_item(selected_expense, selected_month):
    if not selected_expense:
        return html.P("Selecione uma categoria.")

    worksheet = spreadsheet.worksheet(FOLHA_EVENTOS)
    values = worksheet.get("A1:E")

    if not values or len(values) < 2:
        return html.P("Nenhuma despesa encontrada.")

    grouped_items = {}

    for row in values[1:]:
        row = (row + [""] * 5)[:5]

        if not date_matches_month(row[0], selected_month):
            continue

        item_name = str(row[1]).strip()
        total_value = row[3]
        category = row[4]

        if normalize_text(category) != normalize_text(selected_expense):
            continue

        if not item_name:
            continue

        try:
            amount = parse_currency(total_value)
        except (ValueError, TypeError):
            continue

        group_name = get_item_group(item_name)
        group_key = normalize_text(group_name)

        if group_key not in grouped_items:
            grouped_items[group_key] = {
                "name": group_name,
                "total": 0.0,
            }

        grouped_items[group_key]["total"] += amount

    if not grouped_items:
        return html.P(
            "Nenhum item encontrado para esta categoria."
        )

    # ADD THE SORTING BLOCK HERE

    sorted_items = sorted(
        grouped_items.values(),
        key=lambda item: item["total"],
        reverse=True,
    )

    category_total = sum(
        item["total"]
        for item in sorted_items
    )

    # ADD THE CARDS RETURN BLOCK AFTER THE SORTING
    return [
        html.Div(
            [
                html.Div(
                    get_item_emoji(item["name"]),
                    className="expense-card-emoji",
                ),

                html.Div(
                    [
                        html.Div(
                            item["name"],
                            className="expense-card-name",
                        ),

                        html.Div(
                            format_brl(item["total"]),
                            className="expense-card-total",
                        ),

                        html.Div(
                            f"{item['percentage']:.1f}% da categoria",
                            className="expense-card-percentage",
                        ),
                    ]
                ),
            ],
            className="expense-item-card",

            # Green progress-bar effect
            style={
                "background": (
                    "linear-gradient("
                    "to right, "
                    f"rgba(46, 204, 113, 0.35) 0%, "
                    f"rgba(46, 204, 113, 0.35) {item['percentage']}%, "
                    f"white {item['percentage']}%, "
                    "white 100%"
                    ")"
                )
            },
        )
        for item in [
            {
                **grouped_item,
                "percentage": (
                    grouped_item["total"] / category_total * 100
                    if category_total
                    else 0
                ),
            }
            for grouped_item in sorted_items
        ]
    ]


###############  ABA 2 ###########################

def parse_currency(value):
    if value is None or value == "":
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    cleaned = (
        str(value)
        .strip()
        .replace("R$", "")
        .replace(" ", "")
    )

    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")

    return float(cleaned)


@callback(
    Output("weekday-forecast-card", "children"),
    Output("weekend-forecast-card", "children"),
    Output("monthly-forecast-card", "children"),
    Output("weekday-weekend-forecast", "figure"),
    Output("forecast-method-note", "children"),
    Input("expense-type-selector", "value"),
    Input("home-month-filter", "value"),
)
def update_weekday_weekend_forecast(selected_expense, selected_month):
    """Estimate spending occurrence and amount for weekdays/weekends."""
    worksheet = spreadsheet.worksheet(FOLHA_EVENTOS)
    values = worksheet.get("A1:E")

    empty_card = html.P("Ainda não há dados suficientes.")

    if not values or len(values) < 2:
        return empty_card, empty_card, empty_card, go.Figure(), ""

    transactions = []

    for row in values[1:]:
        row = (row + [""] * 5)[:5]

        if (
            selected_expense
            and normalize_text(row[4]) != normalize_text(selected_expense)
        ):
            continue

        date = pd.to_datetime(
            str(row[0]).strip(),
            dayfirst=True,
            errors="coerce",
        )

        if pd.isna(date) or not date_matches_month(row[0], selected_month):
            continue

        try:
            total = parse_currency(row[3])
        except (TypeError, ValueError):
            continue

        transactions.append({"DATE": date.normalize(), "TOTAL": total})

    if not transactions:
        return empty_card, empty_card, empty_card, go.Figure(), ""

    daily_spending = (
        pd.DataFrame(transactions)
        .groupby("DATE")["TOTAL"]
        .sum()
        .sort_index()
    )

    # Missing calendar dates are real zero-spending days, not missing data.
    today = pd.Timestamp.today().normalize()
    month_start = (
        pd.Timestamp(f"{selected_month}-01")
        if selected_month and selected_month != "TODOS"
        else today.replace(day=1)
    )
    month_end = month_start + pd.offsets.MonthEnd(0)
    observation_end = min(today, month_end)
    complete_dates = pd.date_range(
        start=month_start if selected_month != "TODOS" else daily_spending.index.min(),
        end=observation_end,
        freq="D",
    )
    daily_spending = daily_spending.reindex(complete_dates, fill_value=0.0)

    weekdays = daily_spending[daily_spending.index.dayofweek < 5]
    weekends = daily_spending[daily_spending.index.dayofweek >= 5]

    def estimate_period(series, days_in_next_week):
        if series.empty:
            return {
                "probability": 0.0,
                "amount_when_spending": 0.0,
                "expected_daily": 0.0,
                "expected_period": 0.0,
            }

        positive_days = series[series > 0]
        probability = float((series > 0).mean())
        amount_when_spending = (
            float(positive_days.mean()) if not positive_days.empty else 0.0
        )
        expected_daily = probability * amount_when_spending

        return {
            "probability": probability,
            "amount_when_spending": amount_when_spending,
            "expected_daily": expected_daily,
            "expected_period": expected_daily * days_in_next_week,
        }

    weekday_prediction = estimate_period(weekdays, 5)
    weekend_prediction = estimate_period(weekends, 2)

    # Estimate the selected month; completed months have no remaining days.

    monthly_weekday_prediction = estimate_period(weekdays, 1)
    monthly_weekend_prediction = estimate_period(weekends, 1)

    actual_current_month = float(
        daily_spending[
            (daily_spending.index >= month_start)
            & (daily_spending.index <= today)
        ].sum()
    )

    remaining_dates = pd.date_range(
        start=max(today + pd.Timedelta(days=1), month_start),
        end=month_end,
        freq="D",
    )
    remaining_weekdays = int((remaining_dates.dayofweek < 5).sum())
    remaining_weekends = int((remaining_dates.dayofweek >= 5).sum())

    predicted_remaining = (
        remaining_weekdays
        * monthly_weekday_prediction["expected_daily"]
        + remaining_weekends
        * monthly_weekend_prediction["expected_daily"]
    )
    predicted_month_total = actual_current_month + predicted_remaining

    def forecast_card(icon, title, prediction, period_label):
        return [
            html.H4(f"{icon} {title}"),
            html.P(
                "Chance de gastar: "
                f"{prediction['probability'] * 100:.1f}%"
            ),
            html.P(
                "Esperado por dia: "
                f"{format_brl(prediction['expected_daily'])}"
            ),
            html.H5(
                f"{period_label}: "
                f"{format_brl(prediction['expected_period'])}"
            ),
        ]

    weekday_card = forecast_card(
        "💼",
        "Dias úteis",
        weekday_prediction,
        "Próxima segunda–sexta",
    )
    weekend_card = forecast_card(
        "🌴",
        "Fim de semana",
        weekend_prediction,
        "Próximo sábado–domingo",
    )
    monthly_card = [
        html.H4("📅 Previsão mensal"),
        html.P(
            f"Gasto no mês ({month_start:%m/%Y}): {format_brl(actual_current_month)}"
        ),
        html.P(
            f"Previsão restante: {format_brl(predicted_remaining)}"
        ),
        html.H5(
            f"Total previsto: {format_brl(predicted_month_total)}"
        ),
    ]

    figure = go.Figure(
        go.Bar(
            x=["Dias úteis", "Fim de semana"],
            y=[
                weekday_prediction["expected_period"],
                weekend_prediction["expected_period"],
            ],
            marker_color=["#2ecc71", "#3498db"],
            customdata=[
                [
                    weekday_prediction["expected_daily"],
                    weekday_prediction["probability"] * 100,
                ],
                [
                    weekend_prediction["expected_daily"],
                    weekend_prediction["probability"] * 100,
                ],
            ],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Total previsto: R$ %{y:,.2f}<br>"
                "Esperado/dia: R$ %{customdata[0]:,.2f}<br>"
                "Chance de gastar: %{customdata[1]:.1f}%"
                "<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        title="Previsão para a próxima semana",
        xaxis_title="Período",
        yaxis_title="Total previsto (R$)",
        template="plotly_white",
    )

    history_days = len(daily_spending)
    category_label = selected_expense or "todas as despesas"

    if history_days < 56:
        method_note = (
            f"Estimativa inicial para {category_label}: {history_days} dias "
            "de histórico. A precisão tende a melhorar após 8 semanas."
        )
    else:
        method_note = (
            f"Modelo de duas etapas para {category_label}, usando "
            f"o período selecionado ({history_days} dias): "
            "chance de gastar × valor médio quando há gasto."
        )

    if selected_month and selected_month != "TODOS":
        method_note += f" Mês de referência: {month_start:%m/%Y}."

    return (
        weekday_card,
        weekend_card,
        monthly_card,
        figure,
        method_note,
    )



@callback(
    Output("grafico-month-filter", "options"),
    Output("grafico-month-filter", "value"),
    Input("dash_table1", "data"),
    State("grafico-month-filter", "value"),
)
def update_plot_months(data, selected_month):
    months = set()
    for row in data or []:
        date = pd.to_datetime(row.get("DATA", ""), dayfirst=True, errors="coerce")
        if pd.notna(date):
            months.add(date.strftime("%Y-%m"))
    options = [{"label": "Todos os meses", "value": "TODOS"}] + [
        {"label": f"{month[5:]}/{month[:4]}", "value": month}
        for month in sorted(months, reverse=True)
    ]
    return options, selected_month if selected_month in months else "TODOS"


@callback(
    Output("grafico-data", "figure"),
    Output("grafico-despesas", "figure"),
    Input("dash_table1", "data"),
    Input("grafico-expense-filter", "value"),
    Input("grafico-month-filter", "value"),
)
def update_plots(data, selected_expense, selected_month):
    if not data:
        return go.Figure(), go.Figure()

    df = pd.DataFrame(data)

    df["DATA"] = pd.to_datetime(
        df["DATA"],
        dayfirst=True,
        errors="coerce",
    )

    # PREÇO already contains quantity × unit price
    df["TOTAL"] = df["PREÇO"].apply(parse_currency)

    # Remove invalid rows
    df = df.dropna(subset=["DATA"])
    df = df[df["DESPESAS"].notna()]
    df = df[
        df["DESPESAS"].astype(str).str.strip() != ""
    ]

    if selected_month and selected_month != "TODOS":
        df = df[df["DATA"].dt.strftime("%Y-%m") == selected_month]

    # If nothing or "TODAS" is selected, keep every expense type.
    # Otherwise, filter by the selected expense.
    if selected_expense and selected_expense != "TODAS":
        df_filtered = df[
            df["DESPESAS"].apply(normalize_text)
            == normalize_text(selected_expense)
        ]
    else:
        df_filtered = df

    if df_filtered.empty:
        empty_figure = go.Figure()

        empty_figure.add_annotation(
            text="Nenhum dado encontrado",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font={"size": 16},
        )

        empty_figure.update_xaxes(visible=False)
        empty_figure.update_yaxes(visible=False)

        return empty_figure, go.Figure(empty_figure)

    # Total grouped by date
    by_date = (
        df_filtered.groupby("DATA", as_index=False)["TOTAL"]
        .sum()
        .sort_values("DATA")
    )

    figure_date = go.Figure(
        go.Scatter(
            x=by_date["DATA"],
            y=by_date["TOTAL"],
            marker_color="#2ecc71",
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b><br>"
                "Total: R$ %{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    if not selected_expense or selected_expense == "TODAS":
        title_suffix = "Todas as despesas"
    else:
        title_suffix = str(selected_expense).title()

    if selected_month and selected_month != "TODOS":
        title_suffix += f" — {selected_month[5:]}/{selected_month[:4]}"

    figure_date.update_layout(
        title=f"Gastos por data — {title_suffix}",
        xaxis_title="Data",
        yaxis_title="Total gasto (R$)",
        template="plotly_white",
    )

    # Total grouped by expense type
    by_expense = (
        df_filtered.groupby("DESPESAS", as_index=False)["TOTAL"]
        .sum()
        .sort_values("TOTAL", ascending=False)
    )

    figure_expenses = go.Figure(
        go.Bar(
            x=by_expense["DESPESAS"],
            y=by_expense["TOTAL"],
            marker_color="#3498db",
            hovertemplate=(
                "%{x}<br>"
                "R$ %{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    figure_expenses.update_layout(
        title=f"Total por tipo — {title_suffix}",
        xaxis_title="Tipo de despesa",
        yaxis_title="Total gasto (R$)",
        template="plotly_white",
    )

    figure_date.update_xaxes(
        title_text="DATA",
        tickformat="%d/%m/%Y",
    )

    return figure_date, figure_expenses






@callback(
    Output("dash_table1", "columns"),
    Output("dash_table1", "data"),
    Output("nome-do-item", "value"),
    Output("qtd-item", "value"),
    Output("preco-item", "value"),
    Output("despesas-dropdown", "value"),
    Input("register-button", "n_clicks"),
    State("nome-do-item", "value"),
    State("qtd-item", "value"),
    State("preco-item", "value"),
    State("despesas-dropdown", "value"),

)

def register_item(n_clicks, nome, qtd, preco, despesas):
    worksheet = spreadsheet.worksheet(FOLHA_EVENTOS)

    fields_are_valid = (
        nome not in (None, "")
        and qtd not in (None, "")
        and preco not in (None, "")
        and despesas not in (None, "")
    )

    print(
        "SUBMISSION:",
        f"n_clicks={n_clicks!r}",
        f"nome={nome!r}",
        f"qtd={qtd!r}",
        f"preco={preco!r}",
        f"despesas={despesas!r}",
        f"valid={fields_are_valid}",
        f"worksheet={worksheet.title!r}",
    )

    if n_clicks and fields_are_valid:
        qtd_numerica = parse_currency(qtd)
        preco_unitario = parse_currency(preco)
        preco_total = qtd_numerica * preco_unitario

        print(
            "APPENDING:",
            nome,
            qtd_numerica,
            preco_total,
            despesas,
        )

        result = worksheet.append_row(
            [
                datetime.now().strftime("%d/%m/%Y"),
                nome,
                qtd_numerica,
                preco_total,
                despesas,
            ],
            value_input_option="RAW",
            table_range="A:E",
        )

        print("GOOGLE RESPONSE:", result)

    values = worksheet.get("A1:E")

    if not values:
        return (
            [],
            [],
            no_update,
            no_update,
            no_update,
            no_update,
        )


    headers = values[0]
    rows = [
        (row + [""] * len(headers))[:len(headers)]
        for row in values[1:]
    ]

    columns = [
        {"name": header, "id": header}
        for header in headers
    ]

    data = pd.DataFrame(
        rows,
        columns=headers,
    ).to_dict("records")

    data = data[::-1]



    if n_clicks and fields_are_valid:
        return (
            columns,
            data,
            None,
            None,
            None,
            None,
        )

    return (
        columns,
        data,
        no_update,
        no_update,
        no_update,
        no_update,
    )













###############  ABA 1 ###########################



# ============================================================
# RUN APPLICATION
# ============================================================

app.run(
    host="0.0.0.0",
    port=8050,
    debug=False
)
