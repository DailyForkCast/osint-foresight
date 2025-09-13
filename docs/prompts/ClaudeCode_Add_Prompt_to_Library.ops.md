# Claude Code Ops Prompt — Add Prompt to Library

Copy the block below into Claude Code and fill in PROMPT_BODY (or set SOURCE_FILE):

```
# ADD PROMPT TO LIBRARY
PROJECT: Deep Research – Intl Research Security
INTENT: Save the following prompt into our prompts folder with metadata, versioning, and index updates.

# ========= CONFIG =========
PROMPTS_ROOT: ./prompts                   # change if your repo uses a different path
COLLECTION: phase_x                       # e.g., phase_x, phase_0, phase_1 ...
TITLE: "Phase X — Universal Header & Run Controls (ChatGPT-only)"
SLUG: phase_x_universal_header_chatgpt    # lower_snake_case; unique within repo
PHASE: X
COUNTRY_SCOPE: "any"                      # or a specific country
TOOLS_TARGET: ["chatgpt"]                 # or ["claude","chatgpt"], ["claude"], etc.
TAGS: ["template","controls","languages","toggles","evidence","osint"]
VERSION: 0.1.0                            # will auto-bump if file exists
AUTHOR: "Maureen / DR-IRS"
LICENSE: "CC BY 4.0"
FORMAT: "md"                              # md or yaml or both
ADDITIONAL_EXPORTS: ["yaml","json"]       # machine-readable mirrors

# Optional: if the prompt already lives in a file you’ve saved:
# SOURCE_FILE: ./staging/phase_x_chatgpt.md
# If you keep it inline instead, leave SOURCE_FILE unset and paste in PROMPT_BODY.

# ========= PROMPT BODY (PASTE YOUR PROMPT BELOW) =========
PROMPT_BODY: |
  <<PASTE THE PROMPT TEXT YOU WANT STORED HERE>>
  <<Do not include this instruction line in the final file>>
# =========================================================

# =============== TASKS ===============
DO:
  - Ensure directory exists: ${PROMPTS_ROOT}/${COLLECTION}
  - If ${SOURCE_FILE} is set:
      - Read prompt text from ${SOURCE_FILE}
    Else:
      - Use PROMPT_BODY as the source string
  - Normalize line endings to LF and trim trailing whitespace
  - Build YAML front matter:
      ---
      title: "${TITLE}"
      slug: "${SLUG}"
      phase: "${PHASE}"
      country_scope: ${COUNTRY_SCOPE}
      tools_target: ${TOOLS_TARGET}
      tags: ${TAGS}
      version: "${VERSION}"
      author: "${AUTHOR}"
      license: "${LICENSE}"
      created_utc: "{{now_utc_iso}}"
      updated_utc: "{{now_utc_iso}}"
      sha256: "{{computed_after_write}}"
      format: "${FORMAT}"
      collection: "${COLLECTION}"
      ---
  - Write primary artifact:
      PATH_PRIMARY: ${PROMPTS_ROOT}/${COLLECTION}/${SLUG}.md
      CONTENT: [front matter] + newline + [prompt text]
      - If PATH_PRIMARY already exists:
          * Read existing version
          * If content differs: bump patch version (e.g., 0.1.0 -> 0.1.1) in front matter
          * Preserve created_utc; update updated_utc
  - Compute SHA-256 of file bytes and inject into front matter (sha256)
  - Create machine mirrors if requested in ${ADDITIONAL_EXPORTS}:
      * ${SLUG}.yaml: keys {meta: front_matter_as_object, body: prompt_text}
      * ${SLUG}.json:  same structure as YAML
  - Update prompts index at ${PROMPTS_ROOT}/index.json:
      * Ensure array of prompt records exists
      * Upsert record by slug with: title, slug, phase, collection, tools_target, tags, version, paths, updated_utc, sha256
      * Sort by collection then title
      * Pretty-print with 2-space indent
  - Write/append checksum line to ${PROMPTS_ROOT}/checksums.txt:
      * Format: "<sha256>  ${COLLECTION}/${SLUG}.md"
  - Validate:
      * Non-empty body (≥ 300 chars)
      * Required fields present
      * tools_target ∈ {chatgpt, claude, both}
      * PHASE matches /^X|0|[1-9]\d?$/
  - If git repo present:
      * git add ${PROMPTS_ROOT}
      * git commit -m "Add/Update prompt: ${SLUG} v${VERSION} [${COLLECTION}]"
  - Output summary:
      * File tree for ${PROMPTS_ROOT}/${COLLECTION}
      * Record from index.json for ${SLUG}
      * SHA-256 value
      * Next steps: how to reference SLUG from run blocks

ACCEPTANCE_CRITERIA:
  - The file ${PROMPTS_ROOT}/${COLLECTION}/${SLUG}.md exists with YAML front matter
  - ${PROMPTS_ROOT}/index.json contains an up-to-date entry for ${SLUG}
  - SHA-256 recorded in front matter and checksums.txt matches the file
  - Mirrors (.yaml/.json) exist if requested and contain identical meta/body
  - If pre-existing file differed, version was bumped and timestamps updated

ERROR_HANDLING:
  - On missing body/source: FAIL with message "No prompt text provided"
  - On invalid slug collision with different title: FAIL with message & suggest new slug
  - On JSON/YAML serialization error: print failing key and exit non-zero
  - On git absence: SKIP git step, still report success for file ops

PRINT:
  - "Saved prompt '${TITLE}' as ${COLLECTION}/${SLUG}.md (v${VERSION})"
  - "SHA-256: <hash>"
  - "Index updated: ${PROMPTS_ROOT}/index.json"
  - "Mirrors written: ${ADDITIONAL_EXPORTS}"
RUN

```
