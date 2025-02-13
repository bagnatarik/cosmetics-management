import streamlit as lit
import pandas as pd
import matplotlib.pyplot as plt
import utils.functions as f
import altair as alt

connection = f.get_connection()

def show_pages():
    lit.title("Visualization")
    lit.write("Cosmetic risk management project")

    lit.write("Product by Brand")

    query = """
    SELECT m.nom_marque, COUNT(p.id_produit) AS number_of_products
    FROM MARQUE m
    JOIN PRODUIT p ON m.id_marque = p.id_marque
    GROUP BY m.nom_marque
    """

    df = pd.read_sql(query, connection)

    lit.bar_chart(df.set_index('nom_marque')['number_of_products'])

    lit.write("Top 10 Most-Used Molecules")

    query = """
        SELECT m.nom_molecule, COUNT(cp.id_produit) AS number_of_product
        FROM MOLECULE m
        JOIN COMPOSITION cp ON m.id_molecule = cp.id_molecule
        GROUP BY m.nom_molecule
        ORDER BY number_of_product DESC
        FETCH FIRST 10 ROWS ONLY
        """
    df = pd.read_sql(query, connection)
    lit.bar_chart(df.set_index('nom_molecule')['number_of_product'])

    query = """
        SELECT c.nom_categorie AS "category name", COUNT(m.id_molecule) AS "number of molecules" 
        FROM CATEGORIE c
        JOIN MOLECULE m ON c.id_categorie = m.id_categorie 
        GROUP BY c.nom_categorie 
        ORDER BY COUNT(m.id_molecule) DESC
        """
    df = pd.read_sql(query, connection)

    chart = alt.Chart(df).mark_arc().encode(
        theta=alt.Theta(field="number of molecules", type="quantitative"),
        color=alt.Color(field="category name", type="nominal"),
        tooltip=["category name", "number of molecules"]
    ).properties(title="Molecules by Category")
    lit.altair_chart(chart, use_container_width=True)
show_pages()