import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt

# -------------------- Streamlit UI Setup --------------------
st.set_page_config(page_title="Gemini Data Chatbot", page_icon="🤖")
st.title("🤖 Gemini CSV Chatbot")
st.write("Upload your **CSV data** and optionally a **data dictionary**, then ask any question about your data!")

# -------------------- Gemini API Key --------------------
api_key = st.text_input("🔐 Enter your Gemini API Key", type="password")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro")
else:
    st.warning("Please provide your Gemini API Key.")

# -------------------- File Upload Section --------------------
st.markdown("### 📁 Upload Your Files")
data_file = st.file_uploader("Upload your main CSV data file", type=["csv"], key="data")
dict_file = st.file_uploader("Optional: Upload your data dictionary CSV", type=["csv"], key="dict")

# -------------------- Process Uploaded Files --------------------
if data_file and api_key:
    df = pd.read_csv(data_file)
    df_name = "df"

    # If dictionary is uploaded
    if dict_file:
        dict_df = pd.read_csv(dict_file)
        data_dict_text = '\n'.join(
            f"- {row['column_name']}: {row['data_type']}. {row['description']}"
            for _, row in dict_df.iterrows()
        )
    else:
        # Auto generate context from DataFrame itself
        data_dict_text = '\n'.join(
            f"- {col}: {dtype}" for col, dtype in df.dtypes.items()
        )

    # -------------------- Display Info --------------------
    st.subheader("🔍 Data Preview")
    st.dataframe(df.head(3))

    st.subheader("📖 Data Dictionary / Inferred Info")
    st.code(data_dict_text)

    # -------------------- Chat Area --------------------
    question = st.chat_input("💬 Ask a question about your data...")
    if question:
        with st.chat_message("user"):
            st.markdown(question)

        # Create prompt for Gemini
        sample_data = df.head(2).to_string()
        prompt = f"""
You are a Python data assistant.

Your task is to help answer the user's question using the provided DataFrame and column descriptions.

### User Question:
{question}

### DataFrame Name:
{df_name}

### DataFrame Column Info:
{data_dict_text}

### Sample Data (Top 2 Rows):
{sample_data}

### Instructions:
1. Analyze and explain how you interpret the question.
2. Write Python code that uses the DataFrame `{df_name}` to answer the question.
3. Use the `exec()` function to run your code.
4. Store the final result in a variable called `ANSWER`.
5. Do not import pandas or reload data.
6. Convert date columns to datetime if needed.

Your response format should be:

EXPLANATION:
<Explanation>

```python
# Python code here
```
"""

        try:
            # Generate content from Gemini
            response = model.generate_content(prompt)
            text = response.text

            # Split explanation and code
            if "```python" in text:
                explanation, code_block = text.split("```python")
                code = code_block.replace("```", "").strip()
            else:
                explanation = "Could not detect explanation/code format properly."
                code = ""

            # Show explanation and code
            st.markdown("### 🧠 Gemini Explanation")
            st.markdown(explanation.strip())

            st.markdown("### 💻 Generated Python Code")
            st.code(code, language="python")

            # Execute the code safely with context for pd and plt
            exec_locals = {df_name: df, 'pd': pd, 'plt': plt}
            plt.clf()
            exec(code, {}, exec_locals)
            answer = exec_locals.get("ANSWER")

            with st.chat_message("assistant"):
                if answer is not None:
                    st.markdown("### ✅ Answer")
                    st.write(answer)

                # Show chart if exists
                fig = plt.gcf()
                if fig.get_axes():
                    st.markdown("### 📊 Generated Chart")
                    st.pyplot(fig)

                # Ask Gemini to explain result
                explain_prompt = f"The user asked: {question}\nHere is the result: {answer}\nSummarize and explain:"
                try:
                    explanation = model.generate_content(explain_prompt).text
                    st.markdown("### 📝 Explanation of Result")
                    st.markdown(explanation)
                except Exception as e:
                    st.warning(f"(Optional) Could not get explanation: {e}")

        except Exception as e:
            st.error(f"❌ Error while processing:\n{e}")
else:
    st.info("📥 Please upload a CSV file and enter your Gemini API Key to begin.")
