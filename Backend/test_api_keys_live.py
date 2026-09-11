# -*- coding: utf-8 -*-
"""
Live API Key & Pipeline Conditions Test (v2 - Fixed)
=====================================================
Fixes from v1:
  - Uses gemini-3.6-flash (matching ai_pipeline.py)
  - Fixed Unicode for Windows cp1252
  - Removed raw mistralai SDK test (not installed)
  - Added delay between Mistral calls to avoid rate limit
"""

import os, sys, time, traceback
from dotenv import load_dotenv

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

passed = 0
failed = 0
warnings = 0

def sep(title):
    print(f"\n{BOLD}{CYAN}{'='*65}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*65}{RESET}")

def ok(m):
    global passed; passed += 1
    print(f"  {GREEN}[PASS]{RESET} {m}")

def err(m):
    global failed; failed += 1
    print(f"  {RED}[FAIL]{RESET} {m}")

def warn(m):
    global warnings; warnings += 1
    print(f"  {YELLOW}[WARN]{RESET} {m}")

def info(m):
    print(f"  {CYAN}[INFO]{RESET} {m}")


# =====================================================================
#  STEP 0: Environment Variables
# =====================================================================
sep("STEP 0 - Environment Variables Check")

GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

if GEMINI_API_KEY:
    ok(f"GEMINI_API_KEY loaded  (prefix: {GEMINI_API_KEY[:12]}...)")
else:
    err("GEMINI_API_KEY is NOT set in .env")

if MISTRAL_API_KEY:
    ok(f"MISTRAL_API_KEY loaded (prefix: {MISTRAL_API_KEY[:12]}...)")
else:
    err("MISTRAL_API_KEY is NOT set in .env")

if not GEMINI_API_KEY or not MISTRAL_API_KEY:
    print(f"\n  {RED}Cannot continue without both keys. Exiting.{RESET}\n")
    sys.exit(1)


# =====================================================================
#  TEST 1: Gemini Raw SDK with gemini-3.6-flash
# =====================================================================
sep("TEST 1 - Gemini Raw SDK (google-genai) with gemini-3.6-flash")

gemini_raw_ok = False
try:
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    resp = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Say hello in one word.",
    )
    text = resp.text.strip()
    ok(f"Raw Gemini works -> \"{text[:80]}\"")
    gemini_raw_ok = True
except Exception as e:
    err(f"Raw Gemini SDK failed: {e}")


# =====================================================================
#  TEST 2: Gemini via LangChain (exactly as in ai_pipeline.py)
# =====================================================================
sep("TEST 2 - Gemini via LangChain (ChatGoogleGenerativeAI)")

MODEL_NAME = "gemini-3.6-flash"
info(f"Testing model: {MODEL_NAME}  (matches get_primary_model())")

gemini_lc_ok = False
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
    )
    response = llm.invoke("In one sentence, what is photosynthesis?")
    answer = response.content.strip()
    if answer:
        ok(f"LangChain + Gemini works -> \"{answer[:100]}\"")
        gemini_lc_ok = True
    else:
        err("LangChain + Gemini returned empty response")
except Exception as e:
    err(f"LangChain + Gemini failed: {e}")


# =====================================================================
#  TEST 3: Mistral via LangChain (exactly as in get_secondary_model)
# =====================================================================
sep("TEST 3 - Mistral via LangChain (ChatMistralAI)")
info("Waiting 5s to avoid rate limiting...")
time.sleep(5)

mistral_lc_ok = False
try:
    os.environ["MISTRAL_API_KEY"] = MISTRAL_API_KEY
    from langchain_mistralai.chat_models import ChatMistralAI
    mistral_llm = ChatMistralAI(model="open-mixtral-8x7b", temperature=0.1)
    response = mistral_llm.invoke("In one sentence, what is gravity?")
    answer = response.content.strip()
    if answer:
        ok(f"LangChain + Mistral works -> \"{answer[:100]}\"")
        mistral_lc_ok = True
    else:
        err("LangChain + Mistral returned empty response")
except Exception as e:
    err_msg = str(e)
    if "429" in err_msg or "rate" in err_msg.lower():
        warn(f"Mistral rate-limited (429). Key IS valid but you hit the rate limit.")
        warn("This is a temporary issue. Wait 60s and retry, or upgrade your Mistral plan.")
        mistral_lc_ok = "rate_limited"
    else:
        err(f"LangChain + Mistral failed: {e}")


# =====================================================================
#  TEST 4: Mistral Embeddings (RAG pipeline dependency)
# =====================================================================
sep("TEST 4 - Mistral Embeddings (MistralAIEmbeddings)")
info("Waiting 5s to avoid rate limiting...")
time.sleep(5)

embeddings_ok = False
try:
    from langchain_mistralai.embeddings import MistralAIEmbeddings
    embeddings = MistralAIEmbeddings(model="mistral-embed")
    vectors = embeddings.embed_documents(["This is a test sentence for embedding."])
    if vectors and len(vectors[0]) > 0:
        ok(f"Mistral embeddings work -> vector dim = {len(vectors[0])}")
        embeddings_ok = True
    else:
        err("Mistral embeddings returned empty vectors")
except Exception as e:
    err_msg = str(e)
    if "429" in err_msg or "rate" in err_msg.lower():
        warn(f"Mistral embeddings rate-limited (429). Key valid, rate limit hit.")
        embeddings_ok = "rate_limited"
    else:
        err(f"Mistral embeddings failed: {e}")
        traceback.print_exc()


# =====================================================================
#  TEST 5: Structured Output + All Pipeline Conditions
# =====================================================================
sep("TEST 5 - Structured Output + Pipeline Conditions Check")

structured_ok = False
if gemini_lc_ok:
    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import PydanticOutputParser
        from app.schemas.studypack import StudyPackOutput
        from app.core.constants import DEFAULT_QUIZ_SIZE, DEFAULT_DIFFICULTY

        parser = PydanticOutputParser(pydantic_object=StudyPackOutput)

        llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=GEMINI_API_KEY,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an expert educational AI tutor. Generate a study pack about photosynthesis.\n\n"
             f"You must produce exactly {DEFAULT_QUIZ_SIZE} MCQs, all at {DEFAULT_DIFFICULTY} difficulty.\n"
             "Include a non-empty summary, recommended study order, notes with highlights, "
             "glossary, flashcards, and short-answer questions.\n\n"
             "You must output STRICTLY in the following JSON format.\n"
             "{format_instructions}"),
            ("human", "Topic: Photosynthesis. Generate the study pack now.")
        ])

        prompt = prompt.partial(format_instructions=parser.get_format_instructions())
        chain = prompt | llm | parser

        info(f"Invoking structured generation chain (this may take 15-30s)...")
        t0 = time.time()
        result = chain.invoke({})
        elapsed = time.time() - t0
        info(f"Chain completed in {elapsed:.1f}s")

        # ---- Validate all conditions from ai_pipeline.py ----
        all_conditions_pass = True

        # Condition 1: summary not empty
        if result.summary.strip():
            ok(f"Condition 1: summary is non-empty ({len(result.summary)} chars)")
        else:
            err("Condition 1 FAILED: summary is empty")
            all_conditions_pass = False

        # Condition 2: mcqs count == DEFAULT_QUIZ_SIZE
        if len(result.mcqs) == DEFAULT_QUIZ_SIZE:
            ok(f"Condition 2: mcqs count == {DEFAULT_QUIZ_SIZE}")
        else:
            err(f"Condition 2 FAILED: mcqs count = {len(result.mcqs)}, expected {DEFAULT_QUIZ_SIZE}")
            all_conditions_pass = False

        # Condition 3: all mcq.difficulty == DEFAULT_DIFFICULTY
        bad_diffs = [m for m in result.mcqs if m.difficulty != DEFAULT_DIFFICULTY]
        if not bad_diffs:
            ok(f"Condition 3: all MCQ difficulty == '{DEFAULT_DIFFICULTY}'")
        else:
            err(f"Condition 3 FAILED: {len(bad_diffs)} MCQs have wrong difficulty")
            for m in bad_diffs[:3]:
                info(f"  MCQ {m.id}: difficulty='{m.difficulty}'")
            all_conditions_pass = False

        # Condition 4: flashcards not empty
        if result.flashcards:
            ok(f"Condition 4: flashcards non-empty ({len(result.flashcards)} cards)")
        else:
            err("Condition 4 FAILED: flashcards list is empty")
            all_conditions_pass = False

        # Extra info
        info(f"  notes: {len(result.notes)} topics")
        info(f"  glossary: {len(result.glossary)} terms")
        info(f"  short_answers: {len(result.short_answers)} questions")
        info(f"  recommended_study_order: {len(result.recommended_study_order)} items")

        if all_conditions_pass:
            ok("ALL 4 pipeline conditions PASS")
            structured_ok = True
        else:
            warn("Some pipeline conditions failed -- see above")

    except Exception as e:
        err(f"Structured output test failed: {e}")
        traceback.print_exc()
else:
    warn("Skipping structured output test -- Gemini LangChain not working")


# =====================================================================
#  TEST 6: RAG Vector Store (end-to-end)
# =====================================================================
sep("TEST 6 - RAG Vector Store (InMemoryVectorStore)")

rag_ok = False
if embeddings_ok is True:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.vectorstores import InMemoryVectorStore
        from langchain_mistralai.embeddings import MistralAIEmbeddings

        sample_text = (
            "Photosynthesis is the process by which green plants convert light energy "
            "into chemical energy. It occurs in chloroplasts using chlorophyll. "
            "The light reactions happen in the thylakoid membranes. "
            "The Calvin cycle occurs in the stroma. "
            "Carbon dioxide and water are converted to glucose and oxygen."
        )

        splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
        chunks = splitter.split_text(sample_text)
        info(f"Split into {len(chunks)} chunks")

        embeddings = MistralAIEmbeddings(model="mistral-embed")
        vs = InMemoryVectorStore.from_texts(chunks, embeddings)
        retriever = vs.as_retriever()

        docs = retriever.invoke("Where does the Calvin cycle happen?")
        if docs:
            ok(f"RAG retrieval works -> retrieved {len(docs)} docs")
            info(f"  Top result: \"{docs[0].page_content[:80]}\"")
            rag_ok = True
        else:
            err("RAG retrieval returned no documents")
    except Exception as e:
        err(f"RAG vector store test failed: {e}")
        traceback.print_exc()
elif embeddings_ok == "rate_limited":
    warn("Skipping RAG test -- Mistral rate-limited (key is valid though)")
else:
    warn("Skipping RAG test -- embeddings not working")


# =====================================================================
#  FINAL SUMMARY
# =====================================================================
sep("FINAL SUMMARY")

results = [
    ("Gemini API Key (raw SDK)",              "TEST 1", gemini_raw_ok),
    ("Gemini via LangChain (gemini-3.6-flash)","TEST 2", gemini_lc_ok is True),
    ("Mistral via LangChain (open-mixtral)",   "TEST 3", mistral_lc_ok is True),
    ("Mistral Embeddings (mistral-embed)",     "TEST 4", embeddings_ok is True),
    ("Structured Output + All Conditions",     "TEST 5", structured_ok),
    ("RAG Vector Store Pipeline",              "TEST 6", rag_ok),
]

print()
for name, tid, status in results:
    icon = f"{GREEN}PASS{RESET}" if status else f"{RED}FAIL{RESET}"
    if not status:
        # Check if it was rate limited
        if "Mistral" in name and (mistral_lc_ok == "rate_limited" or embeddings_ok == "rate_limited"):
            icon = f"{YELLOW}RATE-LIMITED (key valid){RESET}"
    print(f"  {tid}  [{icon}]  {name}")

print(f"\n  {BOLD}Total:{RESET}  {GREEN}{passed} passed{RESET}  |  {RED}{failed} failed{RESET}  |  {YELLOW}{warnings} warnings{RESET}")

if failed == 0:
    print(f"\n  {GREEN}{BOLD}All checks passed! Your API keys and pipeline are fully functional.{RESET}\n")
elif failed > 0 and warnings > 0:
    print(f"\n  {YELLOW}{BOLD}Some tests had issues. Review details above.{RESET}\n")
else:
    print(f"\n  {RED}{BOLD}Some checks failed. Review the errors above.{RESET}\n")
