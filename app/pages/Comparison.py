import streamlit as lit
import utils.functions as f
from sqlalchemy import text

connection = f.get_connection()

# 🔹 Cache les produits pour éviter de recharger à chaque interaction
@lit.cache_data
def get_products():
    with connection.connect() as connected:
        cursor = connected.execute(text("SELECT id_produit, nom_produit FROM PRODUIT"))
        return {row[0]: row[1] for row in cursor.fetchall()}

@lit.cache_data
def get_molecules(product_id):
    with connection.connect() as connected:
        cursor = connected.execute(text("""
            SELECT MOLECULE.id_molecule, MOLECULE.nom_molecule
            FROM COMPOSITION
            JOIN MOLECULE ON COMPOSITION.id_molecule = MOLECULE.id_molecule
            WHERE id_produit = :id 
        """), {"id": product_id})
        return {row[0]: row[1] for row in cursor.fetchall()}

@lit.cache_data
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

# 🔹 Récupérer la liste des produits (cachée pour éviter les recharges inutiles)
_products = get_products()

# 🔹 Initialiser les valeurs sélectionnées dans `st.session_state`
if "product_1" not in lit.session_state:
    lit.session_state.product_1 = list(_products.keys())[0]  # Premier produit par défaut

if "product_2" not in lit.session_state:
    lit.session_state.product_2 = list(_products.keys())[1]  # Deuxième produit par défaut

# 🔹 Sélection des produits avec sauvegarde dans `st.session_state`
col1, col2 = lit.columns(2)

with col1:
    product_1 = lit.selectbox(
        "Select the first product:",
        options=list(_products.keys()),
        format_func=lambda x: _products[x],
        index=list(_products.keys()).index(lit.session_state.product_1),
        key="product_1"
    )

with col2:
    product_2 = lit.selectbox(
        "Select the second product:",
        options=list(_products.keys()),
        format_func=lambda x: _products[x],
        index=list(_products.keys()).index(lit.session_state.product_2),
        key="product_2"
    )

# 🔹 Vérification de compatibilité
if lit.button("Check compatibility", use_container_width=True):
    if product_1 == product_2:
        lit.warning("Choose 2 different products")
    else:
        with lit.spinner("Checking compatibility..."):
            molecules_1 = get_molecules(product_1)
            molecules_2 = get_molecules(product_2)
            incompatibles, neutrals = check_compatibility(molecules_1, molecules_2)

        if not incompatibles and not neutrals:
            lit.success("These products are compatible. ✅")
        elif not incompatibles and neutrals:
            lit.warning("These products are compatible but contain some neutral molecules. ⚠️")
            lit.table([{"Product 1 molecules": m1, "Product 2 molecules": m2} for m1, m2 in neutrals])
        else:
            lit.error("These products are not compatible. ❌")
            lit.table([{"Product 1 molecules": m1, "Product 2 molecules": m2} for m1, m2 in incompatibles])
            if neutrals:
                lit.warning("There are also neutral molecules:")
                lit.table([{"Product 1 molecules": m1, "Product 2 molecules": m2} for m1, m2 in neutrals])
