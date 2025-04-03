import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
import os

# Streamlit App Title
st.title("📊 MySQL Database Management with Streamlit & SQLAlchemy")

# Database Configuration
DB_USER = os.getenv("MYSQL_USER", "root")  # Change if needed
DB_PASS = os.getenv("MYSQL_PASS", "Soham@456")   # Change to your MySQL password
DB_HOST = os.getenv("MYSQL_HOST", "localhost")  # MySQL server address
DB_NAME = os.getenv("MYSQL_DB", "soham")   # Change to your database name

# Create SQLAlchemy Engine
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")

# Fetch Table Names
def get_table_names():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES;"))
            return [row[0] for row in result]
    except Exception as e:
        st.error(f"❌ Error fetching tables: {e}")
        return []

# Fetch Data from a Table
def fetch_data(table):
    try:
        with engine.connect() as conn:
            query = f"SELECT * FROM {table}"
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return None

# Insert Data into Table
def insert_data(table, data):
    try:
        with engine.connect() as conn:
            query = text(f"INSERT INTO {table} ({', '.join(data.keys())}) VALUES ({', '.join([':' + key for key in data.keys()])})")
            conn.execute(query, data)
            conn.commit()
        st.success(f"✅ Data inserted into {table} successfully!")
    except Exception as e:
        st.error(f"❌ Error inserting data: {e}")

# Delete Data from Table
def delete_data(table, column, value):
    try:
        with engine.connect() as conn:
            query = text(f"DELETE FROM {table} WHERE {column} = :value")
            conn.execute(query, {"value": value})
            conn.commit()
        st.success(f"🗑️ Deleted record from {table} where {column} = {value}")
    except Exception as e:
        st.error(f"❌ Error deleting data: {e}")

# Streamlit UI
st.subheader("🔹 Available Tables")
tables = get_table_names()

if tables:
    st.write("✅ Available Tables:", tables)
    selected_table = st.selectbox("🔹 Select Table", tables)

    if selected_table:
        st.subheader(f"📌 View Data in {selected_table}")
        df = fetch_data(selected_table)
        if df is not None:
            st.dataframe(df)

        st.subheader(f"📌 Insert Data into {selected_table}")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Enter Name")
        with col2:
            score = st.number_input("Enter Score", min_value=0, step=1)

        if st.button("Submit Data"):
            insert_data(selected_table, {"Name": name, "Score": score})

        st.subheader(f"🗑️ Delete Data from {selected_table}")
        if not df.empty:
            delete_name = st.selectbox("Select Name to Delete", df["Name"])
            if st.button("❌ Delete Record"):
                delete_data(selected_table, "Name", delete_name)

else:
    st.warning("⚠️ No tables found in the database.")
