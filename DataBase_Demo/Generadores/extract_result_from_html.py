from pathlib import Path
from bs4 import BeautifulSoup

html_path = Path("miranda_binding_calc/web_runs/miranda_result.html")
out_txt = Path("miranda_binding_calc/web_runs/miranda_output_extracted.txt")

html = html_path.read_text(encoding="utf-8", errors="ignore")
soup = BeautifulSoup(html, "html.parser")

# intenta encontrar el resultado en <pre>
pre = soup.find("pre")
if pre and pre.get_text(strip=True):
    out_txt.write_text(pre.get_text("\n", strip=True), encoding="utf-8")
    print("✅ Extraído desde <pre>:", out_txt)
else:
    # intenta textarea grande
    textareas = soup.find_all("textarea")
    best = None
    best_len = 0
    for t in textareas:
        content = t.get_text(strip=False) or ""
        if len(content) > best_len:
            best = content
            best_len = len(content)

    if best_len > 0:
        out_txt.write_text(best, encoding="utf-8")
        print("✅ Extraído desde <textarea> (el más largo):", out_txt)
    else:
        print("⚠️ No encontré salida en <pre> ni <textarea>. Hay que revisar el HTML.")
