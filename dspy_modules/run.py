import dspy, os
from dotenv import load_dotenv

def test_dspy() -> dspy.Prediction:
    load_dotenv()

    dspy_config_env = True  # just a marker for context, not used
    # Pull configuration from environment variables (set in .env)
    MODEL_NAME   = os.getenv("MODEL_NAME",   "openai/qwen2.5:7b-instruct-q4_K_M")
    TEMPERATURE  = float(os.getenv("TEMPERATURE", 0.2))
    MAX_TOKENS   = int(os.getenv("MAX_TOKENS", 2048*16))
    CACHE_FLAG   = os.getenv("CACHE", "true").lower() not in ("0", "false", "no")

    lm = dspy.LM(
        MODEL_NAME,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        cache=CACHE_FLAG,
        base_url="http://localhost:11434/v1",

    )

    dspy.configure(lm=lm)

    # 2️⃣ Now build / call your DSPy modules
    from dspy_modules.note_gen import NoteGenerator

    generator = NoteGenerator()
    pred: dspy.Prediction = generator(
        context="Why is SQLite great for note-sized data?",
        note_list=["Databases.md", "SQL Basics.md"]
    )
    return pred

def generate_note_from_topic(topic: str, note_list: list) -> dspy.Prediction:
    """
    Generate a note on a user-specified topic using DSPy
    
    Args:
        topic: The topic to generate a note about
        note_list: List of related note filenames to reference
        
    Returns:
        A DSPy prediction containing the generated note
    """
    load_dotenv()

    # Pull configuration from environment variables (set in .env)
    MODEL_NAME   = os.getenv("MODEL_NAME",   "openai/qwen2.5:7b-instruct-q4_K_M")
    TEMPERATURE  = float(os.getenv("TEMPERATURE", 0.2))
    MAX_TOKENS   = int(os.getenv("MAX_TOKENS", 2048))
    CACHE_FLAG   = os.getenv("CACHE", "true").lower() not in ("0", "false", "no")

    lm = dspy.LM(
        MODEL_NAME,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        cache=CACHE_FLAG,
        base_url="http://localhost:11434/v1",
    )

    dspy.configure(lm=lm)

    # Create and use the NoteGenerator module
    from dspy_modules.note_gen import NoteGenerator

    generator = NoteGenerator()
    pred: dspy.Prediction = generator(
        context=topic,
        note_list=note_list
    )
    return pred