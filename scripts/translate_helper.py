#!/usr/bin/env python3
import os
import sys
import re

def split_file(source_path, output_dir, lines_per_chunk=200):
    os.makedirs(output_dir, exist_ok=True)
    with open(source_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    
    total_lines = len(lines)
    chunk_idx = 1
    for start in range(0, total_lines, lines_per_chunk):
        end = min(start + lines_per_chunk, total_lines)
        chunk_lines = lines[start:end]
        
        chunk_filename = f"chunk_{chunk_idx:02d}.md"
        chunk_path = os.path.join(output_dir, chunk_filename)
        with open(chunk_path, 'w', encoding='utf-8') as cf:
            cf.write("\n".join(chunk_lines) + "\n")
        
        print(f"Created {chunk_path} (lines {start+1} to {end})")
        chunk_idx += 1
    return chunk_idx - 1

def check_variables_match(src, dst):
    vars_src = re.findall(r'(\$\([^)]+\)|\$\{[^}]+\}|\$[a-zA-Z_][a-zA-Z0-9_]*)', src)
    vars_dst = re.findall(r'(\$\([^)]+\)|\$\{[^}]+\}|\$[a-zA-Z_][a-zA-Z0-9_]*)', dst)
    return vars_src == vars_dst

def verify_echo_match(src, dst):
    if not check_variables_match(src, dst):
        return False
    src_norm = re.sub(r'echo\s+((?:-\S+\s+)*)("[^"]*"|\'[^\']*\')', r'echo \1<STR>', src)
    dst_norm = re.sub(r'echo\s+((?:-\S+\s+)*)("[^"]*"|\'[^\']*\')', r'echo \1<STR>', dst)
    src_norm = re.sub(r'echo\s+((?:-\S+\s+)*)("[^"]*"|\'[^\']*\')', r'echo \1<STR>', src_norm)
    dst_norm = re.sub(r'echo\s+((?:-\S+\s+)*)("[^"]*"|\'[^\']*\')', r'echo \1<STR>', dst_norm)
    return src_norm.strip() == dst_norm.strip()

def verify_read_match(src, dst):
    if not check_variables_match(src, dst):
        return False
    src_norm = re.sub(r'read\s+(-\S+\s+)?("[^"]*"|\'[^\']*\')', r'read \1<STR>', src)
    dst_norm = re.sub(r'read\s+(-\S+\s+)?("[^"]*"|\'[^\']*\')', r'read \1<STR>', dst)
    return src_norm.strip() == dst_norm.strip()

def verify_ps3_match(src, dst):
    if not check_variables_match(src, dst):
        return False
    src_norm = re.sub(r'PS3\s*=\s*("[^"]*"|\'[^\']*\')', 'PS3=<STR>', src)
    dst_norm = re.sub(r'PS3\s*=\s*("[^"]*"|\'[^\']*\')', 'PS3=<STR>', dst)
    return src_norm.strip() == dst_norm.strip()

def verify_codeblock_line(src, dst):
    if src.strip() == dst.strip():
        return True
        
    src_parts = src.split("#", 1)
    dst_parts = dst.split("#", 1)
    if len(src_parts) == 2 and len(dst_parts) == 2:
        cmd_src, cmd_dst = src_parts[0], dst_parts[0]
        if cmd_src.strip() == cmd_dst.strip():
            return True
        if "echo " in cmd_src and "echo " in cmd_dst:
            return verify_echo_match(cmd_src, cmd_dst)
        if "read " in cmd_src and "read " in cmd_dst:
            if ("-p" in cmd_src and "-p" in cmd_dst) or ("-rp" in cmd_src and "-rp" in cmd_dst):
                return verify_read_match(cmd_src, cmd_dst)
        if "PS3=" in cmd_src and "PS3=" in cmd_dst:
            return verify_ps3_match(cmd_src, cmd_dst)
            
    if "echo " in src and "echo " in dst:
        return verify_echo_match(src, dst)
        
    if "read " in src and "read " in dst:
        if ("-p" in src and "-p" in dst) or ("-rp" in src and "-rp" in dst):
            return verify_read_match(src, dst)
            
    if "PS3=" in src and "PS3=" in dst:
        return verify_ps3_match(src, dst)
        
    return False

def verify_chunk(src_path, dst_path):
    if not os.path.exists(dst_path):
        print(f"Error: Translated chunk file {dst_path} does not exist.")
        return False
        
    with open(src_path, 'r', encoding='utf-8') as f:
        src_lines = f.read().splitlines()
    with open(dst_path, 'r', encoding='utf-8') as f:
        dst_lines = f.read().splitlines()
        
    if len(src_lines) != len(dst_lines):
        print(f"Error: Line count mismatch. Source={len(src_lines)}, Target={len(dst_lines)}")
        return False
        
    errors = 0
    in_code_block = False
    is_bash_block = True
    dir_name = os.path.dirname(src_path)
    base_name = os.path.basename(src_path)
    match = re.match(r'chunk_(\d+)\.md', base_name)
    if match:
        chunk_num = int(match.group(1))
        for i in range(1, chunk_num):
            prev_chunk_path = os.path.join(dir_name, f"chunk_{i:02d}.md")
            if os.path.exists(prev_chunk_path):
                with open(prev_chunk_path, 'r', encoding='utf-8') as pf:
                    for line in pf:
                        sline = line.strip()
                        if sline.startswith("```"):
                            if not in_code_block:
                                in_code_block = True
                                tag = sline[3:].strip().lower()
                                is_bash_block = ("bash" in tag) or ("sh" in tag) or (tag == "")
                            else:
                                in_code_block = False
            
    for i in range(len(src_lines)):
        src = src_lines[i]
        dst = dst_lines[i]
        
        if (src == '') != (dst == ''):
            print(f"Error at line {i+1}: Empty line mismatch. SRC={repr(src)}, DST={repr(dst)}")
            errors += 1
            
        if src.strip().startswith("```"):
            if not dst.strip().startswith("```") or src.strip() != dst.strip():
                print(f"Error at line {i+1}: Code block tag mismatch. SRC={repr(src)}, DST={repr(dst)}")
                errors += 1
            if not in_code_block:
                in_code_block = True
                tag = src.strip()[3:].strip().lower()
                is_bash_block = ("bash" in tag) or ("sh" in tag) or (tag == "")
            else:
                in_code_block = False
                
        elif in_code_block:
            if is_bash_block:
                is_src_comment = src.strip().startswith("#")
                is_dst_comment = dst.strip().startswith("#")
                if is_src_comment != is_dst_comment:
                    print(f"Error at line {i+1}: Code block comment status mismatch.")
                    errors += 1
                    
                if not is_src_comment:
                    if not verify_codeblock_line(src, dst):
                        print(f"Error at line {i+1}: Code block command mismatch. SRC={repr(src)}, DST={repr(dst)}")
                        errors += 1
                    
        src_space = len(src) - len(src.lstrip())
        dst_space = len(dst) - len(dst.lstrip())
        if src_space != dst_space:
            print(f"Error at line {i+1}: Indentation mismatch. SRC={repr(src)}, DST={repr(dst)}")
            errors += 1
            
    return errors == 0

def merge_chunks(output_dir, num_chunks, target_path):
    all_lines = []
    for i in range(1, num_chunks + 1):
        chunk_filename = f"translated_{i:02d}.md"
        chunk_path = os.path.join(output_dir, chunk_filename)
        if not os.path.exists(chunk_path):
            print(f"Error: Missing {chunk_path}")
            return False
        with open(chunk_path, 'r', encoding='utf-8') as f:
            all_lines.extend(f.read().splitlines())
            
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(all_lines) + "\n")
    print(f"Successfully merged all chunks into {target_path}")
    return True

def fix_toc_links_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find headings and build map
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    headings = heading_pattern.findall(content)
    
    def slugify(text):
        cleaned = text.strip()
        cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)
        slug = cleaned.lower()
        slug = slug.replace(" ", "-")
        # GFM slugification strips common punctuation but keeps alphanumeric, hyphens, underscores.
        # But wait! A colon inside spaces in English becomes space-colon-space. Let's make sure it handles double hyphens correctly.
        # E.g. "Annexe 7 : Optimisations" -> "annexe-7---optimisations" (if space-colon-space is converted: "annexe-7-:-optimisations" then : stripped -> "annexe-7--optimisations" or "annexe-7---optimisations")
        # Let's clean the string. If there are double hyphens, GFM preserves them. E.g. "annexe-7--optimisations"
        # We replace colons first:
        slug = slug.replace(":", "")
        # Remove other punctuation:
        slug = re.sub(r'[^\w\-]', '', slug)
        return slug

    slugs = []
    for level, heading_text in headings:
        slugs.append((heading_text, slugify(heading_text)))

    print("Found headings and their GFM slugs:")
    slug_map = {}
    for h_text, slug in slugs:
        clean_h = re.sub(r'\*\*([^*]+)\*\*', r'\1', h_text)
        clean_h = re.sub(r'\*([^*]+)\*', r'\1', clean_h)
        clean_h = clean_h.strip()
        slug_map[clean_h.lower()] = slug
        print(f"  '{h_text}' -> '#{slug}'")

    def link_replacer(match):
        link_text = match.group(1)
        old_anchor = match.group(2)
        
        clean_txt = re.sub(r'\*\*([^*]+)\*\*', r'\1', link_text)
        clean_txt = re.sub(r'\*([^*]+)\*', r'\1', clean_txt)
        clean_txt = clean_txt.strip().lower()
        
        if clean_txt in slug_map:
            new_anchor = slug_map[clean_txt]
            return f"[{link_text}](#{new_anchor})"
        
        for h_clean, slug in slug_map.items():
            if clean_txt in h_clean or h_clean in clean_txt:
                return f"[{link_text}](#{slug})"
                
        return match.group(0)

    lines = content.splitlines()
    in_toc = False
    new_lines = []
    for line in lines:
        if line.strip().startswith("## ") and ("table" in line.lower() or "índice" in line.lower() or "indice" in line.lower()):
            in_toc = True
        elif line.strip().startswith("## ") and in_toc:
            in_toc = False
            
        if in_toc and line.strip() != "":
            new_line = re.sub(r'\[([^\]]+)\]\(#([^)]+)\)', link_replacer, line)
            new_lines.append(new_line)
        else:
            new_lines.append(line)
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(new_lines) + "\n")
    print(f"Automatically fixed TOC links in {file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 translate_helper.py split <source_path> <output_dir> [lines_per_chunk]")
        print("  python3 translate_helper.py verify <src_chunk_path> <dst_chunk_path>")
        print("  python3 translate_helper.py merge <output_dir> <num_chunks> <target_path>")
        print("  python3 translate_helper.py fixtoc <target_path>")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "split":
        lines_per = int(sys.argv[4]) if len(sys.argv) > 4 else 200
        split_file(sys.argv[2], sys.argv[3], lines_per)
    elif cmd == "verify":
        success = verify_chunk(sys.argv[2], sys.argv[3])
        sys.exit(0 if success else 1)
    elif cmd == "merge":
        success = merge_chunks(sys.argv[2], int(sys.argv[3]), sys.argv[4])
        sys.exit(0 if success else 1)
    elif cmd == "fixtoc":
        fix_toc_links_in_file(sys.argv[2])
