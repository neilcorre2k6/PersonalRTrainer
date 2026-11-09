# R Learning Lab

A Windows WPF companion for learning R in the real RStudio IDE. The course covers all 15 modules in the handoff through 23 lessons, from opening a project to a complete data-analysis exercise. It includes original teaching text, guided practice, independent tasks, staged hints, runnable reference answers, reflections, common errors, and official documentation links.

## Run the application

Open `dist\RLearningLab.exe` for the self-contained Windows x64 release. **Keep its `Content` folder alongside it.** No administrator rights are required. R and RStudio are separate prerequisites; the companion does not install or bundle them.

If you use the optional `dist-framework-dependent` build, install the **.NET 8 Desktop Runtime, x64**, or run it on this development machine, where the runtime is already installed. The source uses .NET 8 and can be built using a compatible .NET 8 or newer SDK.

1. Install [R for Windows](https://cran.r-project.org/bin/windows/base/).
2. Install [RStudio Desktop](https://posit.co/download/rstudio-desktop/). Check Posit's current Windows requirements for the version you choose.
3. Open the companion, choose **Setup & tools**, and detect or browse to `Rscript.exe` and `rstudio.exe`. Use **Check R version** to verify R can start.
4. Read and acknowledge the local execution notice if you want automatic checks. You can read all lessons without it.
5. Choose **Open Project in RStudio**. Confirm the active project is `StudentStudy`.
6. Open the lesson's actual `.R` file in RStudio. Read the Learn tab, write your independent answer in Source, run it with Ctrl+Enter, and save with Ctrl+S.
7. Return to **Practice & check**, check your saved work, and confirm any observations. Reflections autosave locally and are never automatically scored.

No R packages beyond the standard R distribution are needed. Base R is used throughout. Excel and ggplot2 are optional future extensions, not required parts of this course.

## What is included

| Module | Lessons and practice |
| --- | --- |
| 0 | R / RStudio / companion roles; panes; Console vs Source; projects; comments; save/reopen; typo recovery; session memory |
| 1 | Arithmetic, precedence, parentheses, powers and division |
| 2 | Assignment, meaningful names, overwriting values, recalculating derived values |
| 3 | Numeric / character / logical data, inspection, comparison, NA and missing-value summaries |
| 4 | Vectors, indexing, length / sum / mean; a small function extension without loops |
| 5 | Data frames, rows and columns, `$`, `head`, `str`, `View` |
| 6 | Working directories, folder trees, relative / absolute paths, `.` / `..`, Windows separators, `source`, deliberate path errors, `setwd` recovery |
| 7 | RStudio base import wizard, saved CSV import, headers, types, missingness and input mistakes |
| 8 | Selecting, filtering, sorting whole rows, correcting data, derived columns, adding/removing rows |
| 9 | Means, medians, counts, grouping, denominators and interpretation |
| 10 | CSV export, output directories, row names, reimport and verification |
| 11 | Bar charts, histograms, scatter plots and ordered line charts |
| 12 | Titles, units, scales, colors, symbols and legends |
| 13 | RStudio export options, reproducible PNG/PDF devices, closing devices, inspecting files |
| 14 | Independent import → clean → summarize → visualize → export → verify → explain project |

The five-row `students.csv` stays stable. A separate twelve-row `students_extended.csv` adds groups, one missing hours value, and a documented `880` → `88` typo for cleaning practice. Both fixtures are fictional. The extended table's corrected group means are A = 80 and B = 65; each group has six students. Eleven students have known study hours. These examples do not support causal or population claims.

Official R and Posit sources are linked per lesson and indexed in [REFERENCES.md](REFERENCES.md). Early orientation links go directly to the official screenshot walkthroughs. The app includes textual pane orientation; screenshots are not bundled, so visiting the current official screenshots requires internet.

## Build, test and publish

From PowerShell in this folder:

```powershell
dotnet build RLearningLab.sln -c Release
dotnet run --project tests/RLearningLab.Tests -c Release -- "C:\path\to\RTrainer"

# Supply R explicitly to run every reference solution and the integration suite:
dotnet run --project tests/RLearningLab.Tests -c Release -- "C:\path\to\RTrainer" "C:\Program Files\R\R-x.y.z\bin\Rscript.exe"

# Self-contained Windows x64 executable; requires Microsoft runtime packages at restore:
dotnet publish src/RLearningLab.App -c Release -r win-x64 --self-contained true `
  -p:RuntimeFrameworkVersion=8.0.33 `
  -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true `
  -p:EnableCompressionInSingleFile=true -p:DebugType=embedded -o dist

# Smaller alternative requiring a separately installed .NET 8 Desktop Runtime:
dotnet publish src/RLearningLab.App -c Release --self-contained false -o dist-framework-dependent

# Combined build/test/publish helper:
.\build.ps1 -Rscript "C:\path\to\Rscript.exe"
```

`build.ps1 -FrameworkDependent` selects the smaller alternative. Build/publish and tests do not require Python. Curriculum authors can run `python tools/build_curriculum.py` to regenerate shipped JSON and templates from the authoring source. This rewrites shipped course assets only, never a learner workspace. Python 3's standard library is sufficient. Rebuild after authoring.

The app has an internal offscreen UI smoke mode:

```powershell
.\dist\RLearningLab.exe --smoke-test=C:\path\to\RTrainer\artifacts\ui-smoke
```

This initializes isolated test learner data under that directory, loads every lesson view, captures the main tabs and setup screen, and records a JSON result. It does not launch RStudio or run learner scripts. `--data-root=C:\some\folder` is a diagnostic override for isolated persistence tests; the normal workspace is always LocalAppData.

## Source organization

```text
RLearningLab.sln
src/
  RLearningLab.Core/       Models, curriculum loader, workspace, JSON store,
                          prerequisite detection, real R execution/grading
  RLearningLab.App/        WPF views, navigation/progress view models, setup
tests/RLearningLab.Tests/  Dependency-free executable test harness
Content/
  curriculum.json         Versioned lesson content and allowlisted checks
  Workspace/
    StudentStudy.Rproj
    Scripts/              Commented learner starter scripts and path helper
    Solutions/            Runnable reference answers
    Data/                 Pristine fictional CSV fixtures
tools/build_curriculum.py Curriculum authoring source
artifacts/                Test reports and smoke captures (development only)
dist/                     Self-contained distributable, when published
```

No embedded editor, REPL, RStudio imitation, plot viewer, database, account system or telemetry is included. WPF displays read-only examples and explanations. RStudio is where learners edit, execute, debug, inspect data and view plots.

## Learner data and preservation

Normal saved data:

```text
%LOCALAPPDATA%\RLearningLab\
  settings.json
  progress.json
  progress.json.bak
  Workspaces\Default\StudentStudy\
    StudentStudy.Rproj
    Scripts\
    Solutions\
    Data\
    Outputs\
    Backups\
```

Startup copies only missing workspace files. It never overwrites an existing script, dataset, project or output. Stable lesson IDs anchor progress independently of lesson titles and ordering. New content can add missing files, but there is no automatic destructive migration. A changed starter for an existing ID will not replace learner work.

Progress separates viewed lessons, attempts, prior automatic success, self-confirmed observations and free-text reflections. Passing an automatic check does not claim an RStudio click or visual design was verified. A lesson completes when its check/confirmation and all observation criteria are satisfied. A failed retry preserves an earlier success. There is no scoring penalty, solution lockout or navigation gate.

JSON saves use a unique temporary file beside the destination, flush it, then replace the primary file while keeping the prior version as `.bak`. Invalid JSON is preserved in a `.corrupt-*` file; the previous backup is recovered when possible. Unknown future schema versions are left untouched and reported. Save errors are visible, including a close warning if the latest progress could not be saved.

**Setup & tools** can restore either CSV from the pristine shipped seed. It asks first, backs up the current CSV into `Backups`, and leaves scripts and progress intact. Restoring a CSV can change the result of scripts that intentionally depended on edited data; rerun and inspect them. Workspace relocation, a backup/export wizard, and a content-migration UI remain future enhancements. For manual backup, close the companion and copy the entire LocalAppData RLearningLab folder.

## Execution and grading

The checker reads the saved `.R` file, starts `Rscript.exe --vanilla` in a fresh process, and sets its working directory to the **StudentStudy project root**, not Scripts. Each check uses a unique disposable scratch directory under `%TEMP%\RLearningLab\Runs`. Progress is never stored in Temp.

The wrapper sources the learner script into a dedicated environment and evaluates allowlisted rule kinds: numeric scalars with tolerance, values/vectors/types, data-frame row counts/columns/column values, output existence, CSV schema/value round trips, and PNG/PDF signatures. Rules and expected values come from JSON. No curriculum-provided arbitrary R expression is evaluated as a validation rule. Result messages are written to a separate bounded file using a small UTF-8 hex protocol; student printed output cannot be mistaken for check results. Stdout/stderr are drained independently and retained with a size limit for optional troubleshooting details.

Runs have a 20-second limit, cancellation, process-tree termination, nonzero-exit handling and scratch cleanup. The UI stays asynchronous. Incidental plots during checks go to disposable scratch; learners inspect actual plots in RStudio. Export checks additionally require a changed file timestamp/size, preventing an old output from passing without regeneration. Checks do not delete previous learner outputs. Export commands can replace their named files as normal R behavior.

Checking distinguishes not run, execution failure, incorrect results, passed, cancelled and timed out. UI-only lessons are self-confirmed. Numeric checks verify results, not the exact technique or reasoning; technique/design criteria are transparently self-checked. PNG/PDF checks are structural signature checks, not a visual correctness judge. The learner must open the files and verify appearance/dimensions. Reflections are stored, not graded by string equality.

**Security:** R scripts execute with the current Windows user's rights. A fresh process, dedicated environment, `--vanilla`, timeout and Temp directory are not a security sandbox. Run only code you knowingly choose to submit. The app requires an explicit execution acknowledgement in Setup. It does not download or execute third-party lesson code, sandbox hostile scripts, or guarantee recovery from a deliberately destructive script. Process cleanup cannot undo a script's side effects.

## RStudio launch limitation

Opening `.Rproj` and `.R` files through RStudio's executable does not reliably guarantee the same existing RStudio window across every version and session configuration. Always confirm `StudentStudy` is active and `getwd()` reports its root. If **Open Exercise File** selects a different window, open the project first, then use **File > Open File** inside that session to open the displayed `Scripts/...` path. The companion reports this guidance instead of silently assuming the launch target. It does not automate or monitor RStudio clicks.

## Manual Windows smoke checklist

- With R/RStudio absent, open lessons and confirm Setup guides installation without a crash. Repeat with R only, both tools, custom installation paths and missing file associations.
- Open the project and exercise in RStudio. Edit, run, save, check, retry, reveal hints/solution, enter reflections, close and reopen both apps.
- For variables, try correct values, a wrong total, a missing object, unsaved edits, a syntax error and a runtime error. Check should use disk content and a fresh process.
- Try `Sys.sleep(60)` in a disposable exercise; cancel it, retry, then let a run time out. Close during a check and confirm the app cancels before exit.
- Exercise project-relative imports from scripts under Scripts. Try a deliberate missing filename; restore the correct path and ensure `setwd()` is not left pointing elsewhere.
- Export both CSV and images. Open the artifacts, check dimensions/labels, then rerun without export commands and confirm stale files fail.
- Restart the companion after editing scripts and CSVs; confirm edits remain. Restore a dataset only deliberately and inspect its backup.
- Check keyboard navigation, visible focus, scrolling, window resizing, scaling and screen-reader names with real users. Official pane screenshots may differ with RStudio versions/layout settings.

The executable test harness covers preservation, schema/path validation and storage recovery, and, when real R is supplied, all 22 automatically checked reference solutions plus failure, timeout/cancellation, clean-state, output-drain, working-directory and artifact cases. It writes timestamped JSON reports under `artifacts/tests` and a latest report at `artifacts/latest-test-results.json`. It explicitly reports skipped R integration tests if R is unavailable. Actual verification performed for this delivery is recorded in `TESTING.md`; the checklist above is not a claim that every manual scenario was performed.

## Distribution notes

The self-contained build includes the .NET runtime, but **does not bundle R or RStudio**. Keep the complete distribution folder together or distribute its ZIP. Rebuild with current Microsoft runtime packages for future releases. This development release is unsigned, so Windows or organizational application controls may show their normal trust prompts. An installer, code signing, progress import/export, translated lessons, optional ggplot2/Excel lessons, automated screenshot maintenance, and novice-user accessibility/usability studies are not included.
