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
        model = genai.GenerativeModel("gemini-1.0-pro")  # ✅ แก้ชื่อโมเดลให้ถูกต้อง
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

                if "analyze" in user_input.lower() or "insight" in user_input.lower():
                    # ✅ ส่งข้อมูลจริงไปยัง Gemini
                    data_description = df.describe(include="all").to_string()
                    data_head = df.head(5).to_string()

                    prompt = f"""
The user uploaded a CSV dataset. Below is the summary and the first few rows:

Summary Statistics:
{data_description}

Sample Rows:
{data_head}

Now answer the following question based on the data:

{user_input}
"""
                    response = model.generate_content(prompt)
                    bot_response = response.text
                else:
                    # 🔁 ปล่อยให้ Gemini ตอบคำถามทั่วไป
                    response = model.generate_content(user_input)
                    bot_response = response.text

                st.session_state.chat_history.append(("assistant", bot_response))
                st.chat_message("assistant").markdown(bot_response)

            elif not analyze_data_checkbox:
                bot_response = "Data analysis is disabled. Please select the 'Analyze CSV Data with AI' checkbox to enable analysis."
                st.session_state.chat_history.append(("assistant", bot_response))
                st.chat_message("assistant").markdown(bot_response)
            else:
                bot_response = "Please upload a CSV file first, then ask me to analyze it."
                st.session_state.chat_history.append(("assistant", bot_response))
                st.chat_message("assistant").markdown(bot_response)

        except Exception as e:
            st.error(f"An error occurred while generating the response: {e}")
    else:
        st.warning("Please configure the Gemini API Key to enable chat responses.")
