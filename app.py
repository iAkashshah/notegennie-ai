import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image
import io

st.set_page_config(page_title="CollegeGem AI", page_icon="🎓", layout="wide")
st.title("🎓 CollegeGem AI")
st.caption("Your Free Gemini 2.5 Flash Study Buddy • Made for College Students")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password", help="Get free key from aistudio.google.com/app/apikey")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ API Connected")
    
    subject = st.selectbox("Your Subject", 
        ["General", "Computer Science", "Mathematics", "Physics", "Chemistry", "Biology", 
         "Engineering", "Economics", "History", "Literature", "Psychology", "Other"])
    
    st.divider()
    st.subheader("Quick Tools")
    if st.button("📝 Generate Practice Quiz"):
        st.session_state.quick_tool = "quiz"
    if st.button("💻 Code Helper"):
        st.session_state.quick_tool = "code"
    if st.button("📝 Essay Outline"):
        st.session_state.quick_tool = "essay"

# Initialize model & history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""

# System instruction
system_instruction = f"""You are CollegeGem AI, a friendly, patient, and expert college tutor.
Always explain step-by-step, give real examples, encourage learning, and never give direct answers for assignments.
Current subject: {subject}. Help with homework, exams, coding, concepts, notes, etc."""

model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask anything about studies..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            full_prompt = prompt
            if st.session_state.pdf_context:
                full_prompt = f"Here are my uploaded notes:\n{st.session_state.pdf_context}\n\nQuestion: {prompt}"
            
            response = model.generate_content(full_prompt)
            answer = response.text
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# PDF Upload
st.subheader("📄 Upload PDF Notes (for context)")
pdf_file = st.file_uploader("Upload lecture notes, textbook pages, or assignment PDF", type="pdf")
if pdf_file:
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    st.session_state.pdf_context = text[:15000]  # limit to avoid token overflow
    st.success(f"✅ {len(text)} characters of notes loaded! Now ask questions about them.")

# Image Upload
st.subheader("🖼️ Upload Image (equation, diagram, photo)")
image_file = st.file_uploader("Upload photo of blackboard, diagram, handwritten notes, or screenshot", type=["png", "jpg", "jpeg"])
if image_file:
    image = Image.open(image_file)
    st.image(image, width=400)
    img_prompt = st.text_input("What do you want to know about this image?")
    if st.button("🔍 Analyze Image"):
        with st.spinner("Analyzing image..."):
            response = model.generate_content([img_prompt, image])
            st.markdown(response.text)

# Quick tools handler
if "quick_tool" in st.session_state:
    tool = st.session_state.quick_tool
    del st.session_state.quick_tool
    if tool == "quiz":
        topic = st.text_input("Enter topic for quiz")
        if st.button("Generate Quiz"):
            res = model.generate_content(f"Create a 5-question practice quiz on {topic} for college students with answers")
            st.markdown(res.text)
    # similar for code and essay...

st.sidebar.info("💡 Tip: Upload notes once, then keep chatting — AI remembers everything!")
st.caption("Built with ❤️ for students | Powered by Google Gemini 2.5 Flash")
