from serper_tool import search_serper
from gemini_tool import gemini_summarize

print("🤖 AI Research Sidekick\n")
query = input("🧠 Enter your research topic: ")

print("\n🔍 Searching...")
search_results = search_serper(query)

print("\n🧠 Summarizing with Gemini...")
summary = gemini_summarize(search_results)

print("\n📄 Final Summary:\n")
print(summary)
