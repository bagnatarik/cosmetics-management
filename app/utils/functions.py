import streamlit as lit
from sqlalchemy import create_engine
from oracledb import makedsn

@lit.cache_resource
def get_connection():
    dsn = makedsn("localhost", 1521, service_name="ORCLCDB")
    connection_string = f"oracle+oracledb://C##Tarik:tarik@{dsn}"
    return create_engine(connection_string)