import streamlit as st
import pandas as pd
import google.generativeai as genai

# -------------------- Setup --------------------
st.title("🐧 My Chatbot and Data Analysis App")
st.subheader("Conversation and Data Analysis")

# Gemini API Key input
gemini_api_key = st.text_input("Gemini API Key: ", placeholder="Type your API Key here...", type="password")

# Initialize Gemini model
model = None
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")  # ใช้ชื่อโมเดลที่ถูกต้อง
        st.success("Gemini API Key successfully configured.")
    except Exception as e:
        st.error(f"An error occurred while setting up the Gemini model: {e}")

# -------------------- Session State --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

# -------------------- Chat History --------------------
for role, message in st.session_state.chat_history:
    st.chat_message(role).markdown(message)

# -------------------- Upload CSV --------------------
st.subheader("Upload CSV for Analysis")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        st.session_state.uploaded_data = pd.read_csv(uploaded_file)
        st.success("File successfully uploaded and read.")
        st.write("### Uploaded Data Preview")
        st.dataframe(st.session_state.uploaded_data.head())
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")

# -------------------- Analysis Checkbox --------------------
analyze_data_checkbox = st.checkbox("Analyze CSV Data with AI")

# -------------------- Chat Input --------------------
if user_input := st.chat_input("Type your message here..."):
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").markdown(user_input)

    if model:
        try:
            if st.session_state.uploaded_data is not None and analyze_data_checkbox:
                df = st.session_state.uploaded_data
                df_name = "uploaded_data"

                # ✅ สร้าง prompt พร้อมข้อมูลจาก DataFrame จริง
                column_info = ", ".join(f"{col} ({df[col].dtype})" for col in df.columns)
                data_head = df.head(10).to_csv(index=False)

                prompt = f"""
You are a data analysis assistant. The user uploaded a CSV file with the following columns:
{column_info}

Here are the first 10 rows of the data:
{data_head}

Now answer the following question using this data:

{user_input}
"""

                response = model.generate_content(prompt)
                bot_response = response.text

            else:
                # ถ้าไม่ได้ให้วิเคราะห์ไฟล์ ใช้แค่ข้อความถามตอบปกติ
                prompt = user_input
                response = model.generate_content(prompt)
                bot_response = response.text

            st.session_state.chat_history.append(("assistant", bot_response))
            st.chat_message("assistant").markdown(bot_response)

        except Exception as e:
            st.error(f"An error occurred while generating the response: {e}")
    else:
        st.warning("Please configure the Gemini API Key to enable chat responses.")
