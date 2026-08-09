from datetime import datetime
from pathlib import Path
from uuid import uuid4

import dash_bootstrap_components as dbc
import pandas as pd
import gspread
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

app.title = "Sistema de Registros"


# ============================================================
# APONTAMENTOS PAGE
# ============================================================

def apontamentos_layout():

    return html.Div(
        [
            # ------------------------------------------------
            # PAGE HEADER
            # ------------------------------------------------
            html.Div(
                [
                    html.H2(
                        "REGISTRO",
                        className="page-title",
                    ),

                    html.P(
                        "REGISTRE UM NOVO USUÁRIO",
                        className="page-subtitle",
                    ),
                ],
                className="page-header",
            ),

            # ------------------------------------------------
            # REGISTRATION FORM
            # ------------------------------------------------
            html.Div(
                [
                    html.Div(
                        [
                            # NAME
                            html.Div(
                                [
                                    html.Label("NOME"),

                                    dcc.Input(
                                        id="input-name",
                                        type="text",
                                        placeholder="DIGITE O NOME",
                                        className="form-input",
                                    ),
                                ],
                                className="field",
                            ),

                            # AGE
                            html.Div(
                                [
                                    html.Label("IDADE"),

                                    dcc.Input(
                                        id="input-age",
                                        type="number",
                                        min=0,
                                        max=120,
                                        step=1,
                                        placeholder="DIGITE A IDADE",
                                        className="form-input",
                                    ),
                                ],
                                className="field",
                            ),

                            # GENDER
                            html.Div(
                                [
                                    html.Label("GÊNERO"),

                                    dcc.Dropdown(
                                        id="dropdown-gender",

                                        options=[
                                            {
                                                "label": "FEMININO",
                                                "value": "FEMININO",
                                            },
                                            {
                                                "label": "MASCULINO",
                                                "value": "MASCULINO",
                                            },
                                            {
                                                "label": "NÃO BINÁRIO",
                                                "value": "NÃO BINÁRIO",
                                            },
                                            {
                                                "label": "PREFIRO NÃO DIZER",
                                                "value": "PREFIRO NÃO DIZER",
                                            },
                                        ],

                                        placeholder="SELECIONE",
                                        clearable=True,
                                    ),
                                ],
                                className="field",
                            ),

                            # OCCUPATION
                            html.Div(
                                [
                                    html.Label("OCUPAÇÃO"),

                                    dcc.Dropdown(
                                        id="dropdown-occupation",

                                        options=[
                                            {
                                                "label": "ENGENHEIRO(A)",
                                                "value": "ENGENHEIRO(A)",
                                            },
                                            {
                                                "label": "TÉCNICO(A)",
                                                "value": "TÉCNICO(A)",
                                            },
                                            {
                                                "label": "OPERADOR(A)",
                                                "value": "OPERADOR(A)",
                                            },
                                            {
                                                "label": "GERENTE",
                                                "value": "GERENTE",
                                            },
                                            {
                                                "label": "PROFESSOR(A)",
                                                "value": "PROFESSOR(A)",
                                            },
                                            {
                                                "label": "ESTUDANTE",
                                                "value": "ESTUDANTE",
                                            },
                                            {
                                                "label": "PROFISSIONAL DA SAÚDE",
                                                "value": "PROFISSIONAL DA SAÚDE",
                                            },
                                            {
                                                "label": "AUTÔNOMO(A)",
                                                "value": "AUTÔNOMO(A)",
                                            },
                                            {
                                                "label": "DESEMPREGADO(A)",
                                                "value": "DESEMPREGADO(A)",
                                            },
                                            {
                                                "label": "OUTRO",
                                                "value": "OUTRO",
                                            },
                                        ],

                                        placeholder="SELECIONE",
                                        clearable=True,
                                    ),
                                ],
                                className="field",
                            ),
                        ],
                        className="form-grid",
                    ),


                    html.Div(
                        [
                            html.Button(
                                "REGISTRAR",
                                id="register-button",
                                n_clicks=0,
                                className="primary-button",
                            ),

                            html.Button(
                                "LIMPAR CAMPOS",
                                id="clear-fields-button",
                                n_clicks=0,
                                className="secondary-button",
                            ),
                        ],
                        className="button-row",
                    ),

                    # SUCCESS OR ERROR MESSAGE
                    html.Div(
                        id="registration-message",
                    ),
                ],
                className="card",
            ),

            # ------------------------------------------------
            # REGISTRATION TABLE
            # ------------------------------------------------
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H4(
                                        "PESSOAS REGISTRADAS"
                                    ),

                                    html.P(
                                        "HISTÓRICO DE REGISTROS"
                                    ),
                                ]
                            ),

                            html.Button(
                                "LIMPAR TABELA",
                                id="clear-table-button",
                                n_clicks=0,
                                className="secondary-button",
                            ),
                        ],
                        className="table-heading",
                    ),

                    dash_table.DataTable(
                        id="registration-table",

                        columns=[
                            {
                                "name": "ID",
                                "id": "ID",
                            },
                            {
                                "name": "DATA E HORA",
                                "id": "DATETIME",
                            },
                            {
                                "name": "NOME",
                                "id": "NOME",
                            },
                            {
                                "name": "IDADE",
                                "id": "IDADE",
                                "type": "numeric",
                            },
                            {
                                "name": "GÊNERO",
                                "id": "GENERO",
                            },
                            {
                                "name": "OCUPAÇÃO",
                                "id": "OCUPACAO",
                            },
                        ],

                        data=[],

                        page_size=10,
                        sort_action="native",
                        filter_action="native",

                        style_table={
                            "overflowX": "auto",
                            "border": "1px solid #dbe3ea",
                        },

                        style_header={
                            "backgroundColor": "#17324d",
                            "color": "white",
                            "fontFamily": '"Segoe UI", Arial, sans-serif',
                            "fontSize": "12px",
                            "fontWeight": "700",
                            "textAlign": "left",
                            "padding": "11px",
                            "border": "none",
                        },

                        style_cell={
                            "backgroundColor": "white",
                            "color": "#273444",
                            "fontFamily": '"Segoe UI", Arial, sans-serif',
                            "fontSize": "12px",
                            "padding": "11px",
                            "textAlign": "left",
                            "minWidth": "100px",
                            "maxWidth": "260px",
                            "overflow": "hidden",
                            "textOverflow": "ellipsis",
                            "border": "none",
                            "borderBottom": "1px solid #e4eaf0",
                        },

                        style_cell_conditional=[
                            {
                                "if": {
                                    "column_id": "ID",
                                },
                                "width": "110px",
                            },
                            {
                                "if": {
                                    "column_id": "DATETIME",
                                },
                                "width": "170px",
                            },
                            {
                                "if": {
                                    "column_id": "IDADE",
                                },
                                "width": "80px",
                            },
                        ],

                        style_data_conditional=[
                            {
                                "if": {
                                    "row_index": "odd",
                                },
                                "backgroundColor": "#f8fafc",
                            }
                        ],
                    ),
                ],
                className="card",
            ),
        ]
    )


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

        # Stores the registrations in the current browser session
        dcc.Store(
            id="registration-store",
            data=[],
            storage_type="session",
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
                                        "APONTAMENTOS",
                                        href="/apontamentos",
                                        active="exact",
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


TIPO_DESPESAS = ["HIGIENE PESSOAL", "ALIMENTAÇÃO", "FARMÁCIA", "LIMPEZA"]

# ============================================================
# PAGE NAVIGATION
# ============================================================

@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):

    if pathname in (
        None,
        "/",
        "/apontamentos",
    ):
        return apontamentos_layout()

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




            ],
            className="card",
        )

    return html.Div(
        [
            html.H2("PÁGINA NÃO ENCONTRADA"),

            html.P(
                "SELECIONE UMA OPÇÃO NO MENU."
            ),
        ],
        className="card",
    )


# ============================================================
# REGISTER, CLEAR FIELDS AND CLEAR TABLE
# ============================================================

###############  ABA 2 ###########################
@callback(
Output("dash_table1", "columns"),
    Output("dash_table1", "data"),
    Input("register-button", "n_clicks"),
    State("nome-do-item", "value"),
    State("qtd-item", "value"),
    State("preco-item", "value"),
    State("despesas-dropdown", "value"),

    prevent_initial_call=True,
)

def register_item(n_clicks, nome, qtd, preco, despesas):
    worksheet = spreadsheet.worksheet(FOLHA_EVENTOS)

    # Read existing rows once
    df = pd.DataFrame(worksheet.get_all_records())

    row = {
        "ITEM": nome,
        "QTD": qtd,
        "PREÇO": preco,
        "DESPESAS": despesas,
    }

    # Persist the new row
    worksheet.append_row(
        list(row.values()),
        value_input_option="USER_ENTERED",
    )

    # Update the local copy without reading the sheet again
    df = pd.concat(
        [df, pd.DataFrame([row])],
        ignore_index=True,
    )

    columns = [{"name": column, "id": column} for column in df.columns]
    data = df.to_dict("records")

    return columns, data

###############  ABA 1 ###########################
@callback(
    Output("registration-store", "data"),
    Output("registration-message", "children"),
    Output("registration-message", "className"),
    Output("input-name", "value"),
    Output("input-age", "value"),
    Output("dropdown-gender", "value"),
    Output("dropdown-occupation", "value"),

    Input("register-button", "n_clicks"),
    Input("clear-fields-button", "n_clicks"),
    Input("clear-table-button", "n_clicks"),

    State("input-name", "value"),
    State("input-age", "value"),
    State("dropdown-gender", "value"),
    State("dropdown-occupation", "value"),
    State("registration-store", "data"),

    prevent_initial_call=True,
)
def handle_form(
    register_clicks,
    clear_fields_clicks,
    clear_table_clicks,
    name,
    age,
    gender,
    occupation,
    records,
):
    records = records or []

    triggered_id = ctx.triggered_id

    # --------------------------------------------------------
    # CLEAR FORM FIELDS
    # --------------------------------------------------------
    if triggered_id == "clear-fields-button":
        return (
            no_update,
            "",
            "",
            "",
            None,
            None,
            None,
        )

    # --------------------------------------------------------
    # CLEAR TABLE
    # --------------------------------------------------------
    if triggered_id == "clear-table-button":
        return (
            [],
            "TABELA LIMPA COM SUCESSO.",
            "message success",
            no_update,
            no_update,
            no_update,
            no_update,
        )

    # --------------------------------------------------------
    # VALIDATE FORM
    # --------------------------------------------------------
    missing_fields = []

    if name is None or not str(name).strip():
        missing_fields.append("NOME")

    if age is None:
        missing_fields.append("IDADE")

    if not gender:
        missing_fields.append("GÊNERO")

    if not occupation:
        missing_fields.append("OCUPAÇÃO")

    if missing_fields:
        return (
            no_update,
            (
                "PREENCHA OS SEGUINTES CAMPOS: "
                + ", ".join(missing_fields)
                + "."
            ),
            "message error",
            no_update,
            no_update,
            no_update,
            no_update,
        )

    # Additional age validation
    if age < 0 or age > 120:
        return (
            no_update,
            "A IDADE DEVE ESTAR ENTRE 0 E 120.",
            "message error",
            no_update,
            no_update,
            no_update,
            no_update,
        )

    # --------------------------------------------------------
    # CREATE REGISTRATION
    # --------------------------------------------------------
    new_record = {
        "ID": uuid4().hex[:8].upper(),
        "DATETIME": datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        ),
        "NOME": str(name).strip().upper(),
        "IDADE": int(age),
        "GENERO": gender,
        "OCUPACAO": occupation,
    }

    # Newest registration appears first
    updated_records = [
        new_record,
        *records,
    ]

    return (
        updated_records,
        (
            f"{new_record['NOME']} "
            "REGISTRADO(A) COM SUCESSO."
        ),
        "message success",
        "",
        None,
        None,
        None,
    )


# ============================================================
# UPDATE TABLE FROM STORE
# ============================================================

@callback(
    Output("registration-table", "data"),
    Input("registration-store", "data"),
)
def show_records(records):

    if not records:
        return []

    # Remove old records created with the previous English keys.
    normalized_records = []

    for record in records:
        normalized_records.append(
            {
                "ID": record.get("ID", ""),
                "DATETIME": record.get("DATETIME", ""),
                "NOME": record.get(
                    "NOME",
                    record.get("NAME", ""),
                ),
                "IDADE": record.get(
                    "IDADE",
                    record.get("AGE", ""),
                ),
                "GENERO": record.get(
                    "GENERO",
                    record.get(
                        "GÊNERO",
                        record.get("GENDER", ""),
                    ),
                ),
                "OCUPACAO": record.get(
                    "OCUPACAO",
                    record.get("OCCUPATION", ""),
                ),
            }
        )

    return normalized_records


# ============================================================
# RUN APPLICATION
# ============================================================

app.run(
    host="0.0.0.0",
    port=8050,
    debug=False
)