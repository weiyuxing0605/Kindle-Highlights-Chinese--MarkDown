import os
import re
import sys


def sanitize_filename(filename):
    return re.sub(r'[\\/*:"<>|]', "_", filename)


def process_clippings(file_path):
    books = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        clippings = content.split('==========')

        for clipping in clippings:
            lines = [line.strip() for line in clipping.split('\n') if line.strip()]
            if len(lines) < 3:
                continue

            book_title = lines[0]
            metadata_line = lines[1]

            # 提取页码和位置信息
            page_match = re.search(r'第\s*(\d+)\s*页', metadata_line)
            loc_match = re.search(r'位置\s*(#\d+-\d+)', metadata_line)

            page = page_match.group(1) if page_match else None
            location = loc_match.group(1) if loc_match else "未知位置"

            # 构建位置描述
            location_desc = []
            if page:
                location_desc.append(f"页码 {page}")
            if location != "未知位置":
                location_desc.append(f"位置 {location}")

            location_str = "，".join(location_desc) if location_desc else "未知位置"
            content = lines[2] if len(lines) >= 3 else ""

            if book_title not in books:
                books[book_title] = []
            books[book_title].append((location_str, content))

    return books


def export_to_markdown(books, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for book_title, clippings in books.items():
        markdown_content = f"# {book_title}\n\n"
        for location, content in clippings:
            markdown_content += f"## {location}\n\n{content}\n\n---\n\n"

        safe_book_title = sanitize_filename(book_title)
        markdown_file_path = os.path.join(output_dir, f"{safe_book_title}.md")

        with open(markdown_file_path, 'w', encoding='utf-8') as file:
            file.write(markdown_content)


if __name__ == "__main__":
    clippings_file_path = "My Clippings.txt"
    output_dir = "kindle_notes"

    if not os.path.exists(clippings_file_path):
        print(f"错误：剪贴文件 {clippings_file_path} 不存在")
        sys.exit(1)

    books = process_clippings(clippings_file_path)
    export_to_markdown(books, output_dir)
    print(f"成功生成 {len(books)} 本书的标注到 {output_dir} 目录")
