# R Learning Lab - Implementation Handoff

## 0. Your assignment

You are the implementation agent for **R Learning Lab**, a beginner-first Windows desktop companion for learning **R in the actual RStudio IDE**. This document captures the product decisions and desired implementation direction from the design discussion.

**Immediate goal:** inspect any existing repository/project, then build a focused, working MVP of the WPF companion. Favor a usable end-to-end learner flow over an extensive unfinished architecture. If an earlier `RLearningLab-PoC.zip` is available, inspect it as optional reference code, **not as the desired UI design**: that proof of concept used a code editor inside WPF, which is now explicitly out of scope.

**Core design rule:** WPF teaches, navigates, checks, and tracks. **RStudio is where the learner writes, executes, debugs, imports, manipulates, and plots R code.** Do not recreate an IDE, editor, REPL, plot window, or RStudio replacement in WPF.

## 1. Who this is for and what success looks like

The target learner has never coded, is not particularly tech-savvy, and may be intimidated by RStudio's multi-pane interface. Use short, direct instructions; explain any jargon before using it; encourage experimentation and reflection; treat errors as learning opportunities. The learner should not need prior knowledge of IDEs, file paths, terminals, or programming.

By the end, the learner should be able to independently:

- Open an RStudio Project, identify the Source editor, Console, Environment, Files, Plots, and Help panes, create/save/reopen `.R` scripts, write comments, and run code.
- Explain basic numbers, expressions, variables, assignment, types, vectors, functions, and data frames; use them in simple R code.
- Explain relative vs absolute paths, identify the *current R working directory*, and diagnose missing-file errors.
- Import CSV data through RStudio's UI and through R code, inspect it, transform/filter/sort it, and calculate basic summaries.
- Export CSV tables and charts (e.g. PNG and PDF) and verify the exported files.
- Create, interpret, and customize simple bar, histogram, scatter, and line plots.
- Complete a small, realistic end-to-end data-analysis exercise without step-by-step instructions.

The teaching pattern throughout: **brief concept -> guided actions in RStudio -> independent task -> check result -> questions to reflect on -> solution/explanation -> common errors**. Solutions must be accessible; this is a learning companion, not a high-stakes locked exam. Avoid punishing mistakes or locking the learner out after failed attempts.

## 2. Firm product decisions

1. **Windows desktop**: WPF / C# / modern .NET, ideally MVVM. The target is a normal Windows app and a straightforward distributable, not a browser-based application.
2. **No embedded R IDE**: no WPF code editor, syntax highlighting, REPL, data viewer, or plot designer. The earlier editor-based PoC was superseded by this decision.
3. **Real RStudio workflow**: the user opens an actual `.Rproj` and `.R` scripts in RStudio; writes/runs code there; then returns to WPF to submit/check the *saved script* or generated output.
4. **Real R for automated checks**: use `Rscript.exe` as a child process when verifying R code, not mock interpretation or matching literal strings. Manual/self-check tasks are appropriate when interaction with RStudio cannot be verified reliably (e.g., identifying the Console pane).
5. **Data-driven curriculum**: chapter/lesson/exercise content, hints, validation rules, expected assets, and answer explanations live in versioned JSON (or another easy-to-edit structured format), not inside C# UI code. Continuous example datasets are CSV files, not hardcoded UI fixtures.
6. **Persistent local data**: save learner progress, settings, submitted answers/reflections, and working scripts under `%LOCALAPPDATA%\RLearningLab\`. Use `%TEMP%` only for disposable execution scratch and transient output; never depend on Temp for progress.
7. **Continuous dataset**: a fictional `students.csv` study-habits dataset starts small and becomes more complex across lessons. Keep a pristine seed, and a learner working copy. Do not claim that correlations in a fictional dataset demonstrate causation.
8. **Beginner-friendly installation**: make R and RStudio prerequisites clear; detect them and give guided setup feedback if absent. A self-contained .NET executable does **not** bundle R or RStudio automatically. Bundling an R runtime later is a separate packaging/licensing decision.
9. **Portable paths**: use an RStudio Project to give a stable project root; teach project-root-relative paths; execute grading with the **same working directory** as the learner's RStudio Project.
10. **Accessible project files**: even though the workspace is in LocalAppData, expose clear buttons such as `Open Project in RStudio`, `Open Exercise File`, `Open Project Folder`, and `Open Outputs Folder`. Consider an optional user-selected workspace later, but keep LocalAppData as the default.

## 3. Proposed learner experience / app screens

### First run / Setup

- Welcome screen explains the relationship between R (language), RStudio (development environment), and R Learning Lab (learning guide).
- Detect `Rscript.exe`, the R executable/version, and RStudio. If missing, provide clear installation/check instructions and a way to select paths manually. Never silently assume paths under `C:\Program Files`.
- Create a learner workspace and RStudio Project from shipped templates, without overwriting existing work.
- Offer a one-click `Open Project in RStudio` action and explain what should appear.

### Course/lesson view

- Course navigation and visible progress; main lesson text in short sections; numbered tasks; small visuals/screenshots for UI orientation.
- Actions: `Open Project in RStudio`, `Open Exercise File` (prefer opening it in the already-open project), `Check My Work`, `Hint`, `Reveal Example Solution`, `Open Project Folder`, `Next Lesson`.
- Show plain-English feedback and simple expected/actual results, *not* an embedded R Console. RStudio remains the environment in which the learner sees and manipulates execution output.
- Reflection questions can be free-text with autosave; do not pretend subjective answers can be reliably scored by a strict equality checker.
- For UI familiarization tasks, use an explicit learner confirmation/checklist rather than covert click monitoring or fake auto-grading.

### Typical flow

1. WPF introduces a short concept, such as `#` comments, Source vs Console, or variables.
2. WPF instructs the learner to open the actual RStudio Project and the lesson's `.R` file (provided as a starter with comments).
3. Learner edits the script, runs it in RStudio, inspects the Console/Environment/Plots, and saves the script.
4. Learner returns to WPF and presses `Check My Work`.
5. WPF checks the saved script and/or expected output files, gives understandable feedback, persists attempts/progress/reflections, and offers hints or a reference answer.
6. The next lesson reuses concepts and, when appropriate, the evolving student dataset.

**Important:** avoid making the learner return to WPF after every line of R code. Group small related tasks into a reasonable exercise submission.

## 4. Curriculum outline and progression

Design the content to be completed at a self-paced beginner tempo. Each module has a short conceptual introduction, click-by-click guided work in RStudio, independent tasks, expected observations, reflection questions, hints, errors to try and recover from, and answers/explanations.

| Module | Topics and hands-on outcomes |
|---|---|
| 0. R and RStudio orientation | R vs RStudio; create/open `.Rproj`; identify Source, Console, Environment, Files, Plots, Help; Source can be absent until a script is opened; type `2 + 2`; create/save/reopen a `.R` script; `#` comments; run selected line with Ctrl+Enter; see output; make/fix a typo; understand scripts vs Console and that saving a script does not necessarily save the active Environment. |
| 1. R as calculator | Arithmetic, precedence, expressions, and reading printed output. |
| 2. Variables | `<-` assignment, meaningful names, overwrite values, perform arithmetic with variables; distinguish a calculated value from a live spreadsheet formula. |
| 3. Data types | Numeric, character, logical, `NA`, simple type inspection and common type errors. |
| 4. Vectors and functions | `c()`, indexing, `length`, `sum`, `mean`, and basic built-in functions; gentle introductions with no required loops. |
| 5. Data frames / tables | Rows, columns, `data.frame()`, `$`, `View`, `head`, inspecting data. Start with a few students. |
| 6. Files and paths | Folder trees; relative vs absolute paths; paths relative to **current R working directory**, not necessarily the script's folder; project root; `getwd()`, `list.files()`, `file.exists()`; `.`, `..`; Windows `/` vs escaped `\\`; deliberate wrong-path errors; `source('Scripts/file.R')`; why hardcoded `setwd()` inside scripts is usually discouraged. |
| 7. Importing | Use RStudio's Import Dataset UI and compare to `read.csv('Data/students.csv')`; understand CSV headers, data types, missing values, and whether a dataset has really been imported. Introduce optional Excel import only once CSV is understood. |
| 8. Manipulating data | Select, filter, sort, change/add columns/rows, correct intentional input mistakes; keep beginner-friendly Base R first. |
| 9. Summaries | Mean, median, counts, simple grouping and interpretation. |
| 10. Exporting tables | `write.csv(..., 'Outputs/students_export.csv', row.names = FALSE)`; output folder must exist; locate file; reopen it and confirm contents; understand why a path matters on export too. |
| 11. Building plots | Bar chart, histogram, scatter plot, line chart; identify suitable chart types; start with Base R, introduce ggplot2 later/optionally with explicit package setup. |
| 12. Customizing plots | Titles, axis labels, colors, legends, and appropriate scales; reflection on what each choice communicates. |
| 13. Exporting plots | Generate PNG/PDF; filename/path, device opening and closing (`png()`, `dev.off()`); confirm exported result; optional `ggsave()` if ggplot2 is taught. |
| 14. Final project | Open project, import data, inspect/fix/transform, summarize, visualize, export tables/graphs, and communicate a few findings. |

The sequence can be refined as implementation reveals dependencies; keep both early RStudio familiarization and explicit file/path handling before imports/exports.

### Continuous dataset

Use a clearly fictional student study-habits dataset. A five-row beginner fixture might look like:

```csv
student,study_hours,exam_score,coffee_cups
Anna,2,65,1
Ben,4,78,3
Clara,5,88,2
David,1,55,0
Emma,3,72,2
```

Later lessons can use a larger deterministic fixture with categories, missing values, or a few deliberately erroneous entries. Ensure datasets are **pedagogically consistent**: a student's completed lesson should not be invalidated because a later lesson changed their working CSV. The app should copy pristine datasets to the learner workspace and offer a deliberate reset (with a warning or backup) rather than overwriting learner edits.

## 5. Working directories and paths: non-negotiable details

Default workspace example (the username is not hardcoded):

```
%LOCALAPPDATA%\RLearningLab\
  progress.json
  settings.json
  Workspaces\Default\StudentStudy\
    StudentStudy.Rproj
    Scripts\
      lesson-00.R
      lesson-02.R
      ...
    Data\
      students.csv
    Outputs\
```

When the RStudio Project is open, the working directory should normally be the **project root**, `StudentStudy`, regardless of whether an edited script resides in `Scripts`. The curriculum must explicitly demonstrate:

```r
getwd()
list.files()
file.exists('Data/students.csv')
students <- read.csv('Data/students.csv')
source('Scripts/helpers.R')
write.csv(students, 'Outputs/students_export.csv', row.names = FALSE)
```

A relative path is resolved against `getwd()` during execution; it is **not intrinsically relative to the saved `.R` file**. An absolute path like `C:/Users/Alex/Documents/data.csv` identifies a specific location but is less portable. Demonstrate `.` and `..`, deliberate wrong paths, and using forward slashes on Windows. Demonstrate `setwd()` as a concept, but avoid encouraging hardcoded working-directory changes in reusable scripts.

The WPF grader must set `ProcessStartInfo.WorkingDirectory` to the same project root. Avoid silently changing working directories inside grading in a way that differs from the intended RStudio behavior. If a student's script explicitly calls `setwd()`, provide an intelligible error/explanation if that causes a mismatch.

**Workspace caveat:** LocalAppData is an excellent place for saved progress, but it's not easy for nontechnical users to find. The app must provide affordances for opening the workspace and exported files. Offer future workspace relocation/backup as a later enhancement.

## 6. Suggested technical structure

A lightweight, testable split is sufficient:

- `Views/` and `ViewModels/`: WPF views and state, preferably MVVM.
- `Models/` or `Domain/`: stable lesson/exercise IDs, lesson definitions, validation rules, learner progress and outcomes.
- `Services/CurriculumLoader`: reads JSON, validates schemas/required fields, loads assets, handles curriculum versions.
- `Services/WorkspaceService`: creates `.Rproj`, starter `.R` scripts, CSV fixture copies, output folders; never overwrites user edits without explicit consent.
- `Services/RInstallationService`: detects/selects `Rscript.exe`, reports R and RStudio status.
- `Services/RStudioLauncher`: opens the project and guides script opening; handle file associations and missing installation gracefully. Do not assume that launching an `.Rproj` and then an `.R` necessarily targets the same RStudio window.
- `Services/RExecutionService`: runs saved learner scripts via `Rscript.exe --vanilla` in a separate process, with redirected stdout/stderr, working directory, cancellation, and a sensible time limit.
- `Services/ExerciseGrader`: judges runtime results and output artifacts according to allowlisted JSON-defined validation kinds.
- `Services/ProgressService`: atomically saves progress under LocalAppData and restores it on restart.

Do not prematurely add a dependency-heavy editor component, a database, a web server, telemetry, accounts, AI features, or a custom R execution environment.

### Data-driven lesson example (illustrative; refine schema)

```json
{
  "schemaVersion": 1,
  "id": "variables-01",
  "chapterId": "02-variables",
  "title": "Calculate a total",
  "estimatedMinutes": 15,
  "conceptMarkdown": "A variable is a name for a stored value. In R, `<-` assigns a value.",
  "instructions": [
    "Open Scripts/variables-01.R in RStudio.",
    "Create price = 10 and quantity = 3.",
    "Calculate total using the two variables.",
    "Run the code and inspect the Environment pane.",
    "Save the script, then check your work here."
  ],
  "starterScript": "Scripts/variables-01.R",
  "hints": [
    "Use the assignment operator <-.",
    "Use * for multiplication: total <- price * quantity"
  ],
  "validation": [
    { "kind": "variableNumericEquals", "name": "price", "expected": 10 },
    { "kind": "variableNumericEquals", "name": "quantity", "expected": 3 },
    { "kind": "variableNumericEquals", "name": "total", "expected": 30 }
  ],
  "reflectionQuestions": [
    "What does <- do?",
    "If you change quantity to 5, why does total remain unchanged until you recalculate it?"
  ],
  "solutionScript": "Solutions/variables-01.R",
  "commonErrors": [
    "Using a variable before creating it.",
    "Forgetting to save the script before checking."
  ]
}
```

Do not treat one possible correct solution as the only acceptable code. For a result-based question, check variables and results; for exercises meant to teach a specific technique, define and transparently communicate additional constraints. A simple checker cannot reliably prove *how* a computation was done from its output alone.

Consider separate **instructional progress** (step viewed / learner confirmed), **attempts**, and **validated completion** so UI-only tasks are not mislabeled as automatically proven.

### Progress example (illustrative)

```json
{
  "schemaVersion": 1,
  "curriculumVersion": "0.1.0",
  "workspaceId": "default",
  "lessonStates": {
    "variables-01": {
      "attemptCount": 3,
      "passed": true,
      "lastCheckedUtc": "2026-10-27T12:00:00Z",
      "reflectionAnswers": ["...", "..."]
    }
  }
}
```

Use stable IDs, versioned schemas, validation when loading, and atomic writes (write temp file in the same destination directory, then replace/move). Updates must not erase prior scripts, datasets, or progress. Avoid tying completion status to lesson display names or filesystem order. For an MVP, JSON suffices; SQLite is unnecessary unless requirements demand complex querying/concurrency.

## 7. Running and grading real R code

Recommended initial workflow:

1. Ensure the learner has saved their `.R` script; explain that checking reads the file from disk, not unsaved changes in RStudio.
2. Create a unique temporary execution folder under `%TEMP%\RLearningLab\Runs\...` (not for durable progress).
3. Launch the detected `Rscript.exe` with `ProcessStartInfo.ArgumentList`, `UseShellExecute=false`, `CreateNoWindow=true`, redirected stdout/stderr, `WorkingDirectory=projectRoot`, `--vanilla`, and an app-generated grader script.
4. In the grader, `source()` the learner's saved script into a dedicated R environment (`new.env(parent=globalenv())` or an appropriately controlled parent) so variables remain inspectable. Catch R exceptions and report them in understandable terms.
5. Evaluate allowlisted checks from curriculum data: variable existence, scalar numerical comparison with tolerance, vector values/length, data-frame columns/rows and transformations, and expected exported file existence/format where appropriate.
6. Write machine-readable check results separately from the student's Console stdout/stderr (e.g. via a small controlled result-file protocol) so arbitrary student `print()` output is not mistaken for grading output. Keep detailed feedback strings in the WPF/content layer.
7. Support cancellation, timeout, process-tree termination, nonzero exit codes, truncated output limits, and cleanup. On failure, do not alter prior progress or the user's script.
8. Report distinguishable states: `not run`, `run failed`, `run succeeded but answer incorrect`, `passed`, and `self-confirmed`. The learner can retry as often as needed.

A beginner's script might be:

```r
# Create the variables and calculate the total.
price <- 10
quantity <- 3
total <- price * quantity
print(total)
```

The grader checks the resulting values. Do not simply search script text for exact strings; spacing, `<-` vs `=`, and equivalent valid expressions differ. If instruction explicitly demands use of variables or a technique, either add a targeted verification rule or use a guided/self-checked criterion rather than pretending value checks prove the method.

**Security boundary:** executing R code with `Rscript.exe` executes arbitrary code with the current Windows user's rights. A temp directory, process timeout, or `--vanilla` flag is **not a sandbox**. Do not market the feature as secure execution of untrusted third-party code. For this local educational MVP, make the limitation explicit and run only code the learner knowingly submits. Hardening/untrusted execution is separate future work.

## 8. UX and accessibility guidance

- Prefer plain English, short sentences, progressive disclosure, generous spacing, consistent actions, and keyboard-accessible controls.
- Use real annotated RStudio screenshots (maintainable against interface/version changes) for early UI orientation; do not attempt screen automation for the basic course.
- For every coding task, say *where to type* (Source vs Console), *how to run*, *what to expect*, and *when to save*.
- Explain errors without shaming. Provide an expandable technical error panel for advanced troubleshooting while keeping main feedback simple.
- Hints should be staged and optional. Solutions should include runnable code *and an explanation*, accessible without penalizing the learner.
- Teach good habits: save `.R` scripts, use comments, use projects/relative paths, inspect results in RStudio, and verify exports.
- Avoid making the app itself an obstacle; it is a companion, not a modal proctor.

## 9. Implementation milestones

### Milestone A - End-to-end vertical slice (build this first)

**Scope:** one Chapter 0 orientation exercise and one variable exercise. Deliver a WPF app that can initialize a workspace, open the RStudio Project, show JSON-backed lesson instructions/hints, point at/open the saved script, grade the variable exercise via real Rscript, show useful feedback, and persist progress under LocalAppData.

**Acceptance criteria:**

- [ ] Builds and launches on Windows; document prerequisite software and build/publish commands.
- [ ] Has **no embedded code editor**; all R code is written and run in real RStudio.
- [ ] Detects missing R/RStudio and guides the learner instead of crashing.
- [ ] Creates a working `.Rproj` and starter `.R` script, and opens/reveals them using buttons.
- [ ] Loads the lesson and its checks from JSON, not hardcoded C# exercise content.
- [ ] After saving a valid script in RStudio, `Check My Work` uses real R and passes; a wrong value fails with beginner-readable feedback; a syntax error displays understandable feedback.
- [ ] Learner can close/reopen WPF and find their saved code, attempts, and lesson state intact.
- [ ] Workspace, grader working directory, and instructions agree on relative paths.
- [ ] Reopening/updating a lesson does **not** overwrite edits.
- [ ] Cancellation/timeout and process failures do not freeze the UI.

### Milestone B - Data and path lessons

- Chapter 0 UI walkthrough content; first calculator/variables/vectors/data-frame lessons.
- Files/path lesson includes `getwd`, `list.files`, `file.exists`, relative/absolute examples, script vs working-directory distinction, and deliberate error recovery.
- Continuous fictional `students.csv` fixture and RStudio UI plus code CSV imports; correct file placement, backed-up seed data, data manipulation and CSV export.
- Multiple grader types and reflection-answer storage.

### Milestone C - Charts and final course

- Base R chart lessons (and optional ggplot2 introduction), plot customization, PNG/PDF export checks, final integrated mini-project, solutions and common-mistake explanations.
- Polished installer/publishing, backup/export/import learner progress, improved accessibility, realistic tests with novice users.

## 10. What to test

Use manual Windows smoke tests plus automated tests for non-UI logic where feasible:

1. Fresh install: no R and no RStudio; R only; both installed; unusual/custom install locations.
2. Create, open, edit, save, check, close, reopen, retry, reveal solution; persistence across restarts.
3. Pass and fail exercises; syntax errors; runtime errors; nonexistent variables; extra `print` output; malformed curriculum JSON; corrupt progress file with a recoverable backup.
4. Exercise reruns must *not* reuse stale prior variables or RStudio state. `Rscript` runs a clean, controlled process.
5. Working directory is project root in RStudio and grader; `Data/students.csv` works from a script under `Scripts/`; `students.csv` alone fails when not present in root.
6. Input/output paths with spaces and non-ASCII Windows username segments; do not build command lines by string concatenation.
7. Missing output folder, wrong CSV format, empty dataset, R script that runs too long, and cancellation.
8. Move/copy the entire project to another path and verify project-relative imports when opened from the new project root (if workspace relocation is supported).
9. RStudio file association not configured, and no already-open RStudio window.
10. Upgrading application content does not rewrite learner code/progress or silently reset datasets.

## 11. Deliverables and reporting

Provide:

1. A buildable WPF solution/project with readable organization and minimal dependencies.
2. JSON-driven curriculum loading with at least a Chapter 0 orientation item and a variable exercise; associated `.R` scripts, `.Rproj` template, and small CSV seed.
3. Real `Rscript.exe` validation, robust run/timeout/error handling, learner-friendly results.
4. LocalAppData persistence and a clear `Open Project Folder` affordance.
5. `README.md` covering prerequisites, getting started, building, publishing, the directory layout, execution/grading design, risks/limitations, and manual smoke tests.
6. A concise summary of what was implemented, how it was tested on Windows, and what remains incomplete. Do not claim tests or builds ran unless they actually did.

**Execution priority:** get Milestone A working before adding the full curriculum. Treat the curriculum above as product requirements/roadmap, not an instruction to generate all lessons before the first runnable release.

## 12. Non-goals and things to avoid

- No WPF R editor / console / in-app plot view or imitation of RStudio.
- No cloud accounts, telemetry, subscription, AI chat tutor, multiplayer, or server infrastructure in the MVP.
- No harsh exam scoring, locked solutions, or brittle string-matching graders.
- No hardcoded course exercises in WPF code, and no storing permanent progress under `%TEMP%`.
- No assumption that paths are relative to a script's file location; explicitly teach and test `getwd()` semantics.
- No requirement to install a complex set of R packages for the introductory course.
- No promise of security isolation simply because `Rscript` runs in a separate process.

## 13. Decision notes / open technical choices

The following are recommendations, not product decisions that should block progress:

- Exact .NET version and MVVM toolkit: choose the simplest supported Windows-targeted stack consistent with the repository.
- JSON schema structure and resource packaging strategy: keep it versioned, human-editable, and testable.
- Opening scripts in an already-open RStudio Project can be tricky via file associations; choose a reliable user-visible workflow and document its limitations rather than guessing.
- For first-run readiness, choose either explicit installed-R detection or an optional packaged R runtime, **but do not silently assume the .NET single-file build makes the whole system portable**.
- Progress storage can remain a single JSON file initially; SQLite is an optional later migration if needed.
- Future charts could use `ggplot2`, but don't impose it on the very first R tasks.

**Product north star:** the learner eventually no longer needs R Learning Lab because they can use real RStudio confidently on their own.
