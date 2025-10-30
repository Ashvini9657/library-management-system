import streamlit as st
import pandas as pd
import datetime
from database import get_connection, create_tables

# Initialize database and tables
st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")
st.title("📚 Library Management System")

# Create all tables automatically when app starts
create_tables()

# Sidebar menu
menu = [
    "Add Book", "View Books", "Add Member", "View Members",
    "Issue Book", "View Issued Books", "Return Book"
]
choice = st.sidebar.selectbox("Menu", menu)

# ------------------- ADD BOOK -------------------
if choice == "Add Book":
    st.subheader("➕ Add New Book")
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    year = st.number_input("Year", min_value=1800, max_value=2100, step=1)

    if st.button("Add Book"):
        if title and author:
            conn = get_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO books (title, author, year, status) VALUES (%s, %s, %s, %s)",
                (title, author, year, "Available"),
            )
            conn.commit()
            conn.close()
            st.success(f"✅ Book '{title}' added successfully!")
        else:
            st.warning("⚠️ Please fill in all fields.")

# ------------------- VIEW BOOKS -------------------
elif choice == "View Books":
    st.subheader("📘 All Books")
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM books", conn)
    conn.close()

    if df.empty:
        st.info("No books found. Add some books first!")
    else:
        st.dataframe(df)

# ------------------- ADD MEMBER -------------------
elif choice == "Add Member":
    st.subheader("👤 Add New Member")
    name = st.text_input("Member Name")
    email = st.text_input("Email")

    if st.button("Add Member"):
        if name and email:
            conn = get_connection()
            c = conn.cursor()
            c.execute("INSERT INTO members (name, email) VALUES (%s, %s)", (name, email))
            conn.commit()
            conn.close()
            st.success(f"✅ Member '{name}' added successfully!")
        else:
            st.warning("⚠️ Please fill in all fields.")

# ------------------- VIEW MEMBERS -------------------
elif choice == "View Members":
    st.subheader("👥 Library Members")
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM members", conn)
    conn.close()

    if df.empty:
        st.info("No members found. Add members first!")
    else:
        st.dataframe(df)

# ------------------- ISSUE BOOK -------------------
elif choice == "Issue Book":
    st.subheader("📖 Issue a Book")
    conn = get_connection()
    books = pd.read_sql("SELECT * FROM books WHERE status='Available'", conn)
    members = pd.read_sql("SELECT * FROM members", conn)

    if not books.empty and not members.empty:
        book = st.selectbox("Select Book", books["title"])
        member = st.selectbox("Select Member", members["name"])
        issue_date = datetime.date.today()

        if st.button("Issue Book"):
            # ✅ Convert to Python int (fix for numpy.int64 error)
            book_id = int(books.loc[books["title"] == book, "id"].values[0])
            member_id = int(members.loc[members["name"] == member, "id"].values[0])

            c = conn.cursor()
            c.execute(
                "INSERT INTO issued_books (book_id, member_id, issue_date) VALUES (%s, %s, %s)",
                (book_id, member_id, issue_date),
            )
            c.execute("UPDATE books SET status='Issued' WHERE id=%s", (book_id,))
            conn.commit()
            st.success(f"✅ Book '{book}' issued to {member} successfully!")
    else:
        st.warning("⚠️ Add books and members before issuing.")
    conn.close()


# ------------------- VIEW ISSUED BOOKS -------------------
elif choice == "View Issued Books":
    st.subheader("📙 Issued Books")
    conn = get_connection()
    query = """
        SELECT i.id, b.title, m.name, i.issue_date, i.return_date
        FROM issued_books i
        JOIN books b ON i.book_id = b.id
        JOIN members m ON i.member_id = m.id
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        st.info("No books have been issued yet.")
    else:
        st.dataframe(df)

# ------------------- RETURN BOOK -------------------
elif choice == "Return Book":
    st.subheader("📚 Return a Book")
    conn = get_connection()
    issued = pd.read_sql(
        """
        SELECT ib.id, b.title, m.name, ib.issue_date
        FROM issued_books ib
        JOIN books b ON ib.book_id = b.id
        JOIN members m ON ib.member_id = m.id
        WHERE ib.return_date IS NULL
        """,
        conn,
    )

    if not issued.empty:
        issued["label"] = issued["title"] + " - " + issued["name"]
        selected = st.selectbox("Select Issued Book", issued["label"])

        if st.button("Return Book"):
            issue_id = int(issued.loc[issued["label"] == selected, "id"].values[0])  # ✅ convert numpy.int64 to int
            book_title = issued.loc[issued["label"] == selected, "title"].values[0]
            book_id = int(pd.read_sql("SELECT id FROM books WHERE title=%s", conn, params=(book_title,))["id"].values[0])

            c = conn.cursor()
            c.execute("UPDATE issued_books SET return_date=%s WHERE id=%s", (datetime.date.today(), issue_id))
            c.execute("UPDATE books SET status='Available' WHERE id=%s", (book_id,))
            conn.commit()
            st.success(f"✅ Book '{book_title}' returned successfully!")
    else:
        st.info("ℹ️ No books currently issued.")
    conn.close()

