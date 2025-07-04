from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# ✅ 1. Split PDF text into optimized chunks (for speed)
def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,       # larger chunks = fewer = faster
        chunk_overlap=50
    )
    return splitter.split_text(text)

# ✅ 2. Create FAISS vector store using HuggingFace Embeddings
def create_vector_store(chunks):
    if not chunks:
        raise ValueError("⚠️ No content found in PDF to index.")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    store = FAISS.from_texts(chunks, embeddings)
    return store

# ✅ 3. Generate answer using flan-t5-base (smarter local model)
def get_answer(query, vector_store):
    docs = vector_store.similarity_search(query, k=1)  # top-1 result = faster
    context = "\n".join([doc.page_content for doc in docs])

    model_name = "google/flan-t5-base"  # Better accuracy, good speed
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, max_length=256)

    # 🧠 Optimized prompt for clear Q&A
    prompt = f"Answer the question based on the following context:\n\nContext: {context}\n\nQuestion: {query}\n\nAnswer:"
    result = pipe(prompt)[0]['generated_text']
    print("✅ Prompt:", prompt)
    print("✅ Answer:", result)
    return result
