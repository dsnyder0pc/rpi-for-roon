# Project-Scoped Rules for Translation Management

## Keeping Translations In-Sync with Diretta.md

Whenever changes are made to the master English [Diretta.md](file:///home/dsnyder/src/rpi-for-roon/Diretta.md) file, all translations under the [translations/](file:///home/dsnyder/src/rpi-for-roon/translations/) directory must be updated to maintain strict line-for-line mapping, matching formatting, code block consistency, and exact indentation.

To automate this workflow, a custom management tool has been created at [scripts/sync_translations.py](file:///home/dsnyder/src/rpi-for-roon/scripts/sync_translations.py).

### How to Sync Translations (Workflow)

When modifications to [Diretta.md](file:///home/dsnyder/src/rpi-for-roon/Diretta.md) have been made in the working tree (staged or unstaged):

1. **Step 1: Structural Synchronization & Generating TODOs**
   Run the sync script to apply insertions, deletions, and structural replacements to all target files and generate a translation TODO list for each language:
   ```bash
   python3 scripts/sync_translations.py
   ```
   *Note:* By default, this diffs the working tree against `HEAD`. To diff against a specific commit or git reference, pass the `--ref <commit-hash>` flag:
   ```bash
   python3 scripts/sync_translations.py --ref <revision>
   ```
   This will:
   - Update `translations/Diretta-*.md` with new structural lines (using the new English lines as placeholders).
   - Generate `translations/todo_<lang>.json` containing only the new or changed lines that require translation.

2. **Step 2: Perform the Translation**
   The agent (or user) translates the English values inside each `translations/todo_<lang>.json` file to their target language.

3. **Step 3: Apply the Translations & Verify**
   Run the sync script with the `--apply` flag to replace the placeholders in the translation files, align formatting and indentation perfectly, run full verification, and clean up the JSON files:
   ```bash
   python3 scripts/sync_translations.py --apply
   ```

4. **Manual Verification (Optional)**
   To run verification at any time without applying new changes:
   ```bash
   python3 scripts/sync_translations.py --verify
   ```

### Critical Rules for Translating Code Blocks and Links

1. **Table of Contents (TOC) & Section Anchors**
   - **TOC anchors must match the translated headings**: If a heading in the text is translated (e.g. `## 1. Prerequisites` -> `## 1. Vorbereitungen`), its corresponding link target in the TOC must point to the slug of the translated heading (e.g. `#1-vorbereitungen`).
   - **GitHub GFM Slugification rules**: 
     - Lowercase the heading.
     - Replace whitespace with hyphens (`-`).
     - Remove punctuation (periods, colons, parentheses, etc.).
     - **Double Hyphens**: If a colon is surrounded by spaces (e.g., `Annexe 7 : Optimisations`), GFM replaces spaces with hyphens first and then strips the colon, leaving a double hyphen (`--`). Ensure these double hyphens are preserved (e.g., `#16-annexe-7--optimisations...`).
     - A utility script `scratch/fix_toc_links.py` is available in scratch files to automate this replacement.

2. **Echo, Read, & Logging Statements**
   - **Translate human-facing messages**: Logging and print statements that write messages to standard output or standard error (e.g., `echo "Welcome to the interactive timezone setup."` or `echo "Error: License cache not found" >&2`) must be translated to the target language.
   - **Translate read prompts**: Prompt strings inside `read -p` or `read -rp` (e.g., `"Enter the address of your RPi and hit [enter]: "`) should be translated, while keeping the command structure, options, and target variable name (e.g. `RPi_IP_Address`) exactly in English.
   - **Protect shell variables & subshells**: Do not translate variables (e.g., `$timezone`, `${TOTAL_MEM}`) or subshell executions (e.g., `$(cat /etc/machine-id)`) inside quotes.
   - **Do NOT translate config writes**: Statements that write technical code or config parameters to files (e.g. `echo "net.ipv4.ip_forward=1" | sudo tee ...` or heredocs `cat <<'EOT'`) must remain 100% identical in English.


