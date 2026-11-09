# Verification — 2026-10-27

## Environment and release

- Windows 11, build 22631, x64.
- Build SDK: .NET 9.0.304. Source targets .NET 8 / WPF.
- Self-contained Windows x64 release includes Microsoft .NET and Windows Desktop runtime **8.0.33**.
- Real R tests use **R 4.6.1 (2026-06-24)**, downloaded from CRAN and extracted project-locally. Nothing was installed system-wide.
- The R installer has a valid Authenticode signature and matches CRAN's published MD5 `7907f3a20ec8ec88cd0da279024b8e27`. The extraction tool ZIP matches its publisher's checksum.
- RStudio is not installed on this machine; actual RStudio launch/window selection was not exercised.

## Build and automated tests: passed

`dotnet build RLearningLab.sln -c Release --no-restore` succeeded with **0 warnings and 0 errors**.

The executable test harness passed **43/43 tests**, using real `Rscript.exe`:

- All 23 lessons have required content and assets, covering modules 0–14.
- Every one of the 22 automatically checked reference solutions passes in a fresh real-R process, including the final analysis, both CSV exports and both chart exports.
- Paths containing spaces and `é` work throughout the integration suite.
- Equivalent code, alternative assignment syntax and extra printed output are accepted.
- Incorrect values, missing objects, syntax errors, runtime errors and nonzero R exits produce distinguishable outcomes.
- Prior objects do not leak between checks.
- Timeout and cancellation terminate long-running R execution.
- Large stdout is drained with bounded retained diagnostics.
- A changed working directory is reported intelligibly.
- Stale export files fail unless regenerated. Wrong image signatures and malformed CSV exports fail.
- Unique execution scratch folders are removed after success, error and cancellation.
- Reinitialization preserves scripts, edited CSVs and existing outputs.
- Dataset restore preserves a backup and leaves scripts intact.
- Atomic JSON storage round-trips progress, attempts, confirmations and Unicode reflections.
- Corrupt JSON and invalid save structures recover from backups while preserving damaged content.
- Unknown future schema versions are not rewritten.
- Traversal paths and unknown validation kinds are rejected.
- Missing R produces a guided not-run result and preserves scripts.

Machine-readable evidence: `artifacts/latest-test-results.json`. Timestamped full run: `artifacts/tests/run-20261027202323097/test-results.json`.

The first integration run caught an inherited Unix-style `C.UTF-8` locale that Windows R rejected. The runner now removes that invalid inherited setting in the child process, allowing Windows R to select its native UTF-8 locale. The final tests include the accented workspace path and pass.

## Final executable and UI: passed

The published **dist/RLearningLab.exe** was launched on the interactive Windows desktop in its isolated offscreen smoke mode. Installed .NET lookup was disabled with a nonexistent `DOTNET_ROOT` and `DOTNET_MULTILEVEL_LOOKUP=0`; native bundle extraction and learner test data were directed into `artifacts`.

The application exited with code **0** and reported success. It loaded all 23 lesson views, opened a hint and reference solution, and captured six views, including the compact **1024 × 720** layout. The final capture routine rejects a completely blank render rather than reporting it as a successful screenshot.

Visually inspected captures:

- `artifacts/release-ui/01-orientation.png`
- `artifacts/release-ui/02-practice.png`
- `artifacts/release-ui/03-reflections.png`
- `artifacts/release-ui/04-references.png`
- `artifacts/release-ui/05-setup.png`
- `artifacts/release-ui/06-compact-practice.png`

UI result: `artifacts/release-ui/ui-smoke.json`.

The initial sandbox captures were blank and were **not** accepted as visual verification. The normal-desktop run replaced that limitation. Visual checking also caught a read-only progress binding and missing capture backgrounds; both were fixed before the final publish and screenshots.

The final project's R-generated scatter PNG was opened and visually inspected: labels, group symbols, legend and the 11 complete pairs appear correctly. CSV and PDF exports also pass the real-R checks. No automated claim is made about the visual correctness of a learner's arbitrary chart.

## Not claimed as tested

- An actual learner editing/saving in a real RStudio window, installation detection against installed RStudio, multiple RStudio windows, file associations and custom RStudio installations.
- End-to-end UI clicks through every failure, restore and save-error dialog; the underlying logic is tested separately.
- Screen readers, high-contrast mode, every DPI scale, non-x64 Windows, other Windows releases, organizational application controls, or usability with novice learners.
- Installer, code signing, automatic content migration, workspace relocation and progress import/export: these features are not part of this release.

The README contains the remaining manual Windows smoke checklist and the known RStudio window-selection limitation. The app remains usable for reading lessons when R and RStudio are absent, and explicitly reports those missing prerequisites.
