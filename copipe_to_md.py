import re
import unicodedata
from pathlib import Path

INPUT_FILE = Path("notebook_dump.txt")  # コピペしたテキストファイル
OUTPUT_DIR = Path("output_md_notebook")
OUTPUT_DIR.mkdir(exist_ok=True)

# ファイル名を安全にする
def sanitize_filename(text, max_length=40):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\\/:*?\"<>|]", "_", text)
    text = re.sub(r"\s+", "_", text)
    return text[:max_length]

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

book_data = []
current_book = None
current_position = ""
current_highlight_type = ""

for line in lines:
    line = line.strip()
    if line.startswith("メモ付きのKindle本:"):
        if current_book:
            book_data.append(current_book)
        current_book = {"title": None, "author": None, "highlights": []}
    elif current_book and not current_book["title"] and line:
        current_book["title"] = line
    elif current_book and not current_book["author"] and line:
        current_book["author"] = line
    elif current_book and re.search(r"のハイライト", line):
        current_highlight_type = line
        current_position = ""
    elif current_book and line.startswith("位置:"):
        current_position = line
    elif current_book and line == "":
        current_position = ""
    elif current_book:
        entry = f"{current_highlight_type} | {current_position}\n\n{line.strip()}" if current_position else f"{current_highlight_type}\n\n{line.strip()}"
        current_book["highlights"].append(entry)
        current_position = ""

if current_book:
    book_data.append(current_book)

for book in book_data:
    title = book.get("title") or "Untitled"
    author = book.get("author") or "Unknown"
    highlights = book.get("highlights", [])

    safe_filename = sanitize_filename(title)
    filename = f"{safe_filename}.md"
    with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
        f.write(f"# {title}（{author}）\n\n")
        f.write("#読書 #Kindle\n\n")
        for h in highlights:
            f.write(f"> {h}\n\n\n")

print(f"{len(book_data)} 冊分のMarkdownファイルを生成しました → {OUTPUT_DIR}")
