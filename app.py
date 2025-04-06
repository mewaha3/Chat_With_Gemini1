import streamlit as st
import google.generativeai as genai
import pandas as pd

try:
    # โหลด API Key
    key = st.secrets['gemini_api_key']
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')

    # เริ่ม Session Chat
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])
    
    st.title('🧠 Gemini Pro Chat + CSV Upload')
    st.markdown("พูดคุยกับ Gemini และให้มันช่วยวิเคราะห์ไฟล์ข้อมูลของคุณ")

    # ส่วนอัปโหลดไฟล์
    uploaded_file = st.file_uploader("📂 อัปโหลด CSV ที่ต้องการถาม", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("📄 แสดงตัวอย่างข้อมูล:")
        st.dataframe(df.head(5))
        st.session_state["df"] = df  # เก็บไว้ใช้ตอนถาม

    # แสดงประวัติการสนทนา
    def role_to_streamlit(role: str) -> str:
        return 'assistant' if role == 'model' else role

    for message in st.session_state.chat.history:
        with st.chat_message(role_to_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    # ช่องใส่คำถาม
    if prompt := st.chat_input("พิมพ์คำถามที่นี่ เช่น 'วิเคราะห์ยอดขายเดือนมกราคม 2024'"):
        df_info = ""
        if "df" in st.session_state:
            df = st.session_state["df"]
            df_info = f"\n\nHere's the data (top 3 rows):\n{df.head(3).to_string()}\n"

        st.chat_message('user').markdown(prompt)
        full_prompt = prompt + df_info

        response = st.session_state.chat.send_message(full_prompt)
        with st.chat_message('assistant'):
            st.markdown(response.text)

except Exception as e:
    st.error(f'เกิดข้อผิดพลาด: {e}')
