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
