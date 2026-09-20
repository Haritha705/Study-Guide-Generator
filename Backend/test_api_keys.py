"""
Live API Key Tester — Gemini Edition
Tests Gemini (primary) → Mistral fallback, Embeddings, Tavily, LangSmith, MongoDB.
"""

import os
from dotenv import load_dotenv

# Load .env from project root (one level up from Backend/)
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY")
MISTRAL_API_KEY   = os.getenv("MISTRAL_API_KEY")
TAVILY_API_KEY    = os.getenv("TAVILY_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
MONGODB_URL       = os.getenv("MONGODB_URL")

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

EXAMPLE_PROMPT = "In one sentence, what is photosynthesis?"
ACTIVE_LLM = None

def print_header(title):
    print(f"\n{BOLD}{CYAN}{'='*55}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*55}{RESET}")

def ok(msg):   print(f"  {GREEN}[PASS] {msg}{RESET}")
def fail(msg): print(f"  {RED}[FAIL] {msg}{RESET}")
def warn(msg): print(f"  {YELLOW}[WARN] {msg}{RESET}")
def info(msg): print(f"  {CYAN}[INFO] {msg}{RESET}")


# ── 1. Gemini ──────────────────────────────────────────
def test_gemini():
    global ACTIVE_LLM
    print_header("1 · Gemini (gemini-3.6-flash) — PRIMARY LLM")

    if not GEMINI_API_KEY:
        fail("GEMINI_API_KEY not found in .env")
        return False

    info(f"Key prefix : {GEMINI_API_KEY[:20]}...")
    info(f"Sending    : \"{EXAMPLE_PROMPT}\"")

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=GEMINI_API_KEY,
        )
        response = llm.invoke(EXAMPLE_PROMPT)
        # gemini-3.6-flash returns content as list of parts or string
        content = response.content
        if isinstance(content, list):
            answer = " ".join(
                p.get("text", "") if isinstance(p, dict) else str(p)
                for p in content
            ).strip()
        else:
            answer = str(content).strip()
        ok("Gemini responded successfully!")
        print(f"\n  {BOLD}Answer:{RESET} {answer}\n")
        ACTIVE_LLM = "Gemini 1.5 Flash"
        return True

    except Exception as e:
        fail(f"Gemini FAILED: {e}")
        return False


# ── 2. Mistral fallback ────────────────────────────────
def test_mistral():
    global ACTIVE_LLM
    print_header("2 · Mistral (open-mixtral-8x7b) — SECONDARY LLM")

    if not MISTRAL_API_KEY:
        fail("MISTRAL_API_KEY not found in .env")
        return False

    info(f"Key prefix : {MISTRAL_API_KEY[:12]}...")
    info(f"Sending    : \"{EXAMPLE_PROMPT}\"")

    try:
        from langchain_mistralai.chat_models import ChatMistralAI
        llm = ChatMistralAI(
            model="open-mixtral-8x7b",
            temperature=0.1,
            api_key=MISTRAL_API_KEY,
        )
        response = llm.invoke(EXAMPLE_PROMPT)
        answer = response.content.strip()
        ok("Mistral responded successfully!")
        print(f"\n  {BOLD}Answer:{RESET} {answer}\n")
        if not ACTIVE_LLM:
            ACTIVE_LLM = "Mistral (open-mixtral-8x7b)"
        return True

    except Exception as e:
        fail(f"Mistral FAILED: {e}")
        return False


# ── 3. Mistral Embeddings ──────────────────────────────
def test_mistral_embeddings():
    print_header("3 · Mistral Embeddings (mistral-embed)")

    if not MISTRAL_API_KEY:
        fail("MISTRAL_API_KEY not found in .env")
        return False

    try:
        from langchain_mistralai.embeddings import MistralAIEmbeddings
        emb = MistralAIEmbeddings(model="mistral-embed", api_key=MISTRAL_API_KEY)
        vector = emb.embed_query("photosynthesis")
        ok(f"Embedding returned vector of dim {len(vector)}")
        return True
    except Exception as e:
        fail(f"Embeddings FAILED: {e}")
        return False


# ── 4. Tavily ──────────────────────────────────────────
def test_tavily():
    print_header("4 · Tavily Web Search")

    if not TAVILY_API_KEY:
        fail("TAVILY_API_KEY not found in .env")
        return False

    info(f"Key prefix : {TAVILY_API_KEY[:14]}...")

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        result = client.search("What is photosynthesis?", max_results=1)
        ok(f"Tavily responded — got {len(result.get('results', []))} result(s)")
        return True
    except ImportError:
        warn("tavily-python not installed — skipping  (pip install tavily-python)")
        return None
    except Exception as e:
        fail(f"Tavily FAILED: {e}")
        return False


# ── 5. LangSmith ──────────────────────────────────────
def test_langsmith():
    print_header("5 · LangSmith Tracing")

    if not LANGSMITH_API_KEY:
        fail("LANGSMITH_API_KEY not found in .env")
        return False

    info(f"Key prefix : {LANGSMITH_API_KEY[:20]}...")

    try:
        from langsmith import Client
        client = Client(api_key=LANGSMITH_API_KEY)
        projects = list(client.list_projects())
        ok(f"LangSmith connected — {len(projects)} project(s) found")
        return True
    except Exception as e:
        fail(f"LangSmith FAILED: {e}")
        return False


# ── 6. MongoDB ────────────────────────────────────────
def test_mongodb():
    print_header("6 · MongoDB Atlas Connection")

    if not MONGODB_URL:
        fail("MONGODB_URL not found in .env")
        return False

    info(f"URL prefix : {MONGODB_URL[:35]}...")

    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import asyncio

        async def ping():
            client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
            await client.admin.command("ping")
            client.close()

        asyncio.run(ping())
        ok("MongoDB Atlas ping successful")
        return True
    except Exception as e:
        fail(f"MongoDB FAILED: {e}")
        return False


# ── MAIN ──────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{BOLD}{'='*55}")
    print("   Study-APP - Live API Key & Service Tester")
    print(f"   Provider: Gemini + Mistral + MongoDB + LangSmith")
    print(f"{'='*55}{RESET}")

    gemini_ok  = test_gemini()

    if not gemini_ok:
        warn("Gemini failed — testing Mistral as fallback...")

    mistral_ok  = test_mistral()
    emb_ok      = test_mistral_embeddings()
    tavily_ok   = test_tavily()
    ls_ok       = test_langsmith()
    mongo_ok    = test_mongodb()

    print_header("SUMMARY")

    results = [
        ("Gemini LLM (primary)",    gemini_ok),
        ("Mistral LLM (fallback)",  mistral_ok),
        ("Mistral Embeddings",      emb_ok),
        ("Tavily Search",           tavily_ok),
        ("LangSmith",               ls_ok),
        ("MongoDB Atlas",           mongo_ok),
    ]

    for name, status in results:
        if status is True:
            ok(f"{name:30s} PASSED")
        elif status is False:
            fail(f"{name:30s} FAILED")
        else:
            warn(f"{name:30s} SKIPPED")

    print()
    if ACTIVE_LLM:
        print(f"  {BOLD}Active LLM for your app  ->  {GREEN}{ACTIVE_LLM}{RESET}")
    else:
        print(f"  {RED}{BOLD}WARNING: NO LLM AVAILABLE — check your API keys!{RESET}")
    print()
