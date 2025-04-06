import streamlit as st
import pandas as pd
import google.generativeai as genai

# -------------------- Setup --------------------
st.title("🐧 Gemini Chatbot with Full CSV Analysis")
st.subheader("Upload your CSV file and ask any question")

# Gemini API Key input
gemini_api_key = st.text_input("Gemini API Key: ", placeholder="Type your API Key here...", type="password")

# Initialize Gemini model
model = None
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")
        st.success("Gemini API Key successfully configured.")
    except Exception as e:
        st.error(f"An error occurred while setting up the Gemini model: {e}")

# -------------------- Session State --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

# -------------------- Show Chat History --------------------
for role, message in st.session_state.chat_history:
    st.chat_message(role).markdown(message)

# -------------------- Upload CSV --------------------
st.subheader("Upload CSV for Analysis")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        st.session_state.uploaded_data = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")
        st.write("### Preview of Uploaded Data")
        st.dataframe(st.session_state.uploaded_data.head())
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")

# -------------------- Enable AI Analysis --------------------
analyze_data_checkbox = st.checkbox("Analyze CSV Data with AI")

# -------------------- Chat Input --------------------
if user_input := st.chat_input("Type your question about the data..."):
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").markdown(user_input)

    if model:
        try:
            if st.session_state.uploaded_data is not None and analyze_data_checkbox:
                df = st.session_state.uploaded_data.copy()

                # สรุปข้อมูล column
                column_info = ", ".join(f"{col} ({df[col].dtype})" for col in df.columns)

                # ✅ ส่งข้อมูลทั้งไฟล์
                data_text = df.to_csv(index=False)

                # สร้าง prompt เต็ม
                prompt = f"""
You are a helpful data analysis assistant.

The user uploaded a CSV file with the following columns:
{column_info}

Here is the entire dataset:
{data_text}

Now please answer this question using the data:
{user_input}
"""

                response = model.generate_content(prompt)
                bot_response = response.text
            else:
                # ถ้าไม่วิเคราะห์ไฟล์ ก็ถามทั่วไป
                response = model.generate_content(user_input)
                bot_response = response.text

            st.session_state.chat_history.append(("assistant", bot_response))
            st.chat_message("assistant").markdown(bot_response)

        except Exception as e:
            st.error(f"An error occurred while generating the response: {e}")
    else:
        st.warning("Please configure the Gemini API Key to enable chat responses.")
