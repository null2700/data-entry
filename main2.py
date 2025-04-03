import streamlit as st
import pymysql
import pandas as pd

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Soham@456",  # Change this to your MySQL password
    "database": "soham"
}

# Establish MySQL Connection
def get_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except pymysql.MySQLError as e:
        st.error(f"❌ Database Connection Failed: {e}")
        return None

# Fetch Table Names
def get_table_names():
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    return []

# Fetch Student Names
def get_student_names(table):
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT Name FROM {table}")
            rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows] if rows else []
    return []

# Insert or Update Student Data
def insert_data(table):
    names = get_student_names(table)
    if not names:
        st.error("⚠️ No student names found! Add names first.")
        return

    selected_name = st.selectbox("Select Student", names)

    # Fetch column names excluding primary keys and 'Total'
    conn = get_connection()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = [col[0] for col in cursor.fetchall() if col[0] not in ["RollNo", "Name", "Total"]]

    data = {"Name": selected_name}
    for col in columns:
        data[col] = st.number_input(f"Enter {col} for {selected_name}", min_value=0, step=1, key=col)

    if st.button("Submit Data"):
        conn = get_connection()
        if conn:
            with conn.cursor() as cursor:
                query = f"UPDATE {table} SET {', '.join([f'{col} = %s' for col in columns])} WHERE Name = %s"
                cursor.execute(query, tuple(data[col] for col in columns) + (selected_name,))
                conn.commit()
            conn.close()
            st.success(f"✅ Data updated for {selected_name} in {table}")

# View Table Data
def view_data(table):
    conn = get_connection()
    if conn:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
        conn.close()
        return df
    return pd.DataFrame()

# Delete Student Data
def delete_data(table):
    names = get_student_names(table)
    if not names:
        st.error("⚠️ No student names found! Add names first.")
        return

    selected_name = st.selectbox("🗑️ Select Student to Delete", names, key="delete_name")

    if st.button("❌ Delete Record"):
        conn = get_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DELETE FROM {table} WHERE Name = %s", (selected_name,))
                conn.commit()
            conn.close()
            st.success(f"🗑️ Deleted {selected_name} from {table}!")

# Export Data to Excel
def export_all_to_excel():
    with pd.ExcelWriter("All_Data.xlsx") as writer:
        for table in get_table_names():
            df = view_data(table)
            if not df.empty:
                df.to_excel(writer, sheet_name=table, index=False)

    with open("All_Data.xlsx", "rb") as f:
        st.download_button(label="📥 Download All Data", data=f, file_name="All_Data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Streamlit UI
st.title("📊 Student Data Management System")

tables = get_table_names()
if tables:
    st.write("✅ Available Tables:", tables)
    table = st.selectbox("🔹 Select Table", tables)

    if table:
        st.subheader(f"📌 Add or Update Data in {table}")
        insert_data(table)

        st.subheader(f"📌 View {table} Data")
        st.dataframe(view_data(table))

        st.subheader(f"🗑️ Delete Student Data from {table}")
        delete_data(table)

        st.subheader("📥 Download All Data")
        export_all_to_excel()
else:
    st.warning("⚠️ No tables found in the database.")

