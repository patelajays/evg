import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd
from pathlib import Path
from render_custom_table import render_custom_table

# Set page config before anything else
st.set_page_config(page_title="Secure Data Portal", layout="wide")

# Display logo
st.image("logo.svg", width=200)

st.title("🔐 Secure Data Portal")

# Load custom Evergreen CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("evergreen_style.css")

# Supabase setup
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Admin email from secrets
ADMIN_EMAIL = st.secrets["ADMIN_EMAIL"]

# Session check and login
if "user" not in st.session_state:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state['user'] = user
            st.success("Logged in successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")
else:
    email = st.session_state['user'].user.email
    st.write(f"Welcome, **{email}**")

    # Logout button
    if st.button("Logout"):
        supabase.auth.sign_out()
        del st.session_state['user']
        st.success("Logged out successfully.")
        st.rerun()

    if email == ADMIN_EMAIL:
        st.subheader("🛠 Admin Panel - All User Data")
        all_data = supabase.table("user_data").select("*").execute()
        df = pd.DataFrame(all_data.data or [])

        if not df.empty:
            user_filter = st.selectbox("Filter by user", ["All"] + sorted(df["email"].unique()))
            if user_filter != "All":
                df = df[df["email"] == user_filter]

            # Toggle view
            editable = st.toggle("✏️ Edit Mode", value=False)
            if editable:
                edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            else:
                st.markdown(render_custom_table(df), unsafe_allow_html=True)
        else:
            st.info("No data in the table yet.")

        st.markdown("### 📄 Upload CSV to Insert Data")
        csv_file = st.file_uploader("Upload CSV", type=["csv"])
        if csv_file:
            df_csv = pd.read_csv(csv_file).fillna("")
            st.write(df_csv)

            if st.button("Upload to Supabase"):
                try:
                    for _, row in df_csv.iterrows():
                        supabase.table("user_data").insert({
                            "empi": row["empi"],
                            "patient_name": row["patient_name"],
                            "dob": row["dob"],
                            "mbi": row["mbi"],
                            "disease_status": row["disease_status"],
                            "payer": row["payer"],
                            "market": row["market"],
                            "ppn": row["ppn"],
                            "asd": row["asd"],
                            "risk_model": row["risk_model"],
                            "eav": row["eav"],
                            "quarter": row["quarter"],
                            "email": row["email"],
                            "ppsd": row["ppsd"],
                            "ppss": row["ppss"],
                            "last_updated_by": "ADMIN"
                        }).execute()
                    st.success("Data uploaded successfully.")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    else:
        st.subheader("👤 Your Data")
        data = supabase.table("user_data").select("*").eq("email", email).execute()
        df = pd.DataFrame(data.data or [])

        if not df.empty:
            editable = st.toggle("✏️ Edit Mode", value=False)
            if editable:
                edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
                if st.button("Save Changes"):
                    for _, row in edited_df.iterrows():
                        supabase.table("user_data").update({
                            "empi": row["empi"],
                            "patient_name": row["patient_name"],
                            "dob": row["dob"],
                            "mbi": row["mbi"],
                            "disease_status": row["disease_status"],
                            "payer": row["payer"],
                            "market": row["market"],
                            "ppn": row["ppn"],
                            "asd": row["asd"],
                            "risk_model": row["risk_model"],
                            "eav": row["eav"],
                            "quarter": row["quarter"],
                            "email": row["email"],
                            "ppsd": row["ppsd"],
                            "ppss": row["ppss"],
                            "last_updated_by": email,
                            "updated_at": datetime.utcnow().isoformat()
                        }).eq("id", row["id"]).execute()
                    st.success("Changes saved.")
            else:
                st.markdown(render_custom_table(df), unsafe_allow_html=True)
        else:
            st.warning("No data found for your account.")
