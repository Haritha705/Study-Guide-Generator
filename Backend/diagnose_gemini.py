"""
Deep Gemini API Diagnostics
- Tests AQ. key with raw google-genai SDK
- Lists all available models for this key/account
- Tests langchain-google-genai with correct model
"""

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def sep(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

def ok(m):   print(f"  {GREEN}[OK]   {m}{RESET}")
def err(m):  print(f"  {RED}[FAIL] {m}{RESET}")
def info(m): print(f"  {CYAN}[INFO] {m}{RESET}")
def warn(m): print(f"  {YELLOW}[WARN] {m}{RESET}")

PROMPT = "In one sentence, what is photosynthesis?"

# ── Step 1: Raw SDK — list models ──────────────────────────────────────────────
sep("STEP 1 · Raw google-genai SDK — List Available Models")
info(f"google-genai version: 2.22.0")
info(f"langchain-google-genai version: 4.4.0")
info(f"Key prefix: {GEMINI_API_KEY[:24] if GEMINI_API_KEY else 'NOT SET'}...")

available_models = []
try:
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    models = client.models.list()
    for m in models:
        name = getattr(m, 'name', str(m))
        supported = getattr(m, 'supported_actions', [])
        available_models.append(name)
        print(f"    {name}  |  actions: {supported}")
    ok(f"Listed {len(available_models)} model(s) for this key")
except Exception as e:
    err(f"Model listing failed: {e}")


# ── Step 2: Raw SDK — generate content ────────────────────────────────────────
sep("STEP 2 · Raw google-genai SDK — Direct generate_content call")

CANDIDATE_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "models/gemini-2.0-flash",
    "models/gemini-1.5-flash",
]

# Prefer models that were actually listed
test_models = []
for m in available_models:
    for c in CANDIDATE_MODELS:
        if c in m or m in c:
            if m not in test_models:
                test_models.append(m)
if not test_models:
    test_models = CANDIDATE_MODELS[:3]

working_raw_model = None
try:
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    for model_name in test_models:
        info(f"Trying model: {model_name}")
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=PROMPT,
            )
            text = resp.text.strip()
            ok(f"Model '{model_name}' works!")
            print(f"\n  {BOLD}Answer:{RESET} {text}\n")
            working_raw_model = model_name
            break
        except Exception as e:
            err(f"  '{model_name}' → {e}")
except Exception as e:
    err(f"Raw SDK init failed: {e}")


# ── Step 3: LangChain wrapper ──────────────────────────────────────────────────
sep("STEP 3 · langchain-google-genai wrapper")

lc_model_to_try = working_raw_model or "gemini-2.0-flash"
# Strip "models/" prefix if present — LangChain adds it internally
if lc_model_to_try.startswith("models/"):
    lc_model_to_try = lc_model_to_try[len("models/"):]

info(f"Testing with model: {lc_model_to_try}")

lc_ok = False
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model=lc_model_to_try,
        temperature=0.2,
        google_api_key=GEMINI_API_KEY,
    )
    response = llm.invoke(PROMPT)
    answer = response.content.strip()
    ok(f"LangChain + Gemini works with '{lc_model_to_try}'!")
    print(f"\n  {BOLD}Answer:{RESET} {answer}\n")
    lc_ok = True
except Exception as e:
    err(f"LangChain wrapper failed: {e}")

    # Try alternative auth via environment variable
    info("Trying GOOGLE_API_KEY env var approach...")
    try:
        import os
        os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model=lc_model_to_try, temperature=0.2)
        response = llm.invoke(PROMPT)
        ok(f"Works via GOOGLE_API_KEY env var!")
        print(f"\n  {BOLD}Answer:{RESET} {response.content.strip()}\n")
        lc_ok = True
    except Exception as e2:
        err(f"Env var approach also failed: {e2}")


# ── Final Recommendation ───────────────────────────────────────────────────────
sep("DIAGNOSIS & RECOMMENDATION")

if lc_ok:
    ok(f"Gemini is WORKING via LangChain")
    ok(f"Use model name: '{lc_model_to_try}' in ai_pipeline.py")
    print(f"\n  {BOLD}Action:{RESET} Update get_primary_model() in ai_pipeline.py to:")
    print(f"    return ChatGoogleGenerativeAI(model=\"{lc_model_to_try}\", temperature=0.2)")
elif working_raw_model:
    warn("Raw SDK works but LangChain wrapper fails")
    warn("Check langchain-google-genai version compatibility")
else:
    err("Key does not work with any tested model")
    err("Exact errors shown above — no assumption about key format")
    print(f"\n  {BOLD}Next steps:{RESET}")
    print("  1. Check if this key needs a specific API endpoint")
    print("  2. Verify the key has 'Generative Language API' permission enabled")
    print("  3. Check: console.cloud.google.com → APIs → Generative Language API")
print()
