import streamlit as st
import pandas as pd
import google.generativeai as genai
import textwrap

# -------------------- Setup --------------------
st.title("🧠 Gemini DataBot: Analyze CSV with AI")
st.subheader("Upload your CSV file and ask questions in natural language")

# Input API Key
api_key = st.text_input("🔐 Enter your Gemini API Key", type="password")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro")

# -------------------- File Upload --------------------
st.markdown("### 📂 Upload Required Files")
col1, col2 = st.columns(2)
with col1:
    data_file = st.file_uploader("Upload Transactions CSV", type="csv", key="data")
with col2:
    dict_file = st.file_uploader("Upload Data Dictionary CSV", type="csv", key="dict")

if data_file and dict_file:
    df = pd.read_csv(data_file)
    df_name = "df"
    data_dict_df = pd.read_csv(dict_file)

    # Format Data Dictionary
    data_dict_text = '\n'.join(
        '- ' + row['column_name'] + ': ' + row['data_type'] + '. ' + row['description']
        for _, row in data_dict_df.iterrows()
    )

    # Sample record
    example_record = df.head(2).to_string()

    # -------------------- Chat Input --------------------
    user_question = st.chat_input("Ask a question about your data...")
    if user_question and api_key:
        with st.chat_message("user"):
            st.markdown(user_question)

        # Build Prompt
        prompt = f"""
You are a helpful Python code generator.
Your goal is to write Python code snippets based on the user's question
and the provided DataFrame information.

Here's the context:

**User Question:**
{user_question}

**DataFrame Name:**
{df_name}

**DataFrame Details:**
{data_dict_text}

**Sample Data (Top 2 Rows):**
{example_record}

**Instructions:**
1. Write Python code that addresses the user's question by querying or manipulating the DataFrame.
2. Use the `exec()` function to execute the generated code.
3. Do not import pandas
4. Change date column type to datetime
5. Store the result of the executed code in a variable named `ANSWER`.
6. Assume the DataFrame is already loaded as `{df_name}`.
7. Keep the code concise and focused on the question.

Example:
query_result = {df_name}[{df_name}['age'] > 30]
"""

        try:
            response = model.generate_content(prompt)
            generated_code = response.text.replace("```python", "").replace("```", "")
            st.markdown("#### 🧠 Generated Code")
            st.code(generated_code, language="python")

            # Execute
            exec_locals = {"df": df}
            exec(generated_code, {}, exec_locals)
            ANSWER = exec_locals.get("ANSWER")

            with st.chat_message("assistant"):
                st.markdown("### ✅ Answer")
                st.write(ANSWER)

                # Ask Gemini to explain
                explain_prompt = f"The user asked: {user_question}\nHere is the result: {ANSWER}\nSummarize and explain:"
                explanation = model.generate_content(explain_prompt).text
                st.markdown("#### 📝 Explanation")
                st.markdown(explanation)

        except Exception as e:
            st.error(f"❌ Error: {e}")
else:
    st.info("Please upload both the transaction file and data dictionary to begin.")
