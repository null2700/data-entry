import streamlit as st
import mysql.connector
import pandas as pd
import os

# Streamlit App Title
st.title("📊 MySQL Database Management with Streamlit")

# MySQL Connection Function
def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),  # Change if hosted elsewhere
            user=os.getenv("MYSQL_USER", "root"),       # Your MySQL username
            password=os.getenv("MYSQL_PASS", "Soham@456"),    # Your MySQL password
            database=os.getenv("MYSQL_DB", "soham"),    # Your database name
            port=3306  # Ensure MySQL is running on this port
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"❌ Database Connection Failed: {err}")
        return None

# Fetch Table Names
def get_table_names():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    return []

# Fetch Data from a Table
def fetch_data(table):
    conn = get_connection()
    if conn:
        query = f"SELECT * FROM {table}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return None

# Insert Data into Table
def insert_data(table, data):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        columns = ", ".join(data.keys())
        values = tuple(data.values())
        placeholders = ", ".join(["%s"] * len(values))
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        st.success(f"✅ Data inserted into {table} successfully!")

# Delete Data from Table
def delete_data(table, column, value):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        query = f"DELETE FROM {table} WHERE {column} = %s"
        cursor.execute(query, (value,))
        conn.commit()
        conn.close()
        st.success(f"🗑️ Deleted record from {table} where {column} = {value}")

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

