import streamlit as st
import pandas as pd
import google.generativeai as genai
import textwrap

# -------------------- Setup --------------------
st.set_page_config(page_title="Gemini CSV Chatbot", page_icon="📊")
st.title("📊 Gemini CSV Chatbot with Data Dictionary")
st.write("Upload your **CSV data** and **data dictionary**, then ask any data question!")

# Gemini API Key
api_key = st.text_input("🔐 Enter your Gemini API Key", type="password")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro")

# -------------------- Upload Files --------------------
st.markdown("### 📂 Upload Files")
data_file = st.file_uploader("Upload your main CSV data file", type=["csv"], key="data")
dict_file = st.file_uploader("Upload your data dictionary CSV", type=["csv"], key="dict")

# -------------------- Process Files --------------------
if data_file and dict_file and api_key:
    df = pd.read_csv(data_file)
    df_name = "df"
    data_dict_df = pd.read_csv(dict_file)

    # สร้างคำอธิบายคอลัมน์จาก data dictionary
    data_dict_text = '\n'.join(
        f"- {row['column_name']}: {row['data_type']}. {row['description']}"
        for _, row in data_dict_df.iterrows()
    )

    # แสดงตัวอย่างข้อมูล
    st.subheader("📌 Data Preview")
    st.dataframe(df.head(2))

    st.subheader("📌 Data Dictionary Summary")
    st.code(data_dict_text)

    # -------------------- Chat Interface --------------------
    question = st.chat_input("💬 Ask a question about your data...")
    if question:
        with st.chat_message("user"):
            st.markdown(question)

        # สร้าง prompt ให้ Gemini ตาม format
        example_record = df.head(2).to_string()
        prompt = f"""
You are a helpful Python code generator.
Your goal is to write Python code snippets based on the user's question
and the provided DataFrame information.

Here's the context:

**User Question:**
{question}

**DataFrame Name:**
{df_name}

**DataFrame Details:**
{data_dict_text}

**Sample Data (Top 2 Rows):**
{example_record}

**Instructions:**
1. Write Python code that addresses the user's question by querying or manipulating the DataFrame.
2. Use the `exec()` function to execute the generated code.
3. Do not import pandas.
4. Change date column type to datetime if needed.
5. Store the result in a variable named `ANSWER`.
6. Assume the DataFrame is already loaded as `{df_name}`.
7. Keep the code concise and focused on answering the question.

Example:
query_result = {df_name}[{df_name}['age'] > 30]
"""

        try:
            # ส่ง prompt ไปที่ Gemini
            response = model.generate_content(prompt)
            generated_code = response.text.replace("```python", "").replace("```", "")
            
            st.markdown("#### 🧠 Generated Code")
            st.code(generated_code, language="python")

            # Execute the generated code
            exec_locals = {df_name: df}
            exec(generated_code, {}, exec_locals)
            result = exec_locals.get("ANSWER")

            with st.chat_message("assistant"):
                st.markdown("### ✅ Result")
                st.write(result)

                # ถาม Gemini เพื่ออธิบายผลลัพธ์
                explanation_prompt = f"The user asked: {question}\nHere is the result: {result}\nSummarize and explain:"
                explanation = model.generate_content(explanation_prompt).text
                st.markdown("### 📝 Explanation")
                st.markdown(explanation)

        except Exception as e:
            st.error(f"❌ Error occurred while generating or running the code:\n{e}")
else:
    st.info("📥 Please upload both data and data dictionary files and provide your Gemini API Key.")
