from langchain_community.document_loaders import PyPDFLoader
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv

# Load environment variables (MISTRAL_API_KEY)
load_dotenv()

print("📄 Scanning resume.pdf...")
try:
    loader = PyPDFLoader("resume.pdf")
    docs = loader.load()
    resume_text = " ".join([page.page_content for page in docs])

    print("🧠 Analyzing skills via Mistral AI...")
    llm = ChatMistralAI(model="mistral-large-latest", temperature=0.1)
    
    prompt = (
        f"Analyze this resume: {resume_text}\n\n"
        "Extract the 6 most prominent, broad engineering competencies (e.g., 'Data Engineering', 'Machine Learning', 'DevOps'). "
        "Assign a realistic proficiency score out of 100 for each, based on the depth of experience shown. "
        "Return ONLY valid Python code defining two lists: 'categories = [...]' and 'skill_scores = [...]'. Do not include markdown blocks or any other text."
    )
    
    response = llm.invoke(prompt)
    print("\n✅ AI Extraction Complete. Paste this into your app.py:\n")
    print(response.content)

except Exception as e:
    print(f"Error: Make sure 'pypdf' is installed (pip install pypdf). Details: {e}")