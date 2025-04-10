
import streamlit as st

def render_custom_table(df):
    html = '<table style="width:100%; border-collapse: collapse; font-size: 14px;">'
    html += "<thead><tr>"
    for col in df.columns:
        html += f'<th style="background-color:#4CAF50; color:white; padding:10px; text-align:left;">{col}</th>'
    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            value = row.get(col, "")
            # Clean the value before rendering
            if isinstance(value, str):
                value = value.strip()
            html += f'<td style="padding:10px; border-bottom:1px solid #ddd;">{value}</td>'
        html += "</tr>"
    html += "</tbody></table>"
    return html
