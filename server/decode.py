import sys
with open('debug_out.txt', 'rb') as f:
    text = f.read().decode('utf-16le')
with open('debug_utf8.txt', 'w', encoding='utf-8') as f:
    f.write(text)
