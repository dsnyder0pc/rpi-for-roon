#!/usr/bin/env python3
"""
sync_translations.py

A tool to keep translation files in sync with the master English 'Diretta.md' document.
It tracks changes (insertions, deletions, modifications) from 'git diff',
applies structural updates to the translation files, generates translation TODOs,
and applies translated entries back while verifying formatting.

Workflow:
  1. Modify 'Diretta.md' as needed.
  2. Run 'python3 scripts/sync_translations.py' (or 'sync_translations.py --ref HEAD')
     This structurally aligns the translation files and generates 'translations/todo_<lang>.json' files.
  3. Translate the entries in the 'todo_<lang>.json' files.
  4. Run 'python3 scripts/sync_translations.py --apply'
     This applies the translated strings, aligns indentation, verifies correctness, and cleans up.

Every command is safe to re-run. Before patching a translation, --sync classifies it
against both the old and the new Diretta.md: a file already aligned with the new
source is left untouched and only its TODO list is refreshed, so running --sync twice
(or running it after translations were updated by hand) cannot double-apply a hunk.
A file matching neither source is reported and skipped rather than patched blindly.

The one exception to "safe to re-run" is a line whose English was rewritten in
place. Such a line is reported until its TODO entry is cleared, because a
re-translated line and a stale one are indistinguishable without reading the
language. Repetition is the safe failure here: --apply never writes an
untranslated entry over an existing translation, so the cost is a reminder that
outstays its welcome rather than a regression that goes unnoticed.

Exit status is non-zero if any file could not be synced, applied, or verified.
"""

import os
import re
import sys
import json
import argparse
import subprocess

# Resolve repository root so the script can be run from any directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
os.chdir(REPO_ROOT)

SRC_PATH = "Diretta.md"
TRANSLATIONS_DIR = "translations"

def get_languages():
    """Auto-detect target languages based on existing Diretta-*.md files."""
    languages = []
    if not os.path.isdir(TRANSLATIONS_DIR):
        return languages
    for name in os.listdir(TRANSLATIONS_DIR):
        if name.startswith("Diretta-") and name.endswith(".md"):
            lang = name[len("Diretta-"):-3]
            if lang not in ["new", "draft", "de-new", "fr-new", "ja-new", "it-new"]:
                languages.append(lang)
    return sorted(languages)

def run_git_diff(ref):
    """Run git diff on Diretta.md against a specific revision/ref."""
    cmd = ["git", "diff", "-U0", ref, SRC_PATH]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if res.returncode != 0:
        print(f"Error running git diff: {res.stderr.strip()}")
        sys.exit(1)
    return res.stdout

def read_src_at_ref(ref):
    """Return the contents of Diretta.md as it existed at a git ref, as a list of lines."""
    cmd = ["git", "show", f"{ref}:{SRC_PATH}"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if res.returncode != 0:
        print(f"Error reading {SRC_PATH} at '{ref}': {res.stderr.strip()}")
        sys.exit(1)
    return res.stdout.splitlines()

def is_aligned_with(target_lines, src_lines):
    """True if target_lines is a structurally valid translation of src_lines.

    This is the invariant the tool maintains: same line count, same code/indent
    structure, with only translatable text allowed to differ.
    """
    return verify_translation(src_lines, target_lines, quiet=True)

def hunk_placeholders(hunks):
    """Map 1-based line numbers in the NEW source to the English text added there.

    Derived purely from the diff metadata, so it is valid regardless of whether a
    given translation has already been synced.
    """
    placeholders = {}
    for hunk in hunks:
        for offset, added_line in enumerate(hunk['added_lines']):
            placeholders[hunk['new_start'] + offset] = added_line
    return placeholders

def rewritten_lines(hunks):
    """Line numbers in the NEW source whose English was rewritten in place.

    Only hunks that replace lines one for one qualify: there the Nth added line
    is unambiguously the new text for the Nth removed line. A hunk that changes
    the line count is handled by the structural patch instead, which already
    leaves an English placeholder behind for translation.
    """
    rewritten = set()
    for hunk in hunks:
        added, removed = hunk['added_lines'], hunk['removed_lines']
        if not removed or len(added) != len(removed):
            continue
        for offset in range(len(added)):
            rewritten.add(hunk['new_start'] + offset)
    return rewritten


def build_todo(placeholders, rewritten, needs_translation, target_lines):
    """Collect lines that still need translating.

    Two kinds qualify, and only the first is visible to a content comparison.
    A line still holding English is an untranslated placeholder, whether it was
    just inserted or never got done. A line whose English was rewritten in
    place is stale even though it reads as a perfectly good translation -- it
    translates a sentence that no longer exists -- and nothing about the line
    itself reveals that, which is why the diff's removed lines are needed.

    The second kind cannot be detected as *done* either: a re-translated line
    is indistinguishable from a stale one without knowing the language. So a
    rewritten line keeps being listed until its TODO entry is removed. That is
    deliberate -- a stale translation reported twice costs a moment, and one
    reported never is a silent regression. `apply_todo_to_lines` is what makes
    the repetition safe, by refusing to write English over a real translation.
    """
    todo = {}
    for line_num, english_text in sorted(placeholders.items()):
        if not needs_translation.get(line_num, False):
            continue
        idx = line_num - 1
        if idx >= len(target_lines):
            continue
        if target_lines[idx].strip() == english_text.strip() or line_num in rewritten:
            todo[str(line_num)] = english_text
    return todo


def apply_todo_to_lines(todo, src_lines, target_lines):
    """Write translated lines into target_lines, refusing the unsafe ones.

    A TODO value identical to the English source is an entry nobody translated.
    Writing it where the target still holds the English placeholder is a no-op,
    but writing it over a real translation would replace that language's text
    with English -- so those entries are skipped and reported instead of
    applied. This is what lets a rewritten line be listed repeatedly without
    ever costing the reader their translation.

    Returns:
        list: 1-based line numbers skipped because they were still English.
    """
    skipped = []
    for line_num_str, translation in todo.items():
        idx = int(line_num_str) - 1
        src_line = src_lines[idx]
        if translation.strip() == src_line.strip() \
                and target_lines[idx].strip() != src_line.strip():
            skipped.append(int(line_num_str))
            continue
        # Align leading space exactly
        src_space = len(src_line) - len(src_line.lstrip())
        target_lines[idx] = ' ' * src_space + translation.lstrip()
    return skipped

def parse_diff(diff_output):
    """Parse unified diff hunks into structured metadata."""
    hunks = []
    current_hunk = None
    header_pattern = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')
    
    for line in diff_output.splitlines():
        if line.startswith("@@"):
            m = header_pattern.match(line)
            if m:
                if current_hunk:
                    hunks.append(current_hunk)
                
                old_start = int(m.group(1))
                old_len = int(m.group(2)) if m.group(2) is not None else 1
                new_start = int(m.group(3))
                new_len = int(m.group(4)) if m.group(4) is not None else 1
                
                current_hunk = {
                    'old_start': old_start,
                    'old_len': old_len,
                    'new_start': new_start,
                    'new_len': new_len,
                    'added_lines': [],
                    'removed_lines': []
                }
        elif current_hunk is not None:
            if line.startswith("+"):
                current_hunk['added_lines'].append(line[1:])
            elif line.startswith("-"):
                current_hunk['removed_lines'].append(line[1:])
            
    if current_hunk:
        hunks.append(current_hunk)
        
    return hunks

def analyze_lines(lines):
    """Determine which lines in the new Diretta.md need translation/review."""
    needs_translation = {}
    in_code_block = False
    
    for idx, line in enumerate(lines):
        line_num = idx + 1
        stripped = line.strip()
        
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            needs_translation[line_num] = False
            continue
        
        if in_code_block:
            is_translatable = False
            if "#" in line:
                is_translatable = True
            elif "echo " in line:
                m = re.search(r'echo\s+("[^"]+"|\'[^\']+\')', line)
                if m:
                    content = m.group(1).strip("\"'")
                    if re.search(r'[a-zA-Z]{2,}\s+[a-zA-Z]{2,}', content):
                        is_translatable = True
            elif "read " in line and (" -p" in line or " -rp" in line):
                m = re.search(r'read\s+(-\S+\s+)?("[^"]+"|\'[^\']+\')', line)
                if m:
                    content = m.group(2).strip("\"'")
                    if re.search(r'[a-zA-Z]{2,}\s+[a-zA-Z]{2,}', content):
                        is_translatable = True
            elif "PS3=" in line:
                m = re.search(r'PS3\s*=\s*("[^"]+"|\'[^\']+\')', line)
                if m:
                    content = m.group(1).strip("\"'")
                    if re.search(r'[a-zA-Z]{2,}\s+[a-zA-Z]{2,}', content):
                        is_translatable = True
            needs_translation[line_num] = is_translatable
        else:
            # Outside a code block, empty lines are skipped; others need translation
            if stripped == "":
                needs_translation[line_num] = False
            else:
                needs_translation[line_num] = True
                
    return needs_translation

def apply_hunks_to_lines(lines, hunks):
    """Apply diff hunks in reverse order (bottom-to-top) to avoid index shifting."""
    new_lines = list(lines)
    inserted_placeholders = {}
    
    sorted_hunks = sorted(hunks, key=lambda h: h['old_start'], reverse=True)
    
    for hunk in sorted_hunks:
        old_start = hunk['old_start']
        old_len = hunk['old_len']
        new_start = hunk['new_start']
        new_len = hunk['new_len']
        added_lines = hunk['added_lines']
        
        if old_len > 0:
            start_idx = old_start - 1
            end_idx = start_idx + old_len
        else:
            start_idx = old_start
            end_idx = old_start
            
        new_lines[start_idx:end_idx] = added_lines
        
        # Track 1-based line numbers in the final file structure
        for idx_offset, added_line in enumerate(added_lines):
            final_line_num = new_start + idx_offset
            inserted_placeholders[final_line_num] = added_line
            
    return new_lines, inserted_placeholders

def check_variables_match(src, dst):
    """Verify that any shell variables or subshells inside the line are preserved exactly."""
    vars_src = re.findall(r'(\$\([^)]+\)|\$\{[^}]+\}|\$[a-zA-Z_][a-zA-Z0-9_]*)', src)
    vars_dst = re.findall(r'(\$\([^)]+\)|\$\{[^}]+\}|\$[a-zA-Z_][a-zA-Z0-9_]*)', dst)
    return vars_src == vars_dst

def verify_echo_match(src, dst):
    """Check if the echo commands are structurally identical, allowing only string arguments to differ."""
    if not check_variables_match(src, dst):
        return False
    # Normalize double-quoted and single-quoted strings that do not contain nested quotes, allowing optional flags like -e or -n
    src_norm = re.sub(r'echo\s+((?:-\S+\s+)*)("[^"]*"|\'[^\']*\')', r'echo \1<STR>', src)
    dst_norm = re.sub(r'echo\s+((?:-\S+\s+)*)("[^"]*"|\'[^\']*\')', r'echo \1<STR>', dst)
    # Perform a second pass for nested contexts (e.g. inside aliases)
    src_norm = re.sub(r'echo\s+((?:-\S+\s+)*)("[^"]*"|\'[^\']*\')', r'echo \1<STR>', src_norm)
    dst_norm = re.sub(r'echo\s+((?:-\S+\s+)*)("[^"]*"|\'[^\']*\')', r'echo \1<STR>', dst_norm)
    return src_norm.strip() == dst_norm.strip()

def verify_read_match(src, dst):
    """Check if the read commands are structurally identical, allowing only the prompt string to differ."""
    if not check_variables_match(src, dst):
        return False
    src_norm = re.sub(r'read\s+(-\S+\s+)?("[^"]*"|\'[^\']*\')', r'read \1<STR>', src)
    dst_norm = re.sub(r'read\s+(-\S+\s+)?("[^"]*"|\'[^\']*\')', r'read \1<STR>', dst)
    return src_norm.strip() == dst_norm.strip()

def verify_ps3_match(src, dst):
    """Check if the PS3 prompt assignment is structurally identical, allowing only the prompt string to differ."""
    if not check_variables_match(src, dst):
        return False
    src_norm = re.sub(r'PS3\s*=\s*("[^"]*"|\'[^\']*\')', 'PS3=<STR>', src)
    dst_norm = re.sub(r'PS3\s*=\s*("[^"]*"|\'[^\']*\')', 'PS3=<STR>', dst)
    return src_norm.strip() == dst_norm.strip()

def verify_codeblock_line(src, dst):
    """Verify code block lines, allowing translated comments, echo strings, read prompts, and PS3 prompts."""
    if src.strip() == dst.strip():
        return True
        
    # Check for inline comments
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
            
    # Check for simple echo statements
    if "echo " in src and "echo " in dst:
        return verify_echo_match(src, dst)
        
    # Check for simple read prompts
    if "read " in src and "read " in dst:
        if ("-p" in src and "-p" in dst) or ("-rp" in src and "-rp" in dst):
            return verify_read_match(src, dst)
            
    # Check for simple PS3 prompts
    if "PS3=" in src and "PS3=" in dst:
        return verify_ps3_match(src, dst)
        
    return False

def verify_translation(src_lines, dst_lines, quiet=False):
    """Verify that a translation file matches the source file's format, code blocks, and indentation."""
    def report(msg):
        if not quiet:
            print(msg)

    if len(src_lines) != len(dst_lines):
        report(f"  [Error] Line count mismatch: Source={len(src_lines)}, Target={len(dst_lines)}")
        return False
        
    errors = 0
    in_code_block = False
    is_bash_block = True
    
    for i in range(len(src_lines)):
        src = src_lines[i]
        dst = dst_lines[i]
        
        if (src == '') != (dst == ''):
            report(f"  [Error] Line {i+1}: Empty line mismatch.")
            errors += 1
            if errors > 5: break
            
        if src.strip().startswith("```"):
            if not dst.strip().startswith("```") or src.strip() != dst.strip():
                report(f"  [Error] Line {i+1}: Code block tag mismatch. SRC={repr(src)}, DST={repr(dst)}")
                errors += 1
                if errors > 5: break
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
                    report(f"  [Error] Line {i+1}: Code block comment status mismatch.")
                    errors += 1
                    if errors > 5: break
                    
                if not is_src_comment:
                    if not verify_codeblock_line(src, dst):
                        report(f"  [Error] Line {i+1}: Code block command mismatch. SRC={repr(src)}, DST={repr(dst)}")
                        errors += 1
                        if errors > 5: break
                        
        src_space = len(src) - len(src.lstrip())
        dst_space = len(dst) - len(dst.lstrip())
        if src_space != dst_space:
            report(f"  [Error] Line {i+1}: Indentation mismatch. SRC={repr(src)}, DST={repr(dst)}")
            errors += 1
            if errors > 5: break
            
    return errors == 0

def cmd_sync(ref, dry_run=False):
    """Extract changes in Diretta.md and structurally sync translation files.

    Safe to re-run: each translation file is classified before it is touched, so a
    file that is already aligned with the new Diretta.md is never patched a second
    time. Re-running only refreshes the TODO lists.
    """
    if not os.path.exists(SRC_PATH):
        print(f"Source file {SRC_PATH} not found.")
        sys.exit(1)

    diff_output = run_git_diff(ref)
    if not diff_output.strip():
        print(f"No changes detected in {SRC_PATH} compared to reference '{ref}'.")
        return 0

    hunks = parse_diff(diff_output)
    print(f"Parsed {len(hunks)} diff hunks from git diff.")

    old_src_lines = read_src_at_ref(ref)
    with open(SRC_PATH, 'r', encoding='utf-8') as f:
        new_src_lines = f.read().splitlines()

    needs_translation = analyze_lines(new_src_lines)
    placeholders = hunk_placeholders(hunks)
    # Lines whose English was replaced in place. Their translations are stale
    # but structurally valid, so nothing else in this tool can spot them.
    rewritten = rewritten_lines(hunks)
    languages = get_languages()

    if not languages:
        print("No translation files found in translations/ directory.")
        return 0

    print(f"Syncing target languages: {', '.join(languages)}")
    if dry_run:
        print("(dry run: no files will be modified)")

    errors = 0

    for lang in languages:
        target_path = os.path.join(TRANSLATIONS_DIR, f"Diretta-{lang}.md")
        todo_path = os.path.join(TRANSLATIONS_DIR, f"todo_{lang}.json")

        with open(target_path, 'r', encoding='utf-8') as f:
            target_lines = f.read().splitlines()

        # Classify before touching anything. Check the new source first so that an
        # already-synced file is never patched again (the ambiguous case, where a
        # change only affects translatable text, resolves to "leave it alone").
        if is_aligned_with(target_lines, new_src_lines):
            new_target_lines = target_lines
            status = "already in sync"
        elif is_aligned_with(target_lines, old_src_lines):
            new_target_lines, _ = apply_hunks_to_lines(target_lines, hunks)
            if len(new_target_lines) != len(new_src_lines):
                print(f"  - [{lang}] [Error] Patch produced {len(new_target_lines)} lines, "
                      f"expected {len(new_src_lines)}. {target_path} left unchanged.")
                errors += 1
                continue
            status = "structurally updated"
        else:
            print(f"  - [{lang}] [Error] {target_path} matches neither the old nor the new "
                  f"{SRC_PATH}; it may have drifted. Run --verify for details. Left unchanged.")
            errors += 1
            continue

        todo = build_todo(placeholders, rewritten, needs_translation, new_target_lines)
        stale = sum(1 for line_num in todo if int(line_num) in rewritten)

        if dry_run:
            print(f"  - [{lang}] {status}; would leave {len(todo)} line(s) to translate.")
            continue

        if status == "structurally updated":
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(new_target_lines) + "\n")

        if todo:
            with open(todo_path, 'w', encoding='utf-8') as f:
                json.dump(todo, f, indent=2, ensure_ascii=False)
            detail = f"{len(todo)} items"
            if stale:
                detail += f", {stale} rewritten in English and now stale"
            print(f"  - [{lang}] {target_path} {status}. TODO file: {todo_path} ({detail}).")
        else:
            if os.path.exists(todo_path):
                os.remove(todo_path)
            print(f"  - [{lang}] {target_path} {status}. No lines require translation.")

    return 1 if errors else 0

def cmd_apply():
    """Apply translations from todo_*.json files, format indentation, verify correctness, and clean up."""
    languages = get_languages()
    
    # Read source lines for verification
    with open(SRC_PATH, 'r', encoding='utf-8') as f:
        src_lines = f.read().splitlines()
        
    applied_count = 0
    failures = 0

    for lang in languages:
        todo_path = os.path.join(TRANSLATIONS_DIR, f"todo_{lang}.json")
        target_path = os.path.join(TRANSLATIONS_DIR, f"Diretta-{lang}.md")
        
        if not os.path.exists(todo_path):
            continue
            
        print(f"Applying translations for [{lang}]...")
        with open(todo_path, 'r', encoding='utf-8') as f:
            todo = json.load(f)
            
        with open(target_path, 'r', encoding='utf-8') as f:
            target_lines = f.read().splitlines()
            
        # Check if the length is already correct
        if len(target_lines) != len(src_lines):
            print(f"  [Error] Cannot apply translations. Target file length ({len(target_lines)}) does not match source file length ({len(src_lines)}). Did you forget to run sync first?")
            failures += 1
            continue
            
        # Apply translations and enforce indentation
        skipped = apply_todo_to_lines(todo, src_lines, target_lines)

        # Verify correctness
        if verify_translation(src_lines, target_lines):
            # Save the file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(target_lines) + "\n")
            if skipped:
                # Written, but not finished: these lines still read in English
                # in the TODO, so the file keeps its existing translation and
                # the TODO stays as the reminder.
                print(f"  [Warning] {target_path} updated, but line(s) "
                      f"{', '.join(str(n) for n in skipped)} were left alone: their "
                      f"{todo_path} entries are still English and would have replaced "
                      f"a real translation. Translate them or delete the entries.")
                failures += 1
                continue
            print(f"  [Success] Verification passed for {target_path}. Cleaning up {todo_path}.")
            os.remove(todo_path)
            applied_count += 1
        else:
            print(f"  [Warning] Verification failed for {target_path}. Please check formatting errors above. {todo_path} was not deleted.")
            failures += 1

    if applied_count == 0:
        print("No translations were applied. (Are there any todo_*.json files present?)")

    return 1 if failures else 0

def cmd_verify():
    """Verify all translation files against Diretta.md."""
    with open(SRC_PATH, 'r', encoding='utf-8') as f:
        src_lines = f.read().splitlines()
        
    languages = get_languages()
    failures = 0
    for lang in languages:
        target_path = os.path.join(TRANSLATIONS_DIR, f"Diretta-{lang}.md")
        with open(target_path, 'r', encoding='utf-8') as f:
            target_lines = f.read().splitlines()

        print(f"Verifying {target_path}...")
        if verify_translation(src_lines, target_lines):
            print(f"  [OK] {target_path} is fully aligned and verified.")
        else:
            print(f"  [FAIL] {target_path} contains alignment or format mismatches.")
            failures += 1

    return 1 if failures else 0

def main():
    parser = argparse.ArgumentParser(description="Synchronize and manage translation files.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--sync", action="store_true", help="Sync translation files structurally (default action)")
    group.add_argument("--apply", action="store_true", help="Apply translations from todo_*.json files")
    group.add_argument("--verify", action="store_true", help="Verify all translation files against master")
    
    parser.add_argument("--ref", default="HEAD", help="Git revision to diff against when syncing (default: HEAD)")
    parser.add_argument("--dry-run", action="store_true", help="Report what --sync would do without modifying any files")

    args = parser.parse_args()

    if args.apply:
        rc = cmd_apply()
    elif args.verify:
        rc = cmd_verify()
    else:
        rc = cmd_sync(args.ref, dry_run=args.dry_run)

    sys.exit(rc or 0)

if __name__ == "__main__":
    main()
