import PyPDF2

def extract_text_from_pdf(pdf_path):
    """Extracts the full text from a PDF."""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or ""
    return full_text

def extract_qa_from_pdf(pdf_path):
    """Extracts question-answer pairs from a PDF."""
    text = extract_text_from_pdf(pdf_path)
    lines = text.split("\n")
    qa_pairs = []
    question = None

    for line in lines:
        if line.strip().endswith("?"):  # Identify questions
            if question:
                qa_pairs.append((question, answer.strip()))
            question = line.strip()
            answer = ""
        elif question:
            answer += " " + line.strip()

    if question and answer.strip():
        qa_pairs.append((question, answer.strip()))
    
    return qa_pairs

def chunk_text(text, max_length=500, overlap=100):
    """Splits text into overlapping chunks."""
    words = text.split()
    chunks = [
        " ".join(words[i:i + max_length])
        for i in range(0, len(words), max_length - overlap)
    ]
    return chunks