import pandas as pd
import streamlit as lit
from utils import functions

connection = functions.get_connection()

def show_pages():
    number_of_rows = 7
    lit.title("Home")
    lit.write("Cosmetic risk management project")
    lit.write("List of products")
    if "search_name" not in lit.session_state:
        lit.session_state.search_name = ""

    with lit.form(key='advanced_search_form'):
        placeholder = lit.empty()

        search_name = placeholder.text_input("Search by ID/Name/Brand:", placeholder="P00 or My brand or My product", key="1")
        submit_button = lit.form_submit_button(label="Search")

        if submit_button:
            lit.session_state.page_number = 1
            lit.session_state.search_name = search_name or ""

    if lit.session_state.search_name:
        search = lit.session_state.search_name
        query = f"SELECT count(*) FROM PRODUIT p INNER JOIN MARQUE m ON p.id_marque = m.id_marque WHERE LOWER(p.id_produit) LIKE LOWER('%{search}%') or LOWER(p.nom_produit) LIKE LOWER('%{search}%') or LOWER(m.nom_marque) LIKE LOWER('%{search}%')"
    else:
        query = "SELECT count(*) FROM PRODUIT p INNER JOIN MARQUE m ON p.id_marque = m.id_marque"
    total_rows = pd.read_sql(query, connection).iloc[0, 0]
    total_pages = (total_rows // number_of_rows) + (1 if total_rows % number_of_rows else 0)

    if "page_number" not in lit.session_state:
        lit.session_state.page_number = 1

    offset = (lit.session_state.page_number - 1) * number_of_rows

    if lit.session_state.search_name:
        search = lit.session_state.search_name
        query = f"""
                SELECT p.id_produit as Identification, p.nom_produit as Product, m.nom_marque as Brand
                FROM PRODUIT p INNER JOIN MARQUE m 
                ON p.id_marque = m.id_marque
                WHERE LOWER(p.id_produit) LIKE LOWER('%{search}%') or LOWER(p.nom_produit) LIKE LOWER('%{search}%') or LOWER(m.nom_marque) LIKE LOWER('%{search}%')
                OFFSET {offset} ROWS FETCH NEXT {number_of_rows} ROWS ONLY
            """
    else:
        query = f"""
                SELECT p.id_produit as Identification, p.nom_produit as Product, m.nom_marque as Brand
                FROM PRODUIT p INNER JOIN MARQUE m 
                ON p.id_marque = m.id_marque
                OFFSET {offset} ROWS FETCH NEXT {number_of_rows} ROWS ONLY
            """
    df = pd.read_sql(query, connection)

    lit.write(f"{total_rows} product(s) found.")
    lit.dataframe(df, hide_index=True, use_container_width=True)

    col1, col2, col3 = lit.columns([1, 2, 1])

    lit.markdown("""
        <style>
        .stColumn > div {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        </style>
    """, unsafe_allow_html=True)

    with col1:
        if lit.session_state.page_number > 1:
            if lit.button("⬅️ Précédent", use_container_width=True):
                lit.session_state.page_number -= 1
                lit.rerun()
        else:
            lit.button("⬅️ Précédent", use_container_width=True, disabled=True)

    with col2:
        lit.markdown(
            f"<p style=\"text-align:center;\">Page {lit.session_state.page_number} / {total_pages}</p>",
            unsafe_allow_html=True
        )

    with col3:
        if lit.session_state.page_number < total_pages:
            if lit.button("Suivant ➡️", use_container_width=True):
                lit.session_state.page_number += 1
                lit.rerun()
        else:
            lit.button("Suivant ➡️", use_container_width=True, disabled=True)

show_pages()