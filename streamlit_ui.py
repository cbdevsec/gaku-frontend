import streamlit as st
import fitz  # PyMuPDF for PDF processing
import nltk
import requests
import matplotlib.pyplot as plt
import networkx as nx
import random
from nltk.tokenize import sent_tokenize
import os 


# 🔹 Configure API URL
API_URL = "http://127.0.0.1:5000"

# 🔹 Force NLTK to use a local directory
nltk.data.path.append(os.path.join(os.path.dirname(__file__), "nltk_data"))

# 🔹 Function to extract text from a PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

# 🔹 Function to generate a mind map
def generate_mindmap(text):
    sentences = sent_tokenize(text)[:10]
    G = nx.Graph()
    
    for i, sentence in enumerate(sentences):
        G.add_node(i, label=sentence)

    for i in range(len(sentences) - 1):
        G.add_edge(i, i + 1)

    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, 'label')

    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightblue', edge_color='gray')
    plt.savefig("mindmap.png")
    st.image("mindmap.png")

# 🔹 Function to generate flashcards
def generate_flashcards(text, num_cards=5):
    sentences = sent_tokenize(text)[:num_cards]
    flashcards = []
    
    for sentence in sentences:
        words = sentence.split()
        if len(words) > 4:
            missing_word = random.choice(words)
            question = sentence.replace(missing_word, "_____")
            flashcards.append((question, missing_word))
    
    return flashcards

# 🔹 Function to fetch study history from Flask
def get_study_history(user_id):
    response = requests.get(f"{API_URL}/get-study-history/{user_id}")
    
    if response.status_code == 200:
        return response.json()
    else:
        return None
    

# ✅ Streamlit UI
st.title("📚 AI Study Assistant")

# 🔹 User Login
user_id = st.text_input("Enter User ID")

# 🔹 Upload PDF
uploaded_file = st.file_uploader("📄 Upload a PDF", type="pdf")

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("📜 **Extracting text...**")
    text = extract_text_from_pdf("temp.pdf")

    st.write("📄 **Extracted Text Preview:**")
    st.text_area("Extracted Text", text[:1000])

    # 🔹 Generate Mindmap
    if st.button("🧠 Generate Mindmap"):
        generate_mindmap(text)

    # 🔹 Generate Flashcards
    if st.button("📚 Generate Flashcards"):
        flashcards = generate_flashcards(text)
        for i, (question, answer) in enumerate(flashcards):
            st.write(f"**Q{i+1}:** {question}")
            st.write(f"🔹 *Answer:* |||| *(Click to reveal)*")
            st.write("---")

   #

st.title("🔐 Login to AI Study Assistant")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    response = requests.post("http://127.0.0.1:5000/login", json={"email": email, "password": password})
    if response.status_code == 200:
        st.success("✅ Login successful!")
    else:
        st.error("❌ Invalid credentials.")

if st.button("📊 View Dashboard"):
    response = requests.get(f"http://127.0.0.1:5000/get-dashboard/{user_id}")
    if response.status_code == 200:
        stats = response.json()
        st.write(f"📚 **Total Flashcards Created**: {stats['flashcards_created']}")
        st.write(f"🎯 **Total Quizzes Taken**: {stats['quizzes_taken']}")
    else:
        st.error("❌ Failed to load dashboard data.")


# 🔹 View Study History
if st.button("🔍 View History"):
    history = get_study_history(user_id)
    if history:
        for entry in history:
            st.write(f"📌 **Type**: {entry['type']}")
            st.write(f"📄 **Content**: {entry['content']}")
            st.write("---")
    else:
        st.error("❌ No history found.")
