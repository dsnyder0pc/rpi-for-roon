#!/usr/bin/env python3
import re
import os

LANGUAGES = ["de", "es", "fr", "it", "ja", "pt"]

def is_technical(text):
    text_clean = text.strip('#').strip()
    # Check if it has no letters
    if not any(c.isalpha() for c in text_clean):
        return True
    # Ignore lines that are config parameter writes or comments that shouldn't be translated (e.g. # === Custom ...)
    if text_clean.startswith('===') or text_clean.endswith('==='):
        return True
    # Ignore purely technical variable assignments or parameter name comments in config templates
    tech_keywords = [
        'upnpiface', 'friendlyname', 'avfriendlyname', 'device', 'auto_resample', 
        'auto_format', 'dop', 'type', 'name', 'dtparam', 'dtoverlay', 
        'limit-speed', 'purist-mode', 'systemd', 'network', 'bootloader', 'pyenv'
    ]
    if any(kw in text_clean.lower() for kw in tech_keywords):
        # But wait! If it's a long sentence containing these keywords, it might still be human-facing.
        # So check word count:
        if len(text_clean.split()) <= 4:
            return True
    return False

def main():
    with open('Diretta.md', 'r', encoding='utf-8') as f:
        eng = f.read().splitlines()
        
    # Detect code blocks
    in_code_block = False
    comment_lines = [] # list of (line_idx, line_text)
    
    for idx, line in enumerate(eng):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
            
        if in_code_block:
            stripped = line.strip()
            # If line is a comment or contains a comment
            if '#' in stripped:
                # Extract the comment part
                comment_part = stripped[stripped.index('#'):]
                if not is_technical(comment_part):
                    comment_lines.append((idx, line, comment_part))
                    
    for lang in LANGUAGES:
        trans_path = f"translations/Diretta-{lang}.md"
        if not os.path.exists(trans_path):
            print(f"File not found: {trans_path}")
            continue
            
        with open(trans_path, 'r', encoding='utf-8') as f:
            trans = f.read().splitlines()
            
        print(f"\n--- Checking comments in {lang} ---")
        untranslated = 0
        for idx, eng_line, comment_part in comment_lines:
            if idx >= len(trans):
                break
            trans_line = trans[idx]
            
            # If the comment is identical to the English version
            if comment_part.strip() in trans_line:
                print(f"Line {idx+1:4d}: {repr(eng_line.strip())}")
                print(f"      -> {repr(trans_line.strip())}")
                untranslated += 1
        print(f"Total untranslated human-facing comments: {untranslated}")

if __name__ == "__main__":
    main()
