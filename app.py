import streamlit as st
import pandas as pd
import google.generativeai as genai

# กำหนด API Key
genai.configure(api_key=st.secrets['gemini_api_key'])

model = genai.GenerativeModel('gemini-2.0-flash-lite')

st.title("🔍 Gemini Data Analyst Bot")
st.markdown("อัปโหลดไฟล์ข้อมูลและถามคำถามเกี่ยวกับข้อมูลได้เลย")

# Upload CSV
data_file = st.file_uploader("📂 Upload Transactions CSV", type="csv")
dict_file = st.file_uploader("📂 Upload Data Dictionary CSV", type="csv")

# รับคำถามจากผู้ใช้
question = st.text_input("💬 What is your question about the data?")

# เริ่มทำงานเมื่ออัปโหลดครบและมีคำถาม
if data_file and dict_file and question:
    try:
        # โหลด DataFrame
        transaction_df = pd.read_csv(data_file)
        data_dict_df = pd.read_csv(dict_file)

        df_name = 'transaction_df'
        example_record = transaction_df.head(2).to_string()
        data_dict_text = '\n'.join(
            '- ' + data_dict_df['column_name'] + ': ' +
            data_dict_df['data_type'] + '. ' +
            data_dict_df['description']
        )

        # 🧠 Prompt สำหรับสร้างโค้ด
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
2. **Crucially, use the `exec()` function to execute the generated code.**
3. Do not import pandas
4. Change date column type to datetime
5. **Store the result of the executed code in a variable named `ANSWER`.**
6. Assume the DataFrame is already loaded into a pandas DataFrame object named `{df_name}`.
"""

        # เรียก Gemini ให้เขียนโค้ด
        response = model.generate_content(prompt)
        generated_code = response.text.replace("```python", "").replace("```", "")
        st.subheader("💡 Generated Code")
        st.code(generated_code, language='python')

        # รันโค้ด
        local_vars = {df_name: transaction_df}
        exec(generated_code, {}, local_vars)

        if "ANSWER" in local_vars:
            answer = local_vars["ANSWER"]
            st.subheader("📊 Answer")
            st.write(answer)

            # ให้ Gemini อธิบายผล
            explanation_prompt = f'''
The user asked: {question}
Here is the result: {answer}

Please summarize the result in plain English and give your opinion on what this customer might want.
'''
            explain_response = model.generate_content(explanation_prompt)
            st.subheader("🧠 Explanation from Gemini")
            st.markdown(explain_response.text)

        else:
            st.warning("❌ No 'ANSWER' variable was found in generated code.")

    except Exception as e:
        st.error(f"⚠️ Error occurred: {e}")
else:
    st.info("📌 กรุณาอัปโหลดทั้งสองไฟล์และกรอกคำถามก่อนเริ่ม")
