import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# Supabase setup
SUPABASE_URL = "https://mnqfojbkscjdjqzejjpe.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ucWZvamJrc2NqZGpxemVqanBlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQyMDc0NTIsImV4cCI6MjA1OTc4MzQ1Mn0.n8Pi5OBferrerQ3CixtNGuMo2q53sCj_7N7B8HY83P8"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# User authentication
st.title("🔐 Secure Data Portal")

if 'user' in st.session_state and st.session_state['user'].user.email == "patelajays@email.com":
    default_page = "Admin Panel"
else:
    default_page = "User View"

page = st.sidebar.selectbox("Choose a page", ["User View", "Admin Panel"], index=["User View", "Admin Panel"].index(default_page))

if page == "User View":
    # Existing login + user-specific table logic here
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if user:
            st.session_state['user'] = user
            st.success("Logged in!")
        else:
            st.error("Login failed")

    if 'user' in st.session_state:
        email = st.session_state['user'].user.email
        st.write(f"Welcome, {email}!")

        # Fetch user data
        data = supabase.table("user_data").select("*").eq("user_email", email).execute()
        df = pd.DataFrame(data.data)

        if not df.empty:
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

            if st.button("Save Changes"):
                for _, row in edited_df.iterrows():
                    supabase.table("user_data").update({
                        "data_field_1": row["data_field_1"],
                        "data_field_2": row["data_field_2"],
                        "last_updated_by": email,
                        "updated_at": datetime.utcnow().isoformat()
                    }).eq("id", row["id"]).execute()
                st.success("Changes saved.")
        else:
            st.warning("No data found for you.")

# Admin Panel
elif page == "Admin Panel":
    st.title("🔎 Admin Panel - All User Data")

    # Basic auth: only allow access if you're logged in with admin email
    if 'user' not in st.session_state or st.session_state['user'].user.email != "patelajays@gmail.com":
        st.warning("You must be the admin to access this page.")
    else:
        # Load all data
        all_data = supabase.table("user_data").select("*").execute()
        df = pd.DataFrame(all_data.data)

        if not df.empty:
            user_filter = st.selectbox("Filter by user", ["All"] + sorted(df["user_email"].unique()))
            if user_filter != "All":
                df = df[df["user_email"] == user_filter]

            st.dataframe(df)
        else:
            st.info("No data in the table yet.")

        st.markdown("### 📤 Upload CSV to Insert Data")
        csv_file = st.file_uploader("Upload CSV", type=["csv"])
        if csv_file:
            df_csv = pd.read_csv(csv_file)
            st.write(df_csv)

            if st.button("Upload to Supabase"):
                # Upload each row
                try:
                    for _, row in df_csv.iterrows():
                        supabase.table("user_data").insert({
                            "user_email": row["user_email"],
                            "data_field_1": row["data_field_1"],
                            "data_field_2": row["data_field_2"],
                            "last_updated_by": "admin"
                        }).execute()
                    st.success("Data uploaded successfully.")
                except Exception as e:
                    st.error(f"Upload failed: {e}")
