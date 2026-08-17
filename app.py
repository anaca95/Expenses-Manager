from datetime import datetime
from pathlib import Path
from uuid import uuid4
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
import gspread
import unicodedata
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
                                            html.P("CADASTRO"),
                                        ]
                                    ),
                                ],
                                className="brand",
                            ),

                            dbc.Nav(
                                [

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
                        style={"width": "60%"},
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
                        html.P("Total gasto neste mês"),
                        html.H3("R$ 0,00", id="total-mensal"),
                    ],
                    className="card",
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
)
def display_expenses_by_item(selected_expense):
    if not selected_expense:
        return html.P("Selecione uma categoria.")

    worksheet = spreadsheet.worksheet(FOLHA_EVENTOS)
    values = worksheet.get("A1:E")

    if not values or len(values) < 2:
        return html.P("Nenhuma despesa encontrada.")

    grouped_items = {}

    for row in values[1:]:
        row = (row + [""] * 5)[:5]

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

        normalized_item = normalize_text(item_name)

        if normalized_item not in grouped_items:
            grouped_items[normalized_item] = {
                "name": item_name,
                "total": 0.0,
            }

        grouped_items[normalized_item]["total"] += amount

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
    Output("grafico-data", "figure"),
    Output("grafico-despesas", "figure"),
    Input("dash_table1", "data"),
)
def update_plots(data):
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

    # Remove rows with invalid dates or empty expense types
    df = df.dropna(subset=["DATA"])
    df = df[df["DESPESAS"].notna()]
    df = df[df["DESPESAS"].astype(str).str.strip() != ""]

    by_date = (
        df.groupby("DATA", as_index=False)["TOTAL"]
        .sum()
        .sort_values("DATA")
    )

    by_expense = (
        df.groupby("DESPESAS", as_index=False)["TOTAL"]
        .sum()
        .sort_values("TOTAL", ascending=False)
    )

    date_figure = go.Figure()

    date_figure.add_trace(
        go.Scatter(
            x=by_date["DATA"],
            y=by_date["TOTAL"],
            mode="lines+markers",
            name="Expenses",
            hovertemplate=(
                "%{x|%d/%m/%Y}<br>"
                "R$ %{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )



    date_figure.update_xaxes(
        title_text="DATA",
        tickformat="%d/%m/%Y",
    )

    date_figure.update_layout(
        title="DESPESAS POR DATA",
        xaxis_title="DATA",
        yaxis_title="TOTAL",
        template="plotly_white",
    )

    expense_figure = go.Figure()

    expense_figure.add_trace(
        go.Bar(
            x=by_expense["DESPESAS"],
            y=by_expense["TOTAL"],
            hovertemplate=(
                "%{x}<br>"
                "R$ %{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    expense_figure.update_layout(
        title="DESPESAS POR TIPO",
        xaxis_title="TIPO",
        yaxis_title="TOTAL",
        template="plotly_white",
    )

    return date_figure, expense_figure






@callback(
    Output("dash_table1", "columns"),
    Output("dash_table1", "data"),
    Output("nome-do-item", "value"),
    Output("qtd-item", "value"),
    Output("preco-item", "value"),
    Output("despesas-dropdown", "value"),
    Output("total-mensal", "children"),
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

    # calculate the total spent in a month and display it in a card like box
    agora = datetime.now()
    total_mensal = 0.0

    for row in values[1:]:
        row = (row + [""] * 5)[:5]

        try:
            data_registro = datetime.strptime(
                str(row[0]).strip(),
                "%d/%m/%Y",
            )

            if (
                data_registro.month == agora.month
                and data_registro.year == agora.year
            ):
                # Column D contains preco_total
                total_mensal += parse_currency(row[3])

        except (ValueError, TypeError, IndexError):
            continue

    total_mensal_formatado = (
        f"R$ {total_mensal:,.2f}"
        .replace(",", "_")
        .replace(".", ",")
        .replace("_", ".")
    )

    if not values:
        return (
            [],
            [],
            no_update,
            no_update,
            no_update,
            no_update,
            "R$ 0,00",
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
            total_mensal_formatado,
        )

    return (
        columns,
        data,
        no_update,
        no_update,
        no_update,
        no_update,
        total_mensal_formatado,
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