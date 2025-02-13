import time

import streamlit as lit
import utils.functions as f
from sqlalchemy import text

connection = f.get_connection()

def get_products():
    with connection.connect() as connected:
        cursor = connected.execute(text("SELECT id_produit, nom_produit FROM PRODUIT"))
        products = {row[0]: row[1] for row in cursor.fetchall()}
        return products

def get_molecules(product_id):
    with connection.connect() as connected:
        cursor = connected.execute(text("""
            SELECT MOLECULE.id_molecule, MOLECULE.nom_molecule
            FROM COMPOSITION
            JOIN MOLECULE ON COMPOSITION.id_molecule = MOLECULE.id_molecule
            WHERE id_produit = :id 
        """), {"id": product_id})

        return {row[0]: row[1] for row in cursor.fetchall()}

def check_compatibility(molecules_1, molecules_2):
    incompatibles = []
    neutrals = []
    with connection.connect() as connected:
        for molecule_1, name_1 in molecules_1.items():
            for molecule_2, name_2 in molecules_2.items():
                cursor = connected.execute(text("""
                    SELECT compatibilite
                    FROM INTERACTION
                    WHERE (id_molecule_1 = :molecule_1 AND id_molecule_2 = :molecule_2)
                    OR (id_molecule_1 = :molecule_2 AND id_molecule_2 = :molecule_1)
                """), {"molecule_1": molecule_1, "molecule_2": molecule_2})

                row = cursor.fetchone()

                if row:
                    if row[0].lower() == "bad":
                        incompatibles.append((name_1, name_2))
                    elif row[0].lower() == "neutral":
                        neutrals.append((name_1, name_2))
    return incompatibles, neutrals

def show_pages():
    lit.title("Comparison")
    lit.write("Cosmetic risk management project")
    spinner_css = """
    <style>
        .stSpinner {
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .stSpinner div {
            display: flex;
            justify-content: center;
            align-items: center;
        }
    </style>
    """
    lit.markdown(spinner_css, unsafe_allow_html=True)

    _products = get_products()

    product_1 = lit.selectbox("Select the first product:", options=list(_products.keys()), format_func=lambda x: _products[x])
    product_2 = lit.selectbox("Select the second product:", options=list(_products.keys()), format_func=lambda x: _products[x])
    if lit.button("Check compatibility", use_container_width=True):
        if product_1 == product_2:
            lit.warning("Choose 2 different products")
        else:
            with lit.spinner(""):
                molecules_1 = get_molecules(product_1)
                molecules_2 = get_molecules(product_2)
                incompatibles, neutrals = check_compatibility(molecules_1, molecules_2)

            if not incompatibles and not neutrals:
                lit.success("These products are compatibles. ✅")
            elif not incompatibles and neutrals:
                lit.warning("These products are compatibles but contains some neutral molecules. ⚠️")
                lit.write("Here is the list:")
                lit.table(
                    [{"Product 1 molecules": molecule_1, "Product 2 molecules": molecule_2} for molecule_1, molecule_2 in neutrals])
            else:
                lit.error("These products are not compatibles. ❌")
                lit.write("Incompatible molecules:")
                lit.table(
                    [{"Product 1 molecules": molecule_1, "Product 2 molecules": molecule_2} for molecule_1, molecule_2 in
                     incompatibles])

                if neutrals:
                    lit.warning("There are also neutral molecules:")
                    lit.table(
                        [{"Product 1 molecules": molecule_1, "Product 2 molecules": molecule_2} for molecule_1, molecule_2
                         in neutrals])

show_pages()