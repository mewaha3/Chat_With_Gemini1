import streamlit as st
import pandas as pd
import google.generativeai as genai

# ตั้งค่า Gemini API Key
genai.configure(api_key=st.secrets["gemini_api_key"])

# สร้างโมเดล
model = genai.GenerativeModel("gemini-2.0-flash-lite")

# UI ส่วนหัว
st.title("🧠 Gemini AI: ถามตอบข้อมูลในไฟล์ CSV")

# อัปโหลดไฟล์
st.markdown("### 📂 Upload Files")
uploaded_data = st.file_uploader("**Upload Transaction CSV File**", type="csv", key="data")
uploaded_dict = st.file_uploader("**Upload Data Dictionary CSV File**", type="csv", key="dict")

# กรอกคำถาม
question = st.text_input("❓ ถามคำถามเกี่ยวกับข้อมูลของคุณที่นี่")

# ตรวจสอบว่าไฟล์ถูกอัปโหลดหรือยัง
if uploaded_data:
    st.success("✅ Transaction file uploaded")
if uploaded_dict:
    st.success("✅ Data dictionary uploaded")

# ตรวจสอบว่าทุกอย่างพร้อมแล้ว
if uploaded_data and uploaded_dict and question:
    try:
        # โหลดข้อมูล
        transaction_df = pd.read_csv(uploaded_data)
        data_dict_df = pd.read_csv(uploaded_dict)

        df_name = "transaction_df"
        example_record = transaction_df.head(2).to_string()
        data_dict_text = '\n'.join(
            '- ' + data_dict_df['column_name'] + ': ' +
            data_dict_df['data_type'] + '. ' +
            data_dict_df['description']
        )

        # สร้าง Prompt
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
7. Keep the generated code concise and focused on answering the question.
"""

        # ส่งไปให้โมเดล Gemini
        response = model.generate_content(prompt)
        generated_code = response.text.replace("```python", "").replace("```", "")

        st.subheader("🧾 Generated Python Code")
        st.code(generated_code, language="python")

        # รันโค้ดด้วย exec
        local_vars = {df_name: transaction_df}
        exec(generated_code, {}, local_vars)

        if "ANSWER" in local_vars:
            st.subheader("📊 Answer")
            st.write(local_vars["ANSWER"])
        else:
            st.warning("No variable named 'ANSWER' was created in the generated code.")

    except Exception as e:
        st.error(f"❌ Error: {e}")

else:
    st.info("กรุณาอัปโหลดไฟล์ทั้งสองและกรอกคำถามก่อนเริ่ม")
