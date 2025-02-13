import streamlit as lit
import utils.functions as f
import pandas as pd

connection = f.get_connection()

def show_pages():
    number_of_rows = 7
    lit.title("Brands")
    lit.write("Cosmetic risk management project")
    lit.write("List of brands")

    if "search_name" not in lit.session_state:
        lit.session_state.search_name = ""

    with lit.form(key='advanced_search_form'):
        placeholder = lit.empty()

        search_name = placeholder.text_input("Search by ID/Name:", placeholder="My brand", key="1")
        submit_button = lit.form_submit_button(label="Search")

        if submit_button:
            lit.session_state.page_number = 1
            lit.session_state.search_name = search_name or ""

    if lit.session_state.search_name:
        search = lit.session_state.search_name
        query = f"SELECT count(*) FROM MARQUE WHERE LOWER(id_marque) LIKE LOWER('%{search}%') or LOWER(nom_marque) LIKE LOWER('%{search}%')"
    else:
        query = "SELECT count(*) FROM MARQUE"
    total_rows = pd.read_sql(query, connection).iloc[0, 0]
    total_pages = (total_rows // number_of_rows) + (1 if total_rows % number_of_rows else 0)

    if "page_number" not in lit.session_state:
        lit.session_state.page_number = 1

    offset = (lit.session_state.page_number - 1) * number_of_rows

    if lit.session_state.search_name:
        search = lit.session_state.search_name
        query = f"""
                SELECT id_marque as Identification, nom_marque as brand, pays as country, annee_naissance as start_year, expiration as end_year_licence
                FROM MARQUE
                WHERE LOWER(id_marque) LIKE LOWER('%{search}%') or LOWER(nom_marque) LIKE LOWER('%{search}%')
                OFFSET {offset} ROWS FETCH NEXT {number_of_rows} ROWS ONLY
            """
    else:
        query = f"""
                SELECT id_marque as Identification, nom_marque as brand, pays as country, annee_naissance as start_year, expiration as end_year_licence
                FROM MARQUE
                OFFSET {offset} ROWS FETCH NEXT {number_of_rows} ROWS ONLY
            """
    df = pd.read_sql(query, connection)
    if df.shape[0] == 0:
        df = pd.DataFrame(columns=["identification", "brand", "country", "start_year", "end_year_licence"])
    else:
        df["end_year_licence"] = df["end_year_licence"].dt.strftime('%B %d, %Y')
    lit.write(f"{total_rows} brand(s) found.")
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

