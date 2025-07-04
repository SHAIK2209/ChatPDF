import streamlit as st
from pdf_reader import extract_text_from_pdf
from qa_engine import split_text, create_vector_store, get_answer
import tempfile

st.set_page_config(page_title="PDF Q&A", layout="wide")
st.title("📘 Ask Questions About Your PDF")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # Extract text
    text = extract_text_from_pdf(tmp_path)
    st.subheader("📄 Preview Extracted Text")
    st.write(text[:500])

    # Split into chunks
    chunks = split_text(text)
    st.success(f"✅ Extracted {len(chunks)} text chunks.")

    # User sets chunk limit
    max_chunks = st.slider("🔧 Limit number of chunks used:", 100, 2000, 500, 100)
    if len(chunks) > max_chunks:
        st.warning(f"⚠️ Truncating to {max_chunks} chunks to keep it fast.")
        chunks = chunks[:max_chunks]

    if len(chunks) == 0:
        st.error("No valid text found in this PDF.")
    else:
        # Build vector store
        with st.spinner("🔍 Creating index..."):
            store = create_vector_store(chunks)

        # ✅ Show question box
        st.subheader("💬 Ask a Question About the PDF")
        question = st.text_input("Type your question below:")

        if question.strip():
            with st.spinner("🤖 Generating answer..."):
                answer = get_answer(question, store)
            st.markdown("### ✅ Answer:")
            st.write(answer)
else:
    st.info("👆 Please upload a PDF to begin.")
