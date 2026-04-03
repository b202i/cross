"""
Cross full-stack import test.
Run with: python3.12 /tmp/test_cross_stack.py
"""
import sys
print(f"Python: {sys.version}")

results = []

def check(label, fn):
    try:
        fn()
        results.append((label, "OK", ""))
    except Exception as e:
        results.append((label, "FAIL", str(e)))

# TTS packages
check("soundfile import + libsndfile", lambda: __import__("soundfile"))
check("soundfile libsndfile version", lambda: (
    __import__("soundfile"),
    print(f"  libsndfile: {__import__('soundfile').__libsndfile_version__}")
))
check("yakyak import", lambda: __import__("yakyak"))
check("websockets import", lambda: __import__("websockets"))

# Scientific stack
check("numpy import", lambda: __import__("numpy"))
check("numpy version check", lambda: (
    n := __import__("numpy"),
    print(f"  numpy: {n.__version__}")
))
check("scipy import", lambda: __import__("scipy"))
check("pandas import", lambda: __import__("pandas"))
check("matplotlib import", lambda: __import__("matplotlib"))
check("seaborn import", lambda: __import__("seaborn"))

# Text / utility
check("weasyprint import", lambda: __import__("weasyprint"))
check("markdown import", lambda: __import__("markdown"))
check("dotenv import", lambda: __import__("dotenv"))
check("tabulate import", lambda: __import__("tabulate"))
check("tqdm import", lambda: __import__("tqdm"))

# AI providers (just import, no API calls)
check("anthropic import", lambda: __import__("anthropic"))
check("openai import", lambda: __import__("openai"))
check("google.genai import", lambda: __import__("google.genai"))

print()
print(f"{'Package':<30} {'Status':<6}  Note")
print(f"{'─'*30} {'─'*6}  {'─'*40}")
for label, status, note in results:
    icon = "✅" if status == "OK" else "❌"
    print(f"  {icon} {label:<28} {status}  {note[:60]}")

fails = [r for r in results if r[1] == "FAIL"]
print()
if fails:
    print(f"FAILURES: {len(fails)}")
else:
    print("ALL PASSED ✅")

