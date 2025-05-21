import hashlib
import json
import re
import unicodedata
from pathlib import Path

# ファイルパスの設定
CLIPPINGS_FILE = Path("My Clippings.txt")           # 入力: Kindle端末からコピーしたファイル
OUTPUT_DIR = Path("output_md")                     # 出力: Markdownファイルの保存先
PROCESSED_LOG = Path("processed.json")             # 処理済みハイライトの記録

# 出力先フォルダを作成
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ハッシュ関数（本タイトル + ハイライト本文）
def get_hash(book, quote):
    return hashlib.md5((book + quote).encode("utf-8")).hexdigest()

# Clippingsファイルのパース関数
def parse_clippings(file_path):
    with open(file_path, encoding="utf-8") as f:
        content = f.read().split("==========")
    highlights = []
    for entry in content:
        lines = [line.strip() for line in entry.strip().split("\n") if line.strip()]
        if len(lines) >= 3:
            book = lines[0]
            quote = lines[2]
            highlights.append((book, quote))
    return highlights

# 処理済みハッシュのロード
def load_processed():
    if PROCESSED_LOG.exists():
        with open(PROCESSED_LOG, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# 処理済みハッシュの保存
def save_processed(processed):
    with open(PROCESSED_LOG, "w", encoding="utf-8") as f:
        json.dump(list(processed), f)

# ファイル名の安全化関数
def sanitize_filename(text, max_length=40):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\\/:*?\"<>|]", "_", text)  # Windows禁則文字
    text = re.sub(r"\s+", "_", text)               # 空白→アンダースコア
    return text[:max_length]

# メイン処理関数
def main():
    highlights = parse_clippings(CLIPPINGS_FILE)
    processed = load_processed()
    book_dict = {}

    for book, quote in highlights:
        hash_id = get_hash(book, quote)
        if hash_id in processed:
            continue
        processed.add(hash_id)
        book_dict.setdefault(book, []).append(quote)

    for book, quotes in book_dict.items():
        safe_title = sanitize_filename(book)
        filename = f"{safe_title}.md"
        with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
            f.write(f"# {book}\n\n")
            f.write("#読書\n\n")
            for q in quotes:
                f.write(f"> {q}\n\n")

    save_processed(processed)
    print(f"{len(book_dict)} 冊分のMarkdownファイルを出力しました。")

if __name__ == "__main__":
    main()
