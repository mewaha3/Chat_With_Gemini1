
import streamlit as st
import pandas as pd
import google.generativeai as genai
import traceback

# ------------------------ Setup ------------------------

st.set_page_config(page_title="Gemini Chatbot with Data", layout="centered")

genai.configure(api_key=st.secrets["gemini_api_key"])
model = genai.GenerativeModel("gemini-2.0-flash-lite")

# ------------------------ Session State ------------------------

if "chat" not in st.session_state:
    st.session_state.chat = []

if "df" not in st.session_state:
    st.session_state.df = None

if "df_name" not in st.session_state:
    st.session_state.df_name = "uploaded_df"

# ------------------------ UI ------------------------

st.title("🤖 Gemini Chatbot + CSV Data Analysis")
st.caption("อัปโหลดไฟล์ข้อมูลแล้วถามคำถามเพื่อให้ Gemini ช่วยวิเคราะห์")

# Upload CSV
uploaded_file = st.file_uploader("📂 Upload your CSV file", type="csv")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df
        st.success("✅ File uploaded successfully!")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

# Show Chat History
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------------ Chat Input ------------------------

if prompt := st.chat_input("💬 ถามข้อมูลในไฟล์ หรือคำถามทั่วไปก็ได้..."):
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        if st.session_state.df is not None:
            df = st.session_state.df
            df_name = st.session_state.df_name
            sample_data = df.head(2).to_string()

            # Gemini Prompt
            prompt_code = f"""
You are a helpful Python code generator.
Your goal is to write Python code snippets based on the user's question
and the provided DataFrame information.

**User Question:**
{prompt}

**DataFrame Name:**
{df_name}

**Sample Data (Top 2 Rows):**
{sample_data}

**Instructions:**
1. Write Python code to answer the question using the DataFrame.
2. Use `exec()` to execute the code.
3. Store the result in a variable named `ANSWER`.
4. Do NOT import pandas or reload the data.

Example:

```python
query_result = {df_name}[{df_name}['age'] > 30]
ANSWER = query_result
```
"""

            # Generate Code
            response = model.generate_content(prompt_code)
            code_raw = response.text.strip().replace("```python", "").replace("```", "")

            with st.chat_message("assistant"):
                st.markdown("🧠 **Generated Code:**")
                st.code(code_raw, language="python")

                # Execute Code
                local_env = {df_name: df}
                exec(code_raw, {}, local_env)

                # Get Result
                answer = local_env.get("ANSWER", "❌ No variable named `ANSWER` found.")
                st.markdown("✅ **Result:**")
                st.write(answer)

            # Save to chat history
            st.session_state.chat.append({
                "role": "assistant",
                "content": f"Here's the result based on your question:\n\n```
{answer}
```"
            })

        else:
            st.warning("⚠️ Please upload a CSV file before asking data-related questions.")

    except Exception as e:
        err_msg = traceback.format_exc()
        st.error("❌ Error occurred while running the code.")
        st.exception(err_msg)
        st.session_state.chat.append({
            "role": "assistant",
            "content": f"❌ เกิดข้อผิดพลาด:\n\n```
{e}
```"
        })
