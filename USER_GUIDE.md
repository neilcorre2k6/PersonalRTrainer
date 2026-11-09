# R Learning Lab - user guide

Version 1.0.0. Written 2026-10-27.

R Learning Lab helps you learn R by practicing in the real RStudio application. Read and check your lessons in the companion; write, run and debug your R code in RStudio.

## 1. Open the application

From this project folder, open **dist/RLearningLab.exe**. If you received the ZIP, extract the whole ZIP to a folder first, then open RLearningLab.exe there.

Keep the **Content** folder beside the executable. The executable includes the .NET runtime, so the supplied release does not require a separate .NET installation. R and RStudio are separate tools and are not bundled.

| Tool | What it does |
| --- | --- |
| R | Performs the calculations and runs R instructions. |
| RStudio Desktop | Gives you a place to write scripts, run code, inspect tables and see plots. |
| R Learning Lab | Explains concepts, gives exercises, checks saved work and remembers progress. |

The course uses standard R functions. No extra R packages are required.

## 2. Connect R and RStudio

1. Open **Setup & tools** near the top-right of the companion.
2. If R is missing, choose **Get R for Windows** and install R.
3. If RStudio is missing, choose **Get RStudio Desktop** and install it.
4. Choose **Detect again**. If a tool is still missing, use its Browse button to locate the executable.
5. For R, select **Rscript.exe**, usually inside the R installation's `bin` folder. For RStudio, select **rstudio.exe**.
6. Choose **Check R version** to confirm that R can start.
7. Read the execution notice. Enable its acknowledgement if you want to use automatic checks, then choose **Save & return**.

Checking runs your saved R script with your Windows user's permissions. It is intended for code you knowingly choose to run. You can read lessons without enabling execution.

The official download destinations are [R for Windows](https://cran.r-project.org/bin/windows/base/) and [RStudio Desktop](https://posit.co/download/rstudio-desktop/). The Setup buttons open these in your browser.

## 3. Open your learning project

Choose **Open Project in RStudio**. The companion prepares a project called **StudentStudy**. In RStudio, confirm that StudentStudy is the active project, normally shown near the upper-right corner.

A project keeps related scripts, input data and outputs together. The companion creates your editable copy outside the application folder, under your Windows LocalAppData folder. Use **Project folder** to open it without having to find LocalAppData yourself.

Choose **Open Exercise File** to open the selected lesson's `.R` file. If that opens a different RStudio window, return to the StudentStudy project and use **File > Open File** there. The companion shows the exercise's relative path, such as `Scripts/02-variables.R`.

## 4. Follow a lesson

Select a lesson from the course list. There are four tabs:

| Tab | How to use it |
| --- | --- |
| Learn | Read the short concepts and try the guided actions in RStudio. |
| Practice & check | Complete the independent exercise, save your script, check it and confirm observations. Hints, solutions and common errors are farther down this tab. |
| Reflect | Explain the ideas in your own words. Your writing saves as you type. |
| References | Open the supporting official R and Posit documentation in your browser. |

A normal practice cycle is:

1. Read the Learn tab and follow its guided example.
2. Open your exercise in RStudio's **Source** editor. Source is the area for writing a script you can save.
3. Write your answer in that script. Select the relevant lines and press **Ctrl+Enter** to run them.
4. Inspect the results in RStudio's Console, Environment or Plots area, as the lesson requests.
5. Press **Ctrl+S** in RStudio to save the exercise.
6. Return to the companion and choose **Check My Work**.
7. Read the feedback, complete any observation checklist and answer the reflection questions.

Checking reads the file saved on disk. It cannot see unsaved edits or objects left over from an earlier RStudio Console session. Your exercise should contain everything needed to run by itself.

Use **Previous** and **Next lesson** to move through the course. You can revisit lessons freely; failed attempts do not lock navigation or hide solutions.

## 5. Understand feedback and completion

| Result | Meaning / next step |
| --- | --- |
| Not run | A check has not run, or R/the exercise file is unavailable. Check Setup and the displayed message. |
| Script ran; results need work | R could execute the script, but one or more expected values or files did not match. Read the individual feedback. |
| Execution failed | R could not complete the script, for example because of a syntax error, missing name or wrong path. Fix the first error in RStudio and save again. |
| Passed | Automatic checks passed. Complete any observation checklist too. |
| Self-confirmed | You confirmed an observation task. The app did not independently verify RStudio actions. |
| Cancelled / timed out | The run was stopped. Review the script and retry when ready. |

Automatic checks use real R and accept equivalent correct expressions. They cannot prove every technique, inspect your RStudio clicks, judge chart design or grade your written reasoning. Those parts use explicit observation checklists and reflections.

The orientation lesson uses **Confirm this practice** after you complete its checklist. A lesson's completion mark appears when its required check/confirmation and observation criteria are satisfied. Reflection text is for learning and is not automatically scored. A failed retry does not erase a prior successful check.

Each R run normally has a 20-second limit. Use **Cancel check** if you need to stop it. **Technical error details / process output** contains additional information for troubleshooting.

## 6. Use hints and solutions

In Practice & check, scroll to **A little help when you need it**:

- **Show next hint** reveals one hint at a time.
- **Reveal Example Solution** shows runnable example code and its explanation.
- **Common errors and recovery** lists mistakes to recognize and fix.

Solutions are always accessible and carry no penalty. A **Copy example** button copies code to the clipboard; paste it into RStudio to try it. The companion itself does not edit R scripts.

## 7. Find scripts, data and exports

Your normal working project has this layout:

```text
StudentStudy/
  StudentStudy.Rproj
  Scripts/       Your editable exercise scripts
  Solutions/     Example solution files
  Data/          CSV input files
  Outputs/       Tables and charts you export
  Backups/       Copies made before dataset restoration
```

Use **Project folder** to browse the project and **Outputs folder** to find exported results. Open a CSV, PNG or PDF after exporting it and check its actual contents.

In RStudio, type `getwd()` in Console to see the current working directory. For these lessons it should be the **StudentStudy project folder**, even when your script is inside Scripts. A relative path such as `Data/students.csv` starts from that working directory, not automatically from the script's folder. The companion's checker also starts at the project root.

The five-row `students.csv` is the simple introductory dataset. The separate twelve-row `students_extended.csv` includes intentional missing data and an input mistake for later exercises. These are fictional teaching datasets. Do not overwrite the small dataset with the extended one.

Export checks require your saved script to regenerate the expected file. An old file left in Outputs is not sufficient by itself. PNG/PDF checks do not judge appearance; open the actual chart and inspect labels, size and content yourself.

## 8. Save and back up your work

The companion automatically saves settings, progress and reflections under:

```text
%LOCALAPPDATA%\RLearningLab\
```

Your actual scripts still need to be saved in RStudio with **Ctrl+S**. The companion does not save unsaved RStudio tabs.

To make a manual backup, close the companion and save your RStudio work, then copy the entire `RLearningLab` folder from LocalAppData to a backup location. It contains both the progress files and the working project. Copying only the application folder or distribution ZIP does not back up your learner data.

Startup adds missing starter files and preserves existing edits. If you intentionally need a pristine dataset, open Setup & tools and choose the relevant **Restore ... dataset** button. The app asks for confirmation and backs up the current CSV in the project's Backups folder before replacing it with the shipped seed. Your scripts and saved progress remain intact.

## 9. Troubleshooting

| Problem | What to try |
| --- | --- |
| App cannot find its course | Keep Content next to RLearningLab.exe. If using a ZIP, extract the whole package. |
| R or RStudio not found | Open Setup, detect again or select the actual executable. Saving a path does not install the tool. |
| My correct answer still fails | Save with Ctrl+S, confirm you edited the displayed exercise file, then rerun the whole script. |
| Object not found | Check spelling and capitalization. Add the assignment to the saved script before its use. |
| Cannot open a CSV or output file | Check `getwd()` and `file.exists('Data/students.csv')`. Reopen StudentStudy.Rproj if the working directory is wrong. Ensure Outputs exists before exporting. |
| Wrong RStudio window opens | Open StudentStudy.Rproj, then open the script through File > Open File inside that session. |
| Check takes too long | Cancel it and inspect for a loop, long operation or command waiting for input. The normal limit is 20 seconds. |
| Chart passes but looks wrong | Open it and use the lesson's observation checklist. Automatic signature checks do not assess its design. |
| Save warning appears | Keep the companion open, check available storage and folder access, and retry saving before closing. |

## 10. More information

- [README.md](README.md): technical overview, build commands, preservation behavior and manual checks.
- [REFERENCES.md](REFERENCES.md): official documentation mapped to each lesson. External references require internet; the lesson text and exercises are included offline.
- [TESTING.md](TESTING.md): what was actually tested and what remains unverified. Real RStudio launch/session behavior still needs a manual check on a machine with RStudio installed.
- [HANDOFF.md](HANDOFF.md): developer context for maintaining or extending the project.

This release does not include a progress import/export wizard, workspace relocation, an installer, optional Excel/ggplot2 lessons or bundled RStudio screenshots. These are future enhancements; the shipped Base R course covers all 15 planned modules.
