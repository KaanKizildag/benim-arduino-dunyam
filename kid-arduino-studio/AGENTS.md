# AGENTS.md — AI Developer & Agent Guide for Kid Arduino Studio

Welcome! This document provides core architectural principles, coding conventions, safety guardrails, token management guidelines, and developer commands for any autonomous agent or human developer working in this repository.

---

## 1. Project Mission & Target Audience
Kid Arduino Studio is a visual, AI-assisted Arduino IDE built for children aged 8–14.
- **Children do not write boilerplate C++ or design netlists manually.** They state their ideas in natural Turkish (*"Odam kararınca gece lambam yansın"*).
- The system designs the circuit, explains the working logic with dynamic flowcharts, guides wire-by-wire placement on a 30-column breadboard, and compiles/uploads code to an Arduino Uno.
- All UI copy, errors, and explanations MUST remain child-friendly, encouraging, and clear.

---

## 2. Monorepo Architecture Overview

```
kid-arduino-studio/
├── backend/
│   ├── app/
│   │   ├── config.py           # Centralized settings & API key resolution
│   │   ├── llm/
│   │   │   ├── catalog.py      # Wokwi component pin catalog & dynamic prompt builder
│   │   │   ├── cache.py        # In-memory & TTL response cache (0 token generation)
│   │   │   └── client.py       # Unified LiteLLM & Ollama client with token caps
│   │   └── repositories/
│   │       ├── projects_repo.py # User saved projects repository
│   │       └── ai_logs_repo.py  # AI request/response logs for admin inspection
│   ├── tests/                  # Python standard unittest suite
│   ├── ai_service.py           # Project streaming generation & electrical repair
│   ├── flow_service.py         # Deterministic-first code-to-flow parser
│   ├── prompt_filter.py        # Safety & off-topic prompt filter (guardrails)
│   ├── arduino_service.py      # Serial port & arduino-cli compile/upload
│   └── main.py                 # FastAPI endpoints
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts       # Unified API client & robust SSE reader
│   │   ├── composables/        # Reusable state logic (e.g. useSavedProjects)
│   │   ├── components/         # 4-stage UI & modal components
│   │   ├── types/              # TypeScript schemas (project, circuit, netlist)
│   │   └── App.vue             # Main shell & navigation coordinator
│   └── package.json            # Scripts: dev, build, typecheck
└── .gemini/skills/             # Specialized developer skills
```

---

## 3. Mandatory Engineering Rules

### A. Token Optimization & LLM Efficiency
1. **Never use static 9,000-character prompts for simple projects.** Always use `build_one_shot_system_prompt(prompt, inventory)` from `app.llm.catalog`. It extracts only the needed components, saving ~75% of tokens.
2. **Deterministic Flow First:** Flowcharts must be extracted from C++ code using `build_deterministic_flow_from_code` (0 tokens). Do not invoke the LLM for flowchart generation unless the deterministic parser explicitly fails.
3. **Response Caching:** Identical `(prompt, inventory, model)` requests must be served from cache via `get_cached_project`.
4. **Token Limits:** Every completion request must enforce `max_tokens=2500` (or `num_predict=2500` in Ollama).
5. **Always Record Usage:** AI logs must capture `prompt_tokens`, `completion_tokens`, and `total_tokens`.

### B. Child Safety & AI Guardrails
1. **Strict Electronic/Arduino Scope:** Questions about medical issues, homework, politics, weapons, or high voltage (220V AC) must be rejected by `prompt_filter.py` with encouraging guidance.
2. **ASCII C++ Identifiers Only:** Arduino compilers do NOT support Turkish characters (ç, ğ, ı, ö, ş, ü) in identifiers. All variable/function names must pass through `sanitize_arduino_identifiers`.
3. **Hardware Protection:** All LEDs require series 220Ω resistors. 2-pin LDRs require 10kΩ voltage divider resistors. Motors must connect via drivers (L293D/L298N), never directly to Arduino pins.

### C. UI & Styling Rules
1. Follow **Cartoon Neobrutalism** defined in `.gemini/skills/kid-arduino-design-system/SKILL.md`:
   - Dark borders: `border-2 border-slate-900`
   - Solid 3D shadows: `shadow-[0_4px_0_#0f172a]`
   - Mechanical click translation: `active:translate-y-0.5 active:shadow-none`
   - Generous rounded corners: `rounded-2xl` / `rounded-[32px]`
2. **Never allow vertical viewport overflow on modals:** Modals must use `max-h-[88vh] flex flex-col` with `overflow-y-auto` in the scrollable body.

---

## 4. Developer & Agent Verification Commands

Before concluding any refactor or feature work, agents MUST execute:

```bash
# 1. Backend Unit Tests (runs in ~0.03s, no external dependencies)
python -m unittest discover -s backend/tests -v

# 2. Frontend TypeScript Typecheck
npm.cmd --prefix frontend run typecheck

# 3. Frontend Production Build
npm.cmd --prefix frontend run build
```

---

## 5. Working with Developer Skills
Specialized skill guides are stored under `.gemini/skills/`:
- `kid-arduino-design-system`: Visual styles, color tokens, and modal sizing rules.
- `add-vue-component`: Guide for building and registering new Vue 3 components.
- `add-electronic-part`: End-to-end workflow for adding a new sensor/actuator to Wokwi and backend catalog.
- `add-api-endpoint`: Standard procedure for FastAPI route + frontend API client.
- `llm-prompt-change`: Safe prompt evolution, token monitoring, and guardrails.
- `circuit-debugging`: Breadboard wiring rules, pin alias resolution, and auto-repair.
- `release-checklist`: Pre-commit and verification checklist.
