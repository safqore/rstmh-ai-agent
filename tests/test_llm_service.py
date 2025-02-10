import pytest
from app.services.llm_service import get_llm_response

# Sample context and chat history for testing
TEST_CONTEXT = "The RSTMH Early Career Grants Programme provides early-career researchers with funding for global health research."
TEST_CHAT_HISTORY = "User: What grants are available?\nBot: The RSTMH Early Career Grants Programme offers funding for early-career researchers."

@pytest.mark.parametrize("query, expected_keywords", [
    # ✅ Test 1: Fully English query about grants (should be answered normally)
    ("What is the RSTMH Early Career Grants Programme?", [
        "RSTMH Early Career Grants Programme", "funding", "early-career researchers"
    ]),

    # ✅ Test 2: Fully English unrelated query (should be politely rejected)
    ("Tell me about space exploration.", [
        "I'm sorry", "only provide information", "RSTMH Early Career Grants Programme", "grants", "funding"
    ]),

    # ✅ Test 3: Non-English query (French - should trigger English-only response)
    ("Quel est le programme de subventions RSTMH ?", [
        "I'm sorry", "only understand and respond in English", "ask your question in English"
    ]),

    # ✅ Test 4: Mixed English and another language (should be rejected)
    ("Tell me about grants در افغانستان", [
        "I'm sorry", "only understand and respond in English", "ask your question in English"
    ]),

    # ✅ Test 5: Fully non-English query (Arabic - should be rejected)
    ("ما هو برنامج منح RSTMH؟", [
        "I'm sorry", "only understand and respond in English", "ask your question in English"
    ]),
])
def test_llm_response(query, expected_keywords):
    print(f"\n[DEBUG] Running test for query: {query}")
    
    print(f"[DEBUG] Context Sent to LLM: {TEST_CONTEXT}")
    print(f"[DEBUG] Chat History Sent to LLM: {TEST_CHAT_HISTORY}")

    response = get_llm_response(query, TEST_CONTEXT, TEST_CHAT_HISTORY)

    print(f"[DEBUG] Expected Keywords: {expected_keywords}")
    print(f"[DEBUG] Actual LLM Response: {response}")

    assert all(keyword in response for keyword in expected_keywords), (
        f"Failed for query: {query}\nResponse: {response}"
    )