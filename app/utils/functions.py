import streamlit as lit
from sqlalchemy import create_engine
import oracledb

@lit.cache_resource
def get_connection():
    connection_string = f"oracle+oracledb://{lit.secrets["db"]["user"]}:{lit.secrets["db"]["password"]}@{lit.secrets["db"]["dsn"]}"
    return create_engine(connection_string)