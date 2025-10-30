# CryptnetUrlCache Parser

**CryptnetUrlCache Parser** is a tool for parsing Windows Cryptnet URL cache metadata files. It extracts URLs, timestamps, file sizes, ETags, and optionally MD5 hashes of cached files. Useful for forensic investigations and malware analysis.

**Update:** I am Masum — I have updated this tool.

---

## Features

- Extracts URL, last download time, last modification time, file size, ETag, and MD5 hash (optional)
- Supports output in CSV, JSON, or JSONL
- CLI-friendly, works with Python, Linux ELF, or Windows EXE

---

## Required Libraries

Install the following Python libraries to run the script:

- altgraph
- pefile
- pyinstaller-hooks-contrib
- pywin32-ctypes
- setuptools
- packaging

---

## Usage Examples

python CryptonetURlCacheParser.py -d <cache_dir> -o output.csv --outputFormat csv --useContent

./CryptonetURlCacheParser -d /path/to/cache/Metadata -o output.csv --outputFormat csv --useContent

CryptonetURlCacheParser.exe -d "C:\Users\<User>\AppData\LocalLow\Microsoft\CryptnetUrlCache\MetaData" -o output.csv --outputFormat csv --useContent
