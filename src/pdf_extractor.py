"""
PDF Downloader & Text/Award Extractor
Downloads award notice PDFs from PPDA / CMST and parses structured text streams.
"""
import os
import re
import zlib
import urllib.request
import urllib.parse
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def download_pdf(pdf_url, download_dir="downloads"):
    os.makedirs(download_dir, exist_ok=True)
    filename = os.path.basename(pdf_url)
    
    parsed = urllib.parse.urlparse(pdf_url)
    encoded_path = urllib.parse.quote(parsed.path)
    full_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, encoded_path, "", "", ""))
    
    local_path = os.path.join(download_dir, filename)
    req = urllib.request.Request(full_url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            content = resp.read()
            with open(local_path, "wb") as f:
                f.write(content)
            return local_path
    except Exception as e:
        print(f"[!] Failed to download {pdf_url}: {e}")
        return None

def extract_pdf_text(pdf_path):
    """
    Decompresses and extracts readable text from PDF streams using pure standard library.
    """
    if not os.path.exists(pdf_path):
        return ""
        
    with open(pdf_path, "rb") as f:
        data = f.read()

    stream_objs = re.findall(rb'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
    extracted_text = []
    
    for stream in stream_objs:
        try:
            decompressed = zlib.decompress(stream)
        except Exception:
            try:
                decompressed = zlib.decompress(stream, -zlib.MAX_WBITS)
            except Exception:
                decompressed = stream
                
        raw_str = decompressed.decode("latin1", errors="ignore")
        matches = re.findall(r'\(([^\(\)\\]*(?:\\.[^\(\)\\]*)*)\)\s*(?:Tj|\')', raw_str)
        if matches:
            extracted_text.extend(matches)
            
        tj_matches = re.findall(r'\[(.*?)\]\s*TJ', raw_str)
        for tj in tj_matches:
            inner_matches = re.findall(r'\(([^\(\)\\]*(?:\\.[^\(\)\\]*)*)\)', tj)
            if inner_matches:
                extracted_text.append("".join(inner_matches))

    clean_text = " ".join([t.replace("\\", "") for t in extracted_text])
    return clean_text

if __name__ == "__main__":
    test_dir = "downloads"
    for f in os.listdir(test_dir):
        if f.endswith(".pdf"):
            path = os.path.join(test_dir, f)
            print(f"\n--- {f} ---")
            print(extract_pdf_text(path)[:500])
