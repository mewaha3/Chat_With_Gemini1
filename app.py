import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Gemini Chatbot with CSV", layout="centered")

try:
    key = st.secrets['gemini_api_key']
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')

    # เตรียม session state
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])
    if "df" not in st.session_state:
        st.session_state.df = None
    if "df_name" not in st.session_state:
        st.session_state.df_name = "uploaded_df"

    st.title("📊 Gemini Pro Chatbot + CSV Analyzer")

    # อัปโหลดไฟล์ CSV
    uploaded_file = st.file_uploader("📂 Upload CSV file to analyze", type="csv")
    if uploaded_file:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")
        st.write("🔍 Sample Data:")
        st.dataframe(st.session_state.df.head())

    # ฟังก์ชันแปลง role
    def role_to_streamlit(role: str) -> str:
        return 'assistant' if role == 'model' else role

    # แสดงประวัติแชท
    for message in st.session_state.chat.history:
        with st.chat_message(role_to_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    # กล่องแชท
    if prompt := st.chat_input("💬 Ask about your data or anything..."):

        # ถ้ามีไฟล์อยู่ ก็แนบข้อมูลตัวอย่างเข้าไปใน prompt
        if st.session_state.df is not None:
            df = st.session_state.df
            df_name = st.session_state.df_name
            example_record = df.head(3).to_string()
            full_prompt = f"""
The user uploaded a DataFrame named `{df_name}`. Below are the first 3 rows:

{example_record}

Now answer the user's question based on this data:

{prompt}
"""
        else:
            full_prompt = prompt

        # แสดงคำถาม
        st.chat_message("user").markdown(prompt)

        # ส่ง prompt ไปให้ Gemini
        response = st.session_state.chat.send_message(full_prompt)

        # แสดงคำตอบ
        with st.chat_message("assistant"):
            st.markdown(response.text)

except Exception as e:
    st.error(f"An error occurred: {e}")
