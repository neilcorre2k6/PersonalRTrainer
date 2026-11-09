# R Learning Lab - developer handoff

Snapshot: **2026-10-27**. Application/curriculum version: **1.0.0**.

This document describes the implemented project and the remaining work. It is context for a future maintainer, not authorization to run commands, change files, install software, or publish a release. Follow the user's current instructions before taking action.

## 1. Start here

The project folder is `C:\Users\neil.mark.corre\Documents\Personal\RTrainer`.

| Item | Location / purpose |
| --- | --- |
| Original product requirements | [RLearningLab_Agent_Handoff.md](RLearningLab_Agent_Handoff.md). Preserved separately from this implementation snapshot. |
| Source solution | [RLearningLab.sln](RLearningLab.sln) |
| Ready-to-run release | `dist/RLearningLab.exe`, with its adjacent `Content` folder |
| Packaged release | `RLearningLab-win-x64.zip` |
| Technical overview | [README.md](README.md) |
| Learner instructions | [USER_GUIDE.md](USER_GUIDE.md) |
| Actual verification and exclusions | [TESTING.md](TESTING.md) |
| Official curriculum references | [REFERENCES.md](REFERENCES.md) |
| Build/test/publish helper | [build.ps1](build.ps1) |

The original handoff was a specification. Do not confuse its requested features with verified implementation. Use the source, this snapshot, and TESTING.md to distinguish delivered behavior from future work.

## 2. Product model and current delivery

R Learning Lab is a beginner-oriented Windows WPF companion. It teaches, navigates, checks saved scripts, and records progress. **RStudio remains the actual coding environment.** The companion displays read-only examples; it has no embedded code editor, R Console, data viewer, or plot viewer.

The implemented course contains **23 lessons across all 15 modules, numbered 0 through 14**. It includes concepts, guided actions, independent exercises, expected observations, staged hints, reference solutions with explanations, reflection questions, common errors, and official R/Posit reference links. Twenty-two lessons have automatic R checks; the first orientation lesson uses learner confirmation. Many automatically checked lessons also require explicitly self-confirmed observations.

The source targets .NET 8 with WPF for Windows. The delivered Windows x64 executable includes .NET/Windows Desktop runtime 8.0.33. It still needs separately available R and RStudio. No additional R packages are needed for the shipped course. There is no installer or code signing.

## 3. Code map

| File | Responsibility |
| --- | --- |
| `src/RLearningLab.Core/Models.cs` | Curriculum, validation, settings, progress, and run-result models; shared JSON serialization options. |
| `src/RLearningLab.Core/Storage.cs` | `SafePaths`, `JsonStore`, `WorkspaceService`, and `CurriculumLoader`. |
| `src/RLearningLab.Core/Installations.cs` | R/RStudio discovery, R version probing, and child-process locale cleanup. |
| `src/RLearningLab.Core/RExecutionService.cs` | Real R process lifecycle, generated grading wrapper, output protocol, validation and artifact freshness. |
| `src/RLearningLab.App/App.xaml` | Shared control styles and resources. |
| `src/RLearningLab.App/App.xaml.cs` | Startup, content/data paths, diagnostic command-line options, and initial window sizing. |
| `src/RLearningLab.App/MainViewModel.cs` | Lesson navigation, completion indicators, and course progress. |
| `src/RLearningLab.App/MainWindow.xaml` and `.xaml.cs` | Lesson views, dynamic content, launch buttons, check/cancel actions, reflection autosave, and internal UI smoke mode. |
| `src/RLearningLab.App/SetupWindow.xaml` and `.xaml.cs` | Installation paths, version check, execution acknowledgement, and backed-up dataset restore. |
| `tests/RLearningLab.Tests/Program.cs` | Executable test harness with local-logic and optional real-R integration tests. |

The structure is deliberately lightweight. There are navigation/progress view models, but dynamic lesson rendering and UI orchestration also live in code-behind. Do not describe it as a fully separated MVVM implementation. There is no third-party MVVM toolkit, database, server, account system, or telemetry service.

## 4. Curriculum and authoring

The application reads [Content/curriculum.json](Content/curriculum.json), schema version 1. Its templates live under `Content/Workspace`:

```text
StudentStudy.Rproj
Scripts/       # independent exercise starters, plus helpers.R
Solutions/     # complete example scripts
Data/          # pristine CSV fixtures
Outputs/       # the learner workspace creates this directory
```

[tools/build_curriculum.py](tools/build_curriculum.py) is the authoring source. Running it regenerates the shipped curriculum JSON, starter scripts, solutions, datasets, project template, and REFERENCES.md. Editing only a generated JSON or template file will not survive the next regeneration. Python 3 is required for authoring regeneration, but not for building or running the application.

Use the existing authoring definitions as the examples for adding a lesson. Each lesson supplies a stable ID, module information, teaching sections, instructions, script paths, hints, reflection questions, self-check criteria, validation rules, and references. `CurriculumLoader` performs required-field, path, asset and rule checks; a separate formal JSON Schema file is not supplied.

Important maintenance details:

- Lesson IDs anchor saved progress. Preserve existing IDs when refining a lesson.
- Reflection answers and self-check confirmations are keyed by their question/criterion text. Changing that wording needs a deliberate migration if existing answers must remain associated with the new text.
- The test harness currently expects 23 lessons and all 15 modules. An intentional course expansion requires updating that assertion as well as its content.
- Existing learner files are never refreshed automatically just because their shipped starter or solution changes. Plan content upgrades explicitly.
- The app reveals the shipped solution from `Content/Workspace/Solutions`, rather than trusting an edited solution in the learner's working copy.
- Reference links supplement offline teaching. Official RStudio screenshot walkthroughs are linked; screenshots are not bundled into the lessons.

### Dataset contract

`students.csv` is the stable five-student fixture. `students_extended.csv` is a separate twelve-student fixture with groups A/B, one missing hours value, and Clara's deliberate `880` score typo. The correction specified in the lessons is `880` to `88`.

After correction, group A's mean score is 80 and group B's is 65, each from six students. Eleven students have known study hours. Exercises and checks depend on these fixtures. Changing them requires reviewing lesson expectations and reference solutions together. The data are fictional and support no real-world causal claims.

## 5. Workspace, saves and completion

The normal durable data root is `%LOCALAPPDATA%\RLearningLab`:

```text
settings.json
progress.json
progress.json.bak
Workspaces/Default/StudentStudy/
  StudentStudy.Rproj
  Scripts/
  Solutions/
  Data/
  Outputs/
  Backups/
```

`WorkspaceService.Initialize()` copies only missing template files. Existing scripts, data, project files and outputs stay intact. Setup offers an explicit restore of either dataset, with confirmation and a backup of the current CSV in the workspace's `Backups` directory.

`JsonStore` writes a unique temporary file beside its destination, flushes, and replaces the primary save while retaining a `.bak`. Corrupt saves are preserved and a prior backup is recovered when available. Unknown future schema versions are reported without rewriting them. Progress save errors appear in the UI and can trigger a warning on close.

Progress records viewed state, attempt count, prior success, latest outcome/time, confirmations, and reflections. Completion requires prior success plus all observation criteria for that lesson. For the orientation lesson, success means explicit self-confirmation. Failed retries preserve prior success. Reflections are not automatically scored. There are no navigation locks or retry penalties. Prior detailed check feedback is not persisted.

## 6. Execution and grading contract

1. The learner intentionally saves a script and selects **Check My Work**.
2. The app starts `Rscript.exe --vanilla` with `ProcessStartInfo.ArgumentList` and the StudentStudy **project root** as working directory.
3. A generated wrapper sources the saved script into a dedicated environment in that fresh R process.
4. Allowlisted checks evaluate resulting objects and output artifacts.
5. Machine-readable results go into a separate scratch result file, not stdout. The UI translates the results into feedback and saves progress.

The default execution limit is 20 seconds. The runner supports cancellation, process-tree termination, redirected stream draining, bounded retained diagnostics, nonzero exits, and scratch cleanup. Scratch is normally under `%TEMP%\RLearningLab\Runs`; it is not used for durable progress. Incidental check-time plots are directed to scratch.

Supported rule kinds are `numeric`, `value`, `vector`, `type`, `rows`, `columns`, `columnValues`, `file`, `csv`, `png`, and `pdf`. Numeric checks use a tolerance, normally 0.000001. `columns` requires the listed columns to exist; it does not reject every additional column. CSV checks compare expected column names/order and can compare exported values with a named result table. PNG/PDF checks inspect signatures, not visual correctness. Artifact checks also require a change in timestamp/size from before the run, so an unchanged leftover export does not pass.

Value checks cannot prove the learner used a particular technique. UI actions, chart appearance and reasoning remain transparent self-checks. This is a learning checker, not a tamper-resistant examination system.

**R execution is not sandboxed.** A separate process, dedicated environment, timeout and `--vanilla` do not isolate arbitrary R code from the user's files. The app requires an execution acknowledgement, and code runs with the current Windows user's permissions. Cancellation cannot undo side effects already performed by that code.

The runner removes an inherited Unix-style `C.UTF-8` locale setting when starting Windows R. This fixes the accented-path failure encountered during integration testing; retain the Unicode-path regression coverage.

## 7. Build, test and package

Run from the project root when authorized:

```powershell
dotnet build RLearningLab.sln -c Release

# Explicit R path avoids accidentally skipping integration tests.
dotnet run --project tests/RLearningLab.Tests -c Release -- `
  "$PWD" "$PWD\tools\.runtime\R\app\bin\Rscript.exe"

# Build, test, publish and copy notices/documentation to dist.
.\build.ps1 -Rscript "$PWD\tools\.runtime\R\app\bin\Rscript.exe"
```

The extracted R above is development tooling, not part of the distributable. A separately installed `Rscript.exe` can be supplied instead. Without a usable R path, the harness runs local tests and explicitly skips R integration tests; that is not equivalent to the recorded full verification.

`build.ps1` defaults to runtime 8.0.33 and a self-contained x64 release. It uses a project-local NuGet package cache under `tools/.runtime/nuget`, copies runtime license notices, and writes `dist/SHA256.txt`. `-FrameworkDependent` selects a smaller build requiring an installed .NET Desktop Runtime. Review the supported runtime version before future releases.

The helper does **not** regenerate curriculum or rebuild the ZIP. Its documentation-copy list currently contains START-HERE.txt, README.md, REFERENCES.md and TESTING.md. The HANDOFF.md and USER_GUIDE.md added with this documentation update are in the project root; include them explicitly if refreshing the distribution documentation.

For an authorized ZIP refresh after publishing:

```powershell
Compress-Archive -Path dist/* -DestinationPath RLearningLab-win-x64.zip `
  -CompressionLevel Optimal -Force
```

Keep `Content` beside the executable and retain `Licenses`. Do not ship `tools/.runtime`, test learner workspaces or development artifacts as application prerequisites.

## 8. Recorded verification

The existing reports were checked while preparing this handoff. This documentation-only update did not rerun builds or tests.

- Release build: zero warnings and zero errors.
- Full test harness: **43/43 passed**, using real R 4.6.1.
- All 22 automatically checked reference solutions passed, including the capstone exports.
- Final self-contained executable: desktop smoke run exited 0, loaded 23 lesson views and produced six captures, including a 1024 by 720 layout.
- The desktop run disabled installed .NET lookup and kept bundle extraction/test data under project artifacts.

Evidence is in `artifacts/latest-test-results.json`, `artifacts/tests/run-20261027202323097/test-results.json`, `artifacts/release-ui/ui-smoke.json`, and the six PNGs beside that UI report. TESTING.md records the scope and exclusions. Earlier blank sandbox captures are not valid visual evidence; the final desktop captures are the accepted set.

## 9. Remaining work, in suggested order

1. **Verify the real RStudio workflow.** RStudio was absent here. Test project launch, opening a script in the intended project, edit/run/save/check, restart, file associations, custom installation paths and multiple open RStudio sessions.
2. **Complete the manual Windows checklist** in README.md, including save-error dialogs, close during execution, restore interactions, keyboard use and display scaling.
3. **Evaluate with beginners and assistive technologies.** All curriculum topics are covered, but novice comprehension, screen readers and high-contrast behavior have not been validated.
4. **Plan content updates and data backup UX.** Automatic migration, workspace relocation and progress import/export are not implemented.
5. **Prepare a wider release if wanted.** Installer, code signing, optional Excel/ggplot2 lessons, translations and maintained screenshot assets remain future work.

Known RStudio limitation: launching an `.Rproj` and then an `.R` through the executable does not establish that both target the same existing session. The current UI tells the learner to confirm StudentStudy and, if needed, use **File > Open File** inside that project. Do not claim reliable same-window launching until it has been tested and improved.

## 10. Suggested next session

Read this snapshot, the original requirements and TESTING.md. Inspect the current files for changes since this snapshot. The most useful next step is the real RStudio manual walkthrough, followed by focused fixes based on observed behavior. Preserve existing learner work, stable IDs, project-root path semantics and the distinction between automatic proof and learner confirmation.
