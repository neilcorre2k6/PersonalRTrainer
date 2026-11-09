"""Authoring source for the shipped curriculum. Python 3, standard library only.
Run from any directory. Rewrites shipped CONTENT, never a learner workspace.
The app consumes Content/curriculum.json and does not require Python.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "Content"
WORKSPACE = CONTENT / "Workspace"
MODULES = ["Meet RStudio", "R as a calculator", "Variables", "Data types", "Vectors and functions", "Data frames", "Files and paths", "Importing data", "Manipulating data", "Summaries", "Exporting tables", "Building plots", "Customizing plots", "Exporting plots", "Your final project"]
BASE = "https://stat.ethz.ch/R-manual/R-devel/library/"
REFS = {
    "orientation": ("Posit: Get started (includes pane screenshots)", "https://docs.posit.co/ide/user/ide/get-started/"),
    "panes": ("Posit: Pane layout and screenshots", "https://docs.posit.co/ide/user/ide/guide/ui/ui-panes.html"),
    "execution": ("Posit: Executing code", "https://docs.posit.co/ide/user/ide/guide/code/execution.html"),
    "shortcuts": ("Posit: Keyboard shortcuts", "https://docs.posit.co/ide/user/ide/reference/shortcuts.html"),
    "projects": ("Posit: RStudio Projects", "https://docs.posit.co/ide/user/ide/guide/code/projects.html"),
    "paths": ("Posit: Working directories and workspaces", "https://support.posit.co/hc/en-us/articles/200711843-Working-Directories-and-Workspaces-in-the-RStudio-IDE"),
    "imports": ("Posit: Local data and import wizard", "https://docs.posit.co/ide/user/ide/guide/data/data-local.html"),
}
for key, package, page, title in [
    ("arithmetic","base","Arithmetic","Arithmetic operators"), ("assignment","base","assignOps","Assignment"), ("function","base","function","Function definitions"),
    ("types","base","typeof","Object types"), ("class","base","class","Object classes"),
    ("na","base","NA","Missing values"), ("comparison","base","Comparison","Comparisons"),
    ("vectors","base","c","Combining values"), ("extract","base","Extract","Selecting and replacing values"),
    ("length","base","length","Length"), ("sum","base","sum","Sum"), ("mean","base","mean","Mean"),
    ("frames","base","data.frame","Data frames"), ("getwd","base","getwd","Working directory"),
    ("files","base","list.files","Listing files"), ("source","base","source","Running a saved script"),
    ("read","utils","read.table","CSV input"), ("write","utils","write.table","CSV output"),
    ("order","base","order","Sorting"), ("median","stats","median","Median"),
    ("aggregate","stats","aggregate","Grouped summaries"), ("table","base","table","Counts"),
    ("plot","graphics","plot.default","Scatter and line plots"), ("bar","graphics","barplot","Bar charts"),
    ("hist","graphics","hist","Histograms"), ("legend","graphics","legend","Legends"),
    ("png","grDevices","png","PNG graphics device"), ("pdf","grDevices","pdf","PDF graphics device"),
    ("devices","grDevices","dev","Closing graphics devices"),
]:
    REFS[key] = ("R documentation: " + title, BASE + package + "/html/" + page + ".html")

LESSONS = []
def rule(kind, name, expected, description, help_text="Review the named result, rerun your script and save it.", **kwargs):
    return dict(kind=kind, name=name, expected=expected, description=description, help=help_text, **kwargs)
def num(name, value): return rule("numeric", name, value, f"{name} equals {value}")
def val(name, value): return rule("value", name, value, f"{name} has the requested value")
def vec(name, value): return rule("vector", name, value, f"{name} contains the requested values in order")
def rows(name, n): return rule("rows", name, n, f"{name} is a data frame with {n} rows")
def cols(name, values): return rule("columns", name, values, f"{name} contains columns: {', '.join(values)}")
def column(name, field, values): return rule("columnValues", name, values, f"{name}${field} contains the requested values", column=field)
def export(kind, path, expected=None, name=""):
    return rule(kind, name, expected, f"Create a fresh, valid {kind.upper()} at {path}", "Include the export command in this saved script. Check the filename and close image devices with dev.off().", path=path)

def lesson(module, slug, title, summary, objectives, concepts, guided, code, tasks, observation, hints, reflections, errors, solution, explanation, refs, checks=(), self_checks=(), minutes=20):
    ident = f"{module:02}-{slug}"
    starter = f"Scripts/{ident}.R"
    answer = f"Solutions/{ident}.R"
    item = dict(id=ident, module=module, moduleTitle=MODULES[module], title=title, summary=summary,
                estimatedMinutes=minutes, objectives=objectives,
                concepts=[dict(heading=h, text=t) for h,t in concepts], guidedSteps=guided, guidedCode=code,
                tasks=tasks, expectedObservation=observation, hints=hints, reflections=reflections,
                commonErrors=errors, solutionExplanation=explanation, starterScript=starter,
                solutionScript=answer, validation=list(checks), selfChecks=list(self_checks),
                references=[dict(title=REFS[r][0], url=REFS[r][1]) for r in refs])
    LESSONS.append(item)
    for folder in ["Scripts", "Solutions", "Data", "Outputs"]: (WORKSPACE / folder).mkdir(parents=True, exist_ok=True)
    # Starters intentionally contain prompts, not solved exercises.
    text = f"# {title}\n# Open StudentStudy.Rproj first. Write your answer below in RStudio.\n# Select your code, Ctrl+Enter to run. Ctrl+S to save before checking.\n# This script must run by itself in a fresh R session.\n\n"
    text += "\n".join("# " + str(i+1) + ". " + t for i,t in enumerate(tasks)) + "\n\n"
    (WORKSPACE / starter).write_text(text, encoding="utf-8")
    (WORKSPACE / answer).write_text(f"# Example solution: {title}\n# One valid approach; equivalent results are accepted.\n\n" + solution.strip() + "\n", encoding="utf-8")

lesson(0,"welcome","Find your way around RStudio",
    "Meet the tools, open your project, and locate the places you will use.",
    ["Explain the roles of R, RStudio and this guide.", "Find Source, Console, Environment, Files, Plots and Help."],
    [("Three tools, one workflow", "R is the language that calculates. RStudio is the application where you write and run R. R Learning Lab gives you practice and feedback. A project is a folder of related work plus an .Rproj file that tells RStudio which folder to use."),
     ("A map of the window", "In the usual layout, Source is upper left, Console lower left, Environment upper right, and Files / Plots / Help lower right. Layouts can differ. Source may appear only after you open a script. Console executes commands; Environment lists temporary objects. Files shows disk files; Plots displays charts; Help explains functions. Use the official pane screenshots linked below to compare with your window.")],
    ["Use Setup to check R and RStudio. Install both if needed; they are separate programs.", "Choose Open Project in RStudio. Check StudentStudy appears in RStudio's project selector.", "In RStudio choose File > Open File, then Scripts/00-welcome.R inside this project. This reveals Source if it was hidden.", "Click the Console after its > prompt, type 2 + 2, and press Enter.", "Find Environment and the Files, Plots and Help tabs. In Help, search for mean. You do not need a plot yet."],
    "2 + 2\n?mean",
    ["Reopen StudentStudy.Rproj using RStudio's File > Open Project menu.", "Identify the six areas named above. Tell yourself which area stores code and which runs it.", "Run 2 + 2 in Console. Visit Files and Help. Confirm the observations below."],
    "The Console prints 4 (often preceded by [1], a result-position label). Opening a script reveals Source. This lesson uses your confirmation because the app does not monitor RStudio clicks.",
    ["An .Rproj file opens a project; an .R file opens a script.", "If Source is absent, use File > New File > R Script.", "The project selector is normally near the upper-right corner."],
    ["What is the difference between R and RStudio?", "Where would you write a script you want to keep?"],
    ["Typing in this guide: switch to RStudio first.", "Typing the > prompt as part of your command: enter only 2 + 2.", "A different pane layout is not an error; use the tab names."],
    "# Console practice: type the following in the RStudio Console.\n2 + 2\n?mean",
    "The Console evaluates 2 + 2 immediately. Source holds a script you can save. The Environment is temporary memory; Files describes disk storage. You can rearrange panes without changing R itself.",
    ["orientation","panes","projects"], self_checks=["StudentStudy is the open RStudio Project.", "I can point to Source, Console, Environment, Files, Plots and Help.", "I ran 2 + 2 in Console and saw 4."], minutes=15)

lesson(0,"scripts","Save, reopen and recover from a typo",
    "Keep your work in a script and make errors feel manageable.",
    ["Create, save and reopen an R script.", "Run selected code and distinguish saved code from session memory."],
    [("A script is a recipe", "A script is a text file of R instructions ending in .R. Text after # on a line is a comment for people. Saving preserves the recipe, not necessarily the objects currently in memory. A saved script can recreate those objects when you run it."),
     ("Read the first error", "R is case-sensitive: greeting and Greeting are different names. An error is feedback about the command R could not complete. Fix the first error, then rerun the relevant lines. A Console + prompt usually means an unfinished expression; press Escape and check your quotes or brackets.")],
    ["Open the exercise file in RStudio Source. Add a comment describing your practice.", "Type note <- 'Hello R', select that line, and press Ctrl+Enter. Inspect Environment.", "On a new line type print(Note) and run it. Read the name in the error, then change Note to note and rerun.", "Press Ctrl+S. Close the script tab and reopen it using File > Open File.", "Choose Session > Restart R. The saved text remains; run it again to recreate note. Do not save or restore .RData for this course."],
    "# My first saved script\nnote <- 'Hello R'\nprint(note)",
    ["In the exercise script create greeting containing the exact text Hello RStudio.", "Print greeting. Add a comment explaining what the script does.", "Run the script, save it, close and reopen the tab. Check the saved script here."],
    "The script prints Hello RStudio. Restarting R clears session objects; running the saved script recreates greeting.",
    ["Put text inside matching straight quotes.", "Use greeting <- 'Hello RStudio'.", "Save with Ctrl+S before Check My Work."],
    ["What survives when you save a script?", "How did you identify and fix the typo?"],
    ["Object not found: check capital letters and run the assignment first.", "A + prompt: press Escape, then check for an unclosed quote.", "Checking unsaved edits: the checker reads only the file on disk."],
    "# Create a greeting, then display it.\ngreeting <- 'Hello RStudio'\nprint(greeting)",
    "The assignment stores the text in greeting, and print displays it. The comment explains intent without running. Reopening a script demonstrates persistence on disk; rerunning after a restart demonstrates how code recreates memory.",
    ["execution","shortcuts","assignment"], checks=[val("greeting","Hello RStudio")], self_checks=["I saved, closed and reopened this .R script.", "I deliberately made a typo, read its error, and fixed it."], minutes=20)

lesson(1,"calculator","Calculate and predict",
    "Use R for arithmetic and make the order of calculation explicit.",
    ["Use +, -, *, / and ^.", "Predict how parentheses change a calculation."],
    [("Expressions produce values", "An expression is a calculation R can evaluate. Use * for multiplication, / for division and ^ for powers. Parentheses group a calculation. Multiplication happens before addition unless parentheses change the order. A printed [1] is an output-position label, not part of the answer.")],
    ["In RStudio Console run 3 + 4 * 2. Predict first.", "Run (3 + 4) * 2 and compare.", "Run 12 / 4, 2 ^ 3 and 10 - 7 on separate lines.", "Open the exercise script in Source. Use the assignment examples to keep your answers under the requested names.", "Run all your exercise lines with Ctrl+Enter, inspect the answers and save."],
    "3 + 4 * 2\n(3 + 4) * 2\n12 / 4\n2 ^ 3\nanswer <- 9 + 1\nprint(answer)",
    ["Create ungrouped from 2 + 3 * 4.", "Create grouped from (2 + 3) * 4.", "Create power from 2 ^ 5, and share from 20 / 4. Print each answer and save."],
    "ungrouped is 14, grouped is 20, power is 32 and share is 5.",
    ["Use name <- calculation to keep an answer.", "Use parentheses around the addition for grouped.", "Do not use x as a multiplication sign."],
    ["Why do the first two answers differ?", "When would adding parentheses make your code easier to read?"],
    ["2(3 + 4) is not ordinary multiplication syntax; use 2 * (3 + 4).", "A decimal uses a dot: 2.5, not 2,5.", "R may print a long result in scientific notation; it is still a number."],
    "ungrouped <- 2 + 3 * 4\ngrouped <- (2 + 3) * 4\npower <- 2 ^ 5\nshare <- 20 / 4\nprint(c(ungrouped, grouped, power, share))",
    "Multiplication is evaluated before addition, giving 14. Grouping the addition gives 20. Exponentiation produces 32, and division produces 5. Names let later checks inspect the values; equivalent valid expressions are accepted.",
    ["arithmetic"], checks=[num("ungrouped",14),num("grouped",20),num("power",32),num("share",5)])

lesson(2,"variables","Calculate a total",
    "Name values and use them to calculate another value.",
    ["Assign and overwrite values.", "Explain why a calculated value does not update itself."],
    [("Names for stored values", "The arrow <- assigns the result on its right to the name on its left. Read price <- 8 as 'store 8 as price'. Choose names that explain the value; avoid spaces and names starting with digits. A later assignment to the same name replaces its current value."),
     ("A result is not a live spreadsheet formula", "When total <- price * quantity runs, R calculates with the values available at that moment. Changing quantity later does not recalculate total. Run the total assignment again when you want a new result.")],
    ["In Source type the example below and run it.", "Inspect price, quantity and total in Environment.", "Change quantity to 4 and run only that assignment. Print total: it still has the old value.", "Run total <- price * quantity again, then print it.", "For the independent task, use the values requested below, run the entire script in order and save."],
    "price <- 8\nquantity <- 2\ntotal <- price * quantity\nprint(total)",
    ["Create price with value 10 and quantity with value 3.", "Calculate total using those two variables; inspect the result in Environment.", "Print total and save. For the final check leave quantity at 3."],
    "The saved script creates price = 10, quantity = 3 and total = 30. Value checks confirm results; the reflection asks you to explain how you produced them.",
    ["Create input variables before calculating the output.", "Multiplication uses *: total <- price * quantity.", "If you experimented with quantity = 5, restore 3 and rerun the total calculation."],
    ["What does <- do?", "If quantity changes to 5, why does total stay the same until you recalculate it?"],
    ["Using a name before assigning it produces object not found.", "Price and price are different names.", "An old value in Environment can hide a missing script line. Restart R and run the whole script."],
    "price <- 10\nquantity <- 3\ntotal <- price * quantity\nprint(total)",
    "The two inputs are assigned first. The multiplication then stores 30 in total. Assignment evaluates a calculation once; it does not establish an automatically updating relationship.",
    ["assignment","arithmetic"], checks=[num("price",10),num("quantity",3),num("total",30)])

lesson(3,"types","Numbers, text and logical values",
    "Recognize the kind of value you are working with.",
    ["Create numeric, character and logical objects.", "Use class() and typeof() to inspect objects."],
    [("Different values support different operations", "A number such as 12 can be used in arithmetic. Quoted text such as '12' is character data. TRUE and FALSE are logical values, useful for yes/no decisions. typeof() describes storage; class() describes the object's class. Ordinary numbers such as 12 are usually stored as double; 12L is an integer."),
     ("Compare values", "Use == to ask whether two values are equal, and > or >= to compare their size. These comparisons return logical values. Use <- to store a value. Text needs straight quotes; logical constants TRUE and FALSE do not.")],
    ["Run the example in Source and inspect the printed types.", "In Console try '12' + 1. Read the error; then try 12 + 1.", "Run 12 >= 10 and 12 == 10. Explain each logical answer.", "In your exercise script create the requested objects and inspect them.", "Run the saved script independently before checking."],
    "count <- 12\nlabel <- '12'\nready <- TRUE\nclass(count)\ntypeof(count)\ntypeof(label)\ntypeof(ready)\ncount >= 10",
    ["Create hours as the number 4, student_name as the text Anna, and passed as TRUE.", "Create above_three by comparing hours > 3.", "Inspect all four objects with typeof(), run your script and save."],
    "hours is numeric, student_name is character, and passed and above_three are logical TRUE.",
    ["Write 4 without quotes for hours.", "Write 'Anna' with quotes for student_name.", "above_three <- hours > 3 stores the comparison result."],
    ["How do 4 and '4' differ?", "What is the difference between <- and ==?"],
    ["Adding to text causes a non-numeric argument error; inspect the type first.", "Use TRUE rather than the text 'TRUE'.", "Do not replace a comparison with an assignment."],
    "hours <- 4\nstudent_name <- 'Anna'\npassed <- TRUE\nabove_three <- hours > 3\nprint(c(typeof(hours), typeof(student_name), typeof(passed)))",
    "Quotes make Anna character data. The number 4 can be compared with 3; the result is a logical TRUE. typeof(hours) is normally double, which is one numeric storage type.",
    ["types","class","comparison"], checks=[num("hours",4),val("student_name","Anna"),val("passed",True),val("above_three",True),rule("type","student_name","character","student_name is character data")])

lesson(3,"missing","Work honestly with missing values",
    "Find missing observations without treating them as zero.",
    ["Recognize NA and use is.na().", "Calculate a mean while making missing-value handling explicit."],
    [("Missing is not zero", "NA marks an unavailable value. It differs from 0 and from the text 'NA'. Arithmetic involving missing values often produces NA. Use is.na(x), not x == NA, to identify them. Removing missing values from a summary changes which observations contribute, so report the missing count."),
     ("Arguments change a function's behavior", "A function is a named operation called with parentheses. In mean(x, na.rm = TRUE), x supplies the data and the named argument na.rm requests removal of missing values for that calculation. It does not fill in or change the original data.")],
    ["Run the guided vector in Source, then print mean(scores).", "Run is.na(scores) and count the TRUE values with sum().", "Run mean(scores, na.rm = TRUE) and compare.", "Try scores == NA in Console. Notice that it does not identify missing positions.", "Write the independent script, run and save it."],
    "scores <- c(60, NA, 80)\nis.na(scores)\nsum(is.na(scores))\nmean(scores)\nmean(scores, na.rm = TRUE)",
    ["Create scores as c(65, NA, 85, 90).", "Create missing_count by counting its missing values.", "Create average_score as the mean of the known values. Keep NA in scores; do not replace it with zero."],
    "missing_count is 1; average_score is 80. scores still has four entries, including one missing entry.",
    ["is.na(scores) produces one logical value per entry.", "sum(is.na(scores)) counts missing entries.", "Use mean(scores, na.rm = TRUE)."],
    ["Why would replacing a missing score with zero change the story?", "How many observations contribute to average_score?"],
    ["mean returns NA by default when data contain NA.", "'NA' is text, while NA is a missing-value marker.", "na.rm removes values from a calculation, not from the stored vector."],
    "scores <- c(65, NA, 85, 90)\nmissing_count <- sum(is.na(scores))\naverage_score <- mean(scores, na.rm = TRUE)\nprint(average_score)",
    "One entry is missing. The three known scores sum to 240, so their mean is 80. The original vector is preserved and the missing count records the limitation.",
    ["na","mean","sum","vectors"], checks=[num("missing_count",1),num("average_score",80),vec("scores",[65,None,85,90])], self_checks=["I verified that scores still contains NA rather than zero."])

lesson(4,"vectors","Keep several values together",
    "Create a vector, select entries and summarize it.",
    ["Use c() and positions starting at 1.", "Call length(), sum() and mean()."],
    [("An ordered collection", "A vector keeps values in order. c(2, 4, 6) combines three values. Positions start at 1: x[1] selects the first entry, and x[c(1, 3)] selects the first and third. A simple atomic vector has one common type; combining numbers with text converts the numbers to text."),
     ("Functions take inputs", "In sum(hours), hours is the input. length() counts entries, sum() adds values, and mean() calculates their average. You can combine function calls, but separate named steps are often easier to understand. No loop is needed here.")],
    ["Run practice <- c(1, 3, 5) in Source.", "Run practice[1] and practice[c(1, 3)]. Predict each answer first.", "Run length(practice), sum(practice) and mean(practice).", "Try c(1, 'two') in Console and inspect typeof() of the result.", "Complete your script, run all lines and save."],
    "practice <- c(1, 3, 5)\npractice[1]\npractice[c(1, 3)]\nlength(practice)\nsum(practice)\nmean(practice)",
    ["Create hours as c(2, 4, 5, 1, 3).", "Create first_hours from its first entry and selected_hours from positions 2 and 5.", "Create student_count, total_hours and mean_hours using the appropriate functions."],
    "first_hours is 2; selected_hours is c(4, 3); there are 5 entries totaling 15, with mean 3.",
    ["Use square brackets for positions and parentheses for function calls.", "selected_hours <- hours[c(2, 5)].", "mean_hours <- mean(hours)."],
    ["What does hours[0] return, and why is it not the first entry?", "What might happen if you mix a number and a word in one vector?"],
    ["hours(1) tries to call a function; use hours[1].", "A selected index beyond the vector length can give NA.", "length() counts entries, not their total."],
    "hours <- c(2, 4, 5, 1, 3)\nfirst_hours <- hours[1]\nselected_hours <- hours[c(2, 5)]\nstudent_count <- length(hours)\ntotal_hours <- sum(hours)\nmean_hours <- mean(hours)",
    "Indexing retrieves values at particular positions. Summary functions operate on the whole vector: length is 5, sum is 15 and mean is 3. These operations avoid repeating the same calculation by hand.",
    ["vectors","extract","length","sum","mean"], checks=[vec("hours",[2,4,5,1,3]),num("first_hours",2),vec("selected_hours",[4,3]),num("student_count",5),num("total_hours",15),num("mean_hours",3)])

lesson(4,"functions","Build a small reusable function",
    "Give a repeated calculation a clear name.",
    ["Recognize arguments and returned values.", "Write and call a small function without loops."],
    [("A named recipe", "Built-in functions such as mean already contain instructions. You can name a small recipe with function(). The names inside its parentheses are arguments. The last evaluated expression is returned. For this optional extension, treat the body between braces as a short sequence of calculations.")],
    ["In Source run the guided function definition.", "Call add_bonus(60) and add_bonus(80). The same recipe uses different inputs.", "Change the bonus in the function body and rerun the definition before calling it again.", "Use ?function in Console for the language help, or revisit the simpler built-in function examples.", "Define the requested function in the exercise script; run and save."],
    "add_bonus <- function(score) {\n  score + 5\n}\nadd_bonus(60)\nadd_bonus(80)",
    ["Define double_hours as a function taking x and returning x * 2.", "Create doubled by calling double_hours(c(1, 3, 5)).", "Print doubled and save the function definition and call together."],
    "doubled is c(2, 6, 10). The same multiplication works for each numeric vector entry.",
    ["Start double_hours <- function(x) { ... }.", "Put x * 2 inside the braces.", "Call the function after defining it."],
    ["How is defining a function different from calling it?", "Why should the definition be saved alongside its use?"],
    ["A function definition alone does not call the function.", "Missing closing braces leave an unfinished expression.", "A previous Console definition will not exist in a clean checking process."],
    "double_hours <- function(x) {\n  x * 2\n}\ndoubled <- double_hours(c(1, 3, 5))\nprint(doubled)",
    "The function applies multiplication to its argument. Calling it with a vector returns a vector of doubled values. This extension is useful practice; the core course needs only simple built-in functions.",
    ["function","arithmetic"], checks=[vec("doubled",[2,6,10])], self_checks=["I defined double_hours using function() and called it with an argument."], minutes=15)

lesson(5,"tables","Meet a data frame",
    "Arrange related vectors as a table of students.",
    ["Distinguish rows, columns and individual values.", "Inspect a data frame without changing it."],
    [("One row per student", "A data frame is a table whose columns can have different types. Each column has the same number of rows. In our study table a row describes one fictional student, and a column describes one attribute. data.frame() combines named columns; $ selects a column by name."),
     ("Inspect before calculating", "head() shows the first rows, names() shows column names, and str() gives a compact structural description. View() opens RStudio's table viewer; its capital V matters. Keep View() as an interactive Console command so a headless checker does not need a display.")],
    ["Run the guided table definition in Source.", "Run head(practice), str(practice) and names(practice).", "In Console run View(practice). Return to your script tab afterward.", "Run practice$hours and practice[1, ]. The comma separates row and column positions.", "Create the independent table in the exercise script, inspect it, run and save."],
    "practice <- data.frame(student = c('Ira', 'Jo'), hours = c(1, 2))\nhead(practice)\nstr(practice)\npractice$hours\npractice[1, ]",
    ["Create students with student names Anna, Ben and Clara, study_hours 2, 4 and 5, and exam_score 65, 78 and 88.", "Create scores by selecting students$exam_score.", "Create first_student by selecting the first row while keeping all columns."],
    "students has 3 rows and 3 named columns; scores contains c(65, 78, 88), and first_student is a one-row table for Anna.",
    ["Use data.frame(student = c(...), study_hours = c(...), exam_score = c(...)).", "All three columns need three entries.", "first_student <- students[1, ] keeps the first row."],
    ["What does one row represent?", "How does students$exam_score differ from students[1, ]?"],
    ["Columns of incompatible lengths cannot describe a rectangular table.", "view() and View() are different names.", "A missing comma in row selection changes what [] selects."],
    "students <- data.frame(student=c('Anna','Ben','Clara'), study_hours=c(2,4,5), exam_score=c(65,78,88))\nscores <- students$exam_score\nfirst_student <- students[1, ]\nhead(students)\nstr(students)",
    "Each vector becomes a column, and matching positions describe the same student. $ selects a whole column; [1, ] selects a row. View is for inspection in RStudio, not for proving an answer automatically.",
    ["frames","extract"], checks=[rows("students",3),cols("students",["student","study_hours","exam_score"]),column("students","student",["Anna","Ben","Clara"]),column("students","study_hours",[2,4,5]),vec("scores",[65,78,88]),rows("first_student",1),column("first_student","student",["Anna"])])

lesson(6,"paths","Find your project root",
    "Understand exactly where R looks for a relative path.",
    ["Inspect getwd() and list.files().", "Distinguish a script's folder from the working directory."],
    [("The folder R starts from", "A path is directions to a file. An absolute path identifies a complete location, for example C:/Users/Alex/Documents/data.csv. A relative path starts from the current R working directory, which getwd() reports. Opening StudentStudy.Rproj normally sets that directory to StudentStudy. Saving a script under Scripts does not make paths start from Scripts."),
     ("Read the folder tree", "StudentStudy contains Scripts, Data and Outputs. Data/students.csv therefore means: start at the working directory, enter Data, then find students.csv. list.files() lists entries at a location. file.exists() asks whether a path can be found. Browsing the Files pane alone does not necessarily change getwd().")],
    ["Open StudentStudy.Rproj and run getwd() in Console. Compare it with Open Project Folder in this guide.", "Run list.files() and list.files('Data'). Find students.csv.", "Run file.exists('Data/students.csv'), then file.exists('students.csv'). Explain the difference.", "Open the script under Scripts and run getwd() again: note that it is still the project root.", "Complete the exercise in Source and save."],
    "getwd()\nlist.files()\nlist.files('Data')\nfile.exists('Data/students.csv')\nfile.exists('students.csv')",
    ["Create data_found by checking file.exists('Data/students.csv').", "Create root_file_found by checking file.exists('students.csv'). Do not move or duplicate the CSV into the root.", "Create data_files from list.files('Data'). Inspect your working directory and save."],
    "data_found is TRUE, root_file_found is FALSE, and Data lists the two shipped CSV fixtures. Checks run with the same project root.",
    ["Reopen the .Rproj if getwd() ends with Scripts or Data.", "Use project-relative Data/students.csv.", "Create data_files <- list.files('Data')."],
    ["Why is Data/students.csv correct even though the script is inside Scripts?", "How would you diagnose cannot open file before changing code?"],
    ["students.csv alone looks in the root, not recursively inside Data.", "A hardcoded setwd() can make your script work only on your machine.", "Do not confuse the folder displayed in Files with the R working directory."],
    "print(getwd())\nprint(list.files())\ndata_found <- file.exists('Data/students.csv')\nroot_file_found <- file.exists('students.csv')\ndata_files <- list.files('Data')",
    "Relative paths are resolved from getwd(). Both RStudio and the checker should start in StudentStudy, so the Data prefix is required. The CSV remains in its intended folder.",
    ["getwd","files","paths","projects"], checks=[val("data_found",True),val("root_file_found",False)], self_checks=["getwd() reports the StudentStudy project root.", "I inspected data_files and found students.csv."])

lesson(6,"relative","Use dot, parent folders and source",
    "Navigate paths deliberately and recover from a missing-file error.",
    ["Explain . and .. in paths.", "Run a helper script and recover from a wrong path."],
    [("Current and parent folders", "A dot means the current directory; two dots mean its parent. From the project root, ./Data/students.csv is the same file as Data/students.csv. Scripts/../Data/students.csv enters Scripts, returns to its parent, then enters Data. Prefer short, clear paths in saved scripts."),
     ("Windows paths and reusable scripts", "R accepts forward slashes on Windows. A literal backslash inside an R string must be escaped, as in 'C:\\\\Data\\\\file.csv'. source('Scripts/helpers.R') runs saved code; by default it does not move the working directory to the helper's folder. setwd() changes the current directory, but hardcoded paths make shared scripts fragile.")],
    ["In Console compare normalizePath('.') and normalizePath('..'). Do not move or delete folders.", "Run file.exists('./Data/students.csv') and file.exists('Scripts/../Data/students.csv').", "Try read.csv('Data/missing.csv') in Console, read the error, then use the correct filename.", "In Console save old_dir <- getwd(); run setwd('Data'), then getwd(). Restore immediately with setwd(old_dir), or reopen the project.", "Inspect Scripts/helpers.R using File > Open File. Run the guided source call and then complete the exercise."],
    "file.exists('./Data/students.csv')\nfile.exists('Scripts/../Data/students.csv')\nsource('Scripts/helpers.R', local = TRUE)\ncourse_label",
    ["Create same_file using file.exists('./Data/students.csv').", "Create via_parent using file.exists('Scripts/../Data/students.csv').", "Run source('Scripts/helpers.R', local = TRUE) so course_label becomes available in the current script environment. Print it. Save without a hardcoded setwd()."],
    "Both path checks are TRUE. The helper creates course_label with the text Fictional student study. The checker still uses the project root.",
    [". means here and .. means parent.", "Use forward slashes and matching quotes.", "The local = TRUE argument makes source evaluate in the caller's environment, including the checking environment."],
    ["Why can changing getwd() break a previously correct relative path?", "What makes a project-relative script easier to move to another computer?"],
    ["A single backslash can start an escape sequence in an R string.", "Do not leave the deliberate missing-file command in your submitted script.", "A helper loaded only in the Console is missing from a clean script run."],
    "same_file <- file.exists('./Data/students.csv')\nvia_parent <- file.exists('Scripts/../Data/students.csv')\nsource('Scripts/helpers.R', local = TRUE)\nprint(course_label)",
    "Both relative routes reach the same CSV from the project root. source executes the helper in the current environment when local = TRUE. No machine-specific directory is needed.",
    ["getwd","source","files"], checks=[val("same_file",True),val("via_parent",True),val("course_label","Fictional student study")], self_checks=["I deliberately caused a wrong-path error in Console and recovered.", "After trying setwd(), I restored the project root."])

lesson(7,"csv","Import CSV through the UI and code",
    "Bring the fictional study table into R and inspect its contents.",
    ["Use RStudio's base text importer.", "Save a reproducible read.csv() call."],
    [("A CSV is a disk file", "CSV stands for comma-separated values. The first row often contains column names; each later row contains an observation. Our file uses commas and decimal dots. read.csv() reads it into a data frame. Having a CSV in Files is different from having a students object in Environment."),
     ("Two ways to import", "RStudio's Import Dataset wizard previews a file and executes generated code. For this course choose From Text (base) when available, avoiding extra packages. A readr importer may offer to install readr. The saved script should use base read.csv() so a fresh R session can reproduce the import.")],
    ["In RStudio's Environment pane choose Import Dataset > From Text (base). Use the folder button to select Data/students.csv inside StudentStudy.", "Inspect the preview: enable a header, choose comma as separator and name the imported object students_ui. Press Import.", "Inspect students_ui in Environment and its table tab. Compare the generated Console command with read.csv().", "In Source run the guided code below, then head(students) and str(students).", "Save a project-relative import in the exercise script; do not rely on the wizard's previous session object."],
    "students <- read.csv('Data/students.csv')\nhead(students)\nstr(students)\nnames(students)",
    ["Import Data/students.csv into students using read.csv().", "Create imported_rows using nrow(students).", "Create imported_names using names(students). Inspect types and the first row, then save."],
    "The table has 5 rows and columns student, study_hours, exam_score and coffee_cups. Anna's study_hours is 2 and exam_score is 65.",
    ["The path starts from StudentStudy, not Scripts.", "Use students <- read.csv('Data/students.csv').", "Use nrow() for rows; length(data_frame) counts columns."],
    ["How can you tell the data were actually imported into R?", "Why save the import command after using the wizard?"],
    ["A semicolon separator applied to this fixture makes one combined column.", "Cannot open file: check getwd() and file.exists() first.", "The UI-imported object does not automatically become part of your saved script."],
    "students <- read.csv('Data/students.csv')\nimported_rows <- nrow(students)\nimported_names <- names(students)\nhead(students)\nstr(students)",
    "The wizard helps inspect import settings. The saved read.csv call makes those data available again in a clean process. Row and column checks catch common delimiter or header mistakes.",
    ["imports","read","frames"], checks=[rows("students",5),cols("students",["student","study_hours","exam_score","coffee_cups"]),column("students","exam_score",[65,78,88,55,72]),num("imported_rows",5),vec("imported_names",["student","study_hours","exam_score","coffee_cups"])], self_checks=["I used the RStudio import wizard and compared its output with the saved code."])

lesson(7,"inspect","Inspect a larger, imperfect dataset",
    "Keep raw data intact and identify quality issues before analysis.",
    ["Inspect column types, categories and missing values.", "Distinguish missing entries from a deliberate input mistake."],
    [("Keep a stable starting point", "Data/students.csv stays a five-row fixture for early lessons. Data/students_extended.csv is a separate, deterministic twelve-row version with a group column, one missing study_hours value and an impossible exam_score of 880. Keeping separate files prevents later lessons from invalidating earlier ones."),
     ("Ask what values mean", "str(), head(), summary() and table() help inspect an import. A score over 100 is a data-quality flag in this fictional exercise, not automatically proof of how to correct it. Here the teaching notes explicitly tell you 880 is a typing error for 88. Real analysis needs evidence before corrections. Excel import is optional later; CSV requires no extra packages.")],
    ["Run the guided import in Source, then inspect head(raw_students) and str(raw_students).", "Use summary(raw_students) to notice the unusual exam-score range.", "Count is.na(raw_students$study_hours) and table(raw_students$group).", "In RStudio Console open View(raw_students), locate Clara's 880 and Hugo's missing hours. Do not edit the raw CSV.", "Complete the inspection exercise and save."],
    "raw_students <- read.csv('Data/students_extended.csv', na.strings=c('', 'NA'))\nstr(raw_students)\nsummary(raw_students)\ntable(raw_students$group)\nsum(is.na(raw_students$study_hours))",
    ["Import the extended CSV into raw_students, treating blank cells and NA as missing.", "Create missing_hours as the number of missing study_hours entries.", "Create impossible_scores as the number of exam_score values above 100, and groups as the sorted unique group labels."],
    "There are 12 students, one missing study_hours entry, one score above 100 and two groups: A and B.",
    ["Use na.strings = c('', 'NA') in read.csv().", "sum(is.na(raw_students$study_hours)) counts missing hours.", "groups <- sort(unique(raw_students$group))."],
    ["What evidence would you need before correcting an unexpected real-world value?", "Why keep the raw file and cleaned data separate?"],
    ["An empty cell is not the same observation as zero hours.", "summary() is a diagnostic overview, not automatic data cleaning.", "Changing the five-row CSV would break the assumptions of earlier practice."],
    "raw_students <- read.csv('Data/students_extended.csv', na.strings=c('', 'NA'))\nmissing_hours <- sum(is.na(raw_students$study_hours))\nimpossible_scores <- sum(raw_students$exam_score > 100, na.rm=TRUE)\ngroups <- sort(unique(raw_students$group))",
    "Explicit missing-value handling preserves the unknown hours. Comparison flags the known bad score without silently correcting it. The raw import remains available for comparison with later cleaning.",
    ["read","na","table"], checks=[rows("raw_students",12),num("missing_hours",1),num("impossible_scores",1),vec("groups",["A","B"])])

lesson(8,"filter","Select, filter and sort",
    "Make smaller tables without losing the relationship between columns.",
    ["Select columns and filter rows with logical conditions.", "Sort whole rows by a numeric column."],
    [("Rows first, columns second", "For a data frame, x[rows, columns] selects a smaller table. A blank side of the comma keeps everything on that side. A logical condition selects matching rows. Use & for 'and' and | for 'or'. Missing logical conditions need explicit handling when the source has NA."),
     ("Keep each row together", "order() returns row positions in sorted order. Apply those positions to the whole table, rather than sorting one column and putting it back. Sorting just the scores would attach them to the wrong students.")],
    ["Import the five-row CSV and run students[, c('student', 'exam_score')].", "Run students[students$study_hours >= 3, ]. Explain which rows remain.", "Run students[order(students$exam_score), ] and identify the first row.", "Try a combined condition: students$study_hours >= 3 & students$coffee_cups <= 2.", "Create the independent results in Source, run and save."],
    "students <- read.csv('Data/students.csv')\nselected <- students[, c('student','exam_score')]\nfrequent <- students[students$study_hours >= 3, ]\nascending <- students[order(students$exam_score), ]",
    ["Import students, then create score_table containing only student and exam_score columns.", "Create focused containing students with study_hours >= 3.", "Create ranked by sorting the entire students table by exam_score from highest to lowest."],
    "focused contains Ben, Clara and Emma. ranked is ordered Clara, Ben, Emma, Anna, David. score_table has only the two requested columns.",
    ["Keep the comma in students[condition, ].", "Use decreasing = TRUE inside order().", "ranked <- students[order(students$exam_score, decreasing=TRUE), ]."],
    ["Why must you sort all columns together?", "How do row selection and column selection differ?"],
    ["Using = instead of == does not express an equality comparison.", "Omitting the comma can select columns instead of rows.", "sort(students$exam_score) alone does not sort the data frame."],
    "students <- read.csv('Data/students.csv')\nscore_table <- students[, c('student','exam_score')]\nfocused <- students[students$study_hours >= 3, ]\nranked <- students[order(students$exam_score, decreasing=TRUE), ]",
    "Column names select the two-variable table. A logical row condition selects three students. order returns row positions that keep each student's attributes together while sorting.",
    ["extract","order","comparison"], checks=[rows("score_table",5),cols("score_table",["student","exam_score"]),rows("focused",3),column("focused","student",["Ben","Clara","Emma"]),column("ranked","student",["Clara","Ben","Emma","Anna","David"])], self_checks=["I verified score_table contains exactly two columns."])

lesson(8,"clean","Correct and extend a table",
    "Make documented changes while preserving raw data.",
    ["Correct a known error and add a derived column.", "Add and remove rows while keeping a consistent schema."],
    [("A deliberate copy", "Assigning clean_students <- raw_students gives you a named working table. Make corrections in that table so you can compare it with the raw import. In this fixture Clara's 880 is documented to mean 88. Use a name-based condition rather than a fragile remembered row number."),
     ("New columns and rows", "You can add a column with $ and a calculation, then append a row with rbind() if its columns match. Remove a row with a logical condition or a negative row position. Document why you changed an observation; do not quietly delete inconvenient results.")],
    ["Import the extended fixture and copy it to practice_clean.", "Replace practice_clean$exam_score where student == 'Clara' with 88.", "Add study_minutes <- study_hours * 60 as a new column; observe that unknown hours remain unknown.", "In a separate practice copy, append a row with matching columns and then remove it by its student name.", "Build the independent exercise from the raw import, then run and save."],
    "raw_students <- read.csv('Data/students_extended.csv')\npractice_clean <- raw_students\npractice_clean$exam_score[practice_clean$student == 'Clara'] <- 88\npractice_clean$study_minutes <- practice_clean$study_hours * 60\nextra <- practice_clean[1, ]\nextra$student <- 'PracticeOnly'\npractice_copy <- rbind(practice_clean, extra)\npractice_copy <- practice_copy[practice_copy$student != 'PracticeOnly', ]",
    ["Import the extended CSV into raw_students and copy it to clean_students.", "Correct Clara's exam_score from 880 to 88. Keep all other original values and preserve the missing hours.", "Add study_minutes as study_hours * 60.", "Create with_new by adding Maya in group A, with 4 study hours, score 80, 1 coffee cup and 240 study minutes.", "Create without_new by removing Maya from with_new. Leave clean_students at the original 12 students."],
    "clean_students has 12 rows and six columns; Clara's score is 88. with_new has 13 rows, and without_new has 12. The raw import still contains 880.",
    ["Use clean_students$exam_score[clean_students$student == 'Clara'] <- 88.", "For rbind, supply a data.frame with the same column names.", "Remove Maya with with_new[with_new$student != 'Maya', ]."],
    ["Why use Clara's name instead of a row number?", "What happens to missing hours when multiplied by 60?"],
    ["Appending a row with different columns causes rbind errors.", "Changing raw_students erases your in-memory comparison point.", "NA in a row condition may introduce missing rows; handle it explicitly when applicable."],
    "raw_students <- read.csv('Data/students_extended.csv')\nclean_students <- raw_students\nclean_students$exam_score[clean_students$student == 'Clara'] <- 88\nclean_students$study_minutes <- clean_students$study_hours * 60\nwith_new <- rbind(clean_students, data.frame(student='Maya', study_hours=4, exam_score=80, coffee_cups=1, group='A', study_minutes=240))\nwithout_new <- with_new[with_new$student != 'Maya', ]",
    "A documented correction is applied to the working table, while the raw table stays untouched. Derived minutes preserve NA. rbind adds a schema-compatible observation, and a name-based condition removes just that observation.",
    ["extract","frames","arithmetic","na"], checks=[rows("clean_students",12),cols("clean_students",["study_minutes"]),column("clean_students","exam_score",[65,78,88,55,72,72,68,65,92,60,85,70]),column("clean_students","study_minutes",[120,240,300,60,180,240,120,None,360,60,300,180]),column("raw_students","exam_score",[65,78,880,55,72,72,68,65,92,60,85,70]),rows("with_new",13),rows("without_new",12)], self_checks=["Hugo's study_hours and study_minutes remain NA.", "Maya's new row contains the requested values."])

lesson(9,"summaries","Describe a group of values",
    "Calculate summaries and explain what they hide.",
    ["Calculate a mean, median and count.", "Interpret summaries with units and context."],
    [("Different questions, different summaries", "A mean divides a total by the number of observations. A median is the middle of sorted values, or the mean of the two middle values for an even count. Counts tell you how much data supports a summary. A mean can be strongly affected by an extreme value; compare summaries instead of assuming one number tells the whole story."),
     ("Give a number context", "Say what you summarized, the unit and how many observations contributed. The study dataset is invented for practice; it does not measure a real student population. Any pattern is descriptive, and it cannot demonstrate that study hours or coffee cause a change in exam scores.")],
    ["Run mean(c(1, 2, 9)) and median(c(1, 2, 9)). Explain why they differ.", "Import the five-row students table.", "Calculate mean(students$exam_score), median(students$exam_score) and nrow(students).", "Compare all exam scores with the summary; identify what the average leaves out.", "Complete and save your independent summary script."],
    "mean(c(1, 2, 9))\nmedian(c(1, 2, 9))\nstudents <- read.csv('Data/students.csv')\nsummary(students$exam_score)",
    ["Import the five-row students CSV.", "Create mean_score, median_score and sample_size from exam_score and the table.", "Create high_count as the number of exam_score values at least 75. Write an interpretation in the reflection below."],
    "The mean is 71.6, the median is 72, sample_size is 5 and high_count is 2.",
    ["Use mean() and median() on students$exam_score.", "nrow(students) counts students.", "sum(students$exam_score >= 75) counts TRUE comparisons."],
    ["Describe mean_score in a sentence with context and sample size.", "Why would these invented observations not prove that coffee improves exam results?"],
    ["mean(students) is not the mean of its score column.", "length(students) counts columns rather than students.", "A correlation is not evidence of causation, especially in invented practice data."],
    "students <- read.csv('Data/students.csv')\nmean_score <- mean(students$exam_score)\nmedian_score <- median(students$exam_score)\nsample_size <- nrow(students)\nhigh_count <- sum(students$exam_score >= 75)",
    "The five fictional scores total 358, giving mean 71.6. Their middle sorted score is 72. Two scores meet the 75 threshold. These are descriptions of a small invented table, not general conclusions about real students.",
    ["mean","median","sum"], checks=[num("mean_score",71.6),num("median_score",72),num("sample_size",5),num("high_count",2)])

lesson(9,"groups","Compare groups and report missingness",
    "Summarize cleaned data by group without hiding missing observations.",
    ["Use table() and aggregate().", "Separate total rows from available observations."],
    [("A summary for each group", "table(group) counts category entries. aggregate(exam_score ~ group, data = ..., FUN = mean) splits scores by group and applies mean. In that formula, the left side is summarized and the right side supplies groups. Inspect the resulting column names before using them."),
     ("Make the denominator clear", "The number of rows and the number of known study-hours observations can differ. Count missing values explicitly. Correct the documented score typo before comparing score means. A group contrast in this fictional dataset is practice in description, not a treatment effect.")],
    ["Import the extended table and correct Clara's score in a working copy.", "Run table(clean_students$group).", "Run the aggregate example and read each row aloud.", "Count total students, known study_hours entries and missing study_hours entries.", "Write a standalone exercise script, run and save it."],
    "clean_students <- read.csv('Data/students_extended.csv')\nclean_students$exam_score[clean_students$student == 'Clara'] <- 88\ntable(clean_students$group)\naggregate(exam_score ~ group, data=clean_students, FUN=mean)",
    ["Import extended data into clean_students and correct Clara's score to 88.", "Create group_summary using aggregate to calculate mean exam_score by group, sorted by group.", "Create known_hours as the count of nonmissing study_hours and missing_hours as the missing count."],
    "Group A has six students and mean score 80; group B has six students and mean score 65. There are 11 known hours values and one missing.",
    ["Use aggregate(exam_score ~ group, data=clean_students, FUN=mean).", "Sort group_summary with order(group_summary$group).", "sum(!is.na(clean_students$study_hours)) counts known entries."],
    ["What does the ~ separate in this formula?", "What limitations should accompany the group comparison?"],
    ["Summarizing the uncorrected 880 inflates group A's mean.", "FUN=mean passes the function; FUN=mean() calls it too early.", "Do not count a missing entry as a measured zero."],
    "clean_students <- read.csv('Data/students_extended.csv')\nclean_students$exam_score[clean_students$student == 'Clara'] <- 88\ngroup_summary <- aggregate(exam_score ~ group, data=clean_students, FUN=mean)\ngroup_summary <- group_summary[order(group_summary$group), ]\nknown_hours <- sum(!is.na(clean_students$study_hours))\nmissing_hours <- sum(is.na(clean_students$study_hours))",
    "The corrected group means are 80 and 65, with six observations each. The hours column has only eleven known values. Reporting the missing count prevents a reader from mistaking all twelve rows for complete observations.",
    ["aggregate","table","na"], checks=[rows("group_summary",2),column("group_summary","group",["A","B"]),column("group_summary","exam_score",[80,65]),num("known_hours",11),num("missing_hours",1)])

lesson(10,"export-csv","Export a table and read it back",
    "Save a useful CSV and verify the file, not just the absence of an error.",
    ["Export with write.csv(..., row.names = FALSE).", "Reimport the output and verify its contents."],
    [("From memory back to disk", "write.csv() writes a table to a disk file. The output folder must exist. Use row.names = FALSE to avoid exporting an extra row-number column. Export paths follow the same working-directory rules as import paths. Writing an existing filename replaces its contents, so choose names deliberately."),
     ("Verify the round trip", "file.exists() proves a file exists, not that its contents are right. Reimport it, inspect columns and rows, and compare values. Open Outputs Folder lets you find the result without navigating LocalAppData manually. Checks require the export command to run again, so a leftover file cannot pass by itself.")],
    ["Use Open Outputs Folder to see where exports will appear.", "In Source run dir.create('Outputs', showWarnings = FALSE) before exporting.", "Import the five-row fixture and write a practice CSV with row.names = FALSE.", "Read the practice file back and inspect its names, rows and values.", "Complete the independent export, run, save and inspect the resulting file."],
    "dir.create('Outputs', showWarnings=FALSE)\nstudents <- read.csv('Data/students.csv')\nwrite.csv(students, 'Outputs/practice.csv', row.names=FALSE)\nround_trip <- read.csv('Outputs/practice.csv')\nhead(round_trip)",
    ["Import the five-row CSV into students.", "Create exported containing student and exam_score, in that order.", "Write exported to Outputs/students_export.csv without row names.", "Read it back into reopened. Verify the columns and values, and save your script."],
    "The exported CSV has five rows and exactly student and exam_score columns. Reimporting gives the same table.",
    ["Create the Outputs folder before writing.", "Use write.csv(exported, 'Outputs/students_export.csv', row.names=FALSE).", "reopened <- read.csv('Outputs/students_export.csv')."],
    ["Why is file.exists() alone an incomplete export check?", "What extra column appears if you omit row.names = FALSE?"],
    ["Cannot open connection may mean the output folder is missing.", "An old file can remain after a failed run; regenerate and inspect it.", "Exporting to an absolute personal path makes the script less portable."],
    "students <- read.csv('Data/students.csv')\nexported <- students[, c('student','exam_score')]\ndir.create('Outputs', showWarnings=FALSE)\nwrite.csv(exported, 'Outputs/students_export.csv', row.names=FALSE)\nreopened <- read.csv('Outputs/students_export.csv')",
    "Selecting columns first controls the exported schema. row.names = FALSE prevents a surplus index column. Reimporting checks the actual saved artifact; the grader also compares its values with exported.",
    ["write","read"], checks=[rows("exported",5),column("exported","student",["Anna","Ben","Clara","David","Emma"]),column("exported","exam_score",[65,78,88,55,72]),rows("reopened",5),export("csv","Outputs/students_export.csv",["student","exam_score"],"exported")], self_checks=["I located the exported CSV and inspected the reimported values."])

lesson(11,"distributions","Build bar charts and histograms",
    "Choose a chart that answers a clear question.",
    ["Distinguish categories from a numeric distribution.", "Create barplot() and hist() charts in RStudio."],
    [("One bar per category", "A bar chart compares values attached to separate categories. For a small class, barplot(scores, names.arg = names) can compare individual students. Start its value axis at zero so bar lengths remain meaningful."),
     ("Intervals of a numeric variable", "A histogram groups numeric observations into intervals and shows how many fall into each. Its horizontal axis is numeric, not one label per student. Different break choices change the visual impression. Five values are too few for strong claims about a population's distribution.")],
    ["Import the five-row fixture in Source.", "Run the guided barplot and find it in RStudio's Plots tab.", "Run hist on exam_score; use Plots Back and Forward to compare charts.", "Try breaks = 3 and breaks = 6. Observe how grouping changes.", "Complete the independent plots. The app checks data, while you confirm visual observations."],
    "students <- read.csv('Data/students.csv')\nbarplot(students$exam_score, names.arg=students$student, ylim=c(0,100))\nhist(students$exam_score, main='Fictional exam scores', xlab='Score')",
    ["Import students and create bar_values from its exam_score column and bar_labels from its student column.", "Make a bar chart of those values with student labels and a zero-based score axis.", "Create score_hist <- hist(students$exam_score, plot = FALSE) to inspect counts, then draw the histogram with hist().", "Create histogram_count as sum(score_hist$counts). Save your script and inspect both charts in RStudio."],
    "The bar chart compares five students; the histogram counts the same five scores in numeric intervals. Both visuals require your observation, not an automated claim about appearance.",
    ["Use barplot(bar_values, names.arg=bar_labels, ylim=c(0,100)).", "hist(..., plot=FALSE) computes histogram bins without drawing.", "histogram_count <- sum(score_hist$counts)."],
    ["Which chart would show counts across score ranges?", "Why can changing histogram breaks change the visual impression?"],
    ["A bar chart of raw group names needs counts first; use table(group).", "A histogram is not one bar per named student.", "RStudio shows only the current plot; use plot history to revisit others."],
    "students <- read.csv('Data/students.csv')\nbar_values <- students$exam_score\nbar_labels <- students$student\nbarplot(bar_values, names.arg=bar_labels, ylim=c(0,100), ylab='Score')\nscore_hist <- hist(students$exam_score, plot=FALSE)\nhistogram_count <- sum(score_hist$counts)\nhist(students$exam_score, main='Fictional exam scores', xlab='Score')",
    "The same scores answer two different questions. Bars compare identified students, while histogram bins describe the distribution. The numeric checks verify inputs and counts; your checklist records that you examined the actual charts.",
    ["bar","hist"], checks=[vec("bar_values",[65,78,88,55,72]),vec("bar_labels",["Anna","Ben","Clara","David","Emma"]),num("histogram_count",5)], self_checks=["I drew and inspected a labeled bar chart with a zero-based value axis.", "I drew a histogram and compared at least two break choices."])

lesson(11,"relationships","Build scatter and line plots",
    "Separate a relationship between measurements from an ordered sequence.",
    ["Make a scatter plot of paired measurements.", "Use a line only when observation order has meaning."],
    [("Pairs of measurements", "A scatter plot places one point at each pair of x and y measurements. Here x is study hours and y is exam score for the same fictional student. A visual pattern is an association; it does not show that one variable caused the other."),
     ("Order gives a line meaning", "Connecting observations with a line implies a meaningful sequence, such as consecutive days. Connecting unrelated students in CSV row order suggests a sequence the data do not have. For line practice we use a separate, explicitly ordered seven-day study diary.")],
    ["Import students and run the guided scatter plot. Describe each axis and one point.", "In Console identify Anna's pair (2, 65) on the chart.", "Run the seven-day line example and describe its sequence.", "Try connecting students in their existing row order only as a thought experiment: explain why it could mislead.", "Create the independent data objects and charts in Source, then save."],
    "students <- read.csv('Data/students.csv')\nplot(students$study_hours, students$exam_score, xlab='Study hours', ylab='Exam score')\nday <- 1:7\npractice_hours <- c(1,2,1,3,2,4,3)\nplot(day, practice_hours, type='b', xlab='Day', ylab='Study hours')",
    ["Create x_hours and y_scores from the five-row students data and draw their scatter plot.", "Create days as 1:7 and daily_hours as c(1, 2, 1, 3, 2, 4, 3).", "Draw daily_hours against days with type = 'b' so both points and lines appear. Label both axes and save."],
    "The scatter contains five paired observations. The diary line follows seven ordered days; it is a separate practice series, not repeated measurements from the student CSV.",
    ["plot(x_hours, y_scores) maps hours to the horizontal axis.", "type = 'b' draws both points and lines.", "Keep the x and y vectors the same length."],
    ["What does one point represent in the scatter plot?", "Why is a line appropriate for the diary but not arbitrary student row order?"],
    ["Swapping axes changes the question the plot communicates.", "Different x/y lengths produce an error.", "A rising pattern in fictional data does not establish causation."],
    "students <- read.csv('Data/students.csv')\nx_hours <- students$study_hours\ny_scores <- students$exam_score\nplot(x_hours, y_scores, xlab='Study hours', ylab='Exam score', pch=19)\ndays <- 1:7\ndaily_hours <- c(1,2,1,3,2,4,3)\nplot(days, daily_hours, type='b', xlab='Day', ylab='Study hours')",
    "The scatter preserves each student's hour-score pair. The line chart follows the defined day sequence. Appropriate chart choice depends on what the observations represent, not simply on which plotting function is available.",
    ["plot"], checks=[vec("x_hours",[2,4,5,1,3]),vec("y_scores",[65,78,88,55,72]),vec("days",[1,2,3,4,5,6,7]),vec("daily_hours",[1,2,1,3,2,4,3])], self_checks=["I inspected the scatter and identified Anna's point.", "I inspected the labeled diary line and can explain why its order matters."])

lesson(12,"customize","Make a chart understandable",
    "Use titles, units, symbols and legends to communicate clearly.",
    ["Label axes and choose appropriate scales.", "Distinguish groups with symbols as well as colors."],
    [("Labels answer the reader's questions", "Use main for a title, xlab and ylab for axis labels, and xlim or ylim for deliberate bounds. Keep all observations visible unless a clearly explained question requires otherwise. A scatter plot need not start both axes at zero, but its scale should not exaggerate a claim."),
     ("Do not rely only on color", "Group colors can help, but some readers cannot distinguish them. Combine color with different point symbols (pch) and a legend that explains both. Titles should state what is shown rather than assert an unsupported cause. Our fictional data remain illustrative after styling.")],
    ["Import extended data and correct Clara's score. Exclude only rows with missing plotted values, noting how many remain.", "Run the guided plot with group colors and symbols.", "Add a legend with matching col and pch arguments.", "Compare a tight score axis with ylim = c(0,100); discuss how the impression changes without changing the data.", "Complete and save the independent chart. Visual design is self-checked."],
    "students <- read.csv('Data/students_extended.csv')\nstudents$exam_score[students$student == 'Clara'] <- 88\nplot_data <- students[complete.cases(students[, c('study_hours','exam_score')]), ]\npoint_colors <- ifelse(plot_data$group == 'A', '#087E8B', '#A55224')\npoint_symbols <- ifelse(plot_data$group == 'A', 16, 17)\nplot(plot_data$study_hours, plot_data$exam_score, col=point_colors, pch=point_symbols, main='Fictional students: hours and scores', xlab='Study hours per week', ylab='Exam score (0-100)', ylim=c(0,100))\nlegend('topleft', legend=c('Group A','Group B'), col=c('#087E8B','#A55224'), pch=c(16,17), bty='n')",
    ["Create plot_data from the corrected extended table, keeping only rows with known study_hours and exam_score.", "Create point_symbols as 16 for group A and 17 for group B, and point_colors using two distinguishable colors.", "Draw the scatter with a descriptive title, axis labels including units, a 0–100 score range, and a legend that matches colors and symbols.", "Create plotted_count as nrow(plot_data), inspect the chart and save."],
    "The chart has 11 points. Group identity is available through both symbols and color; one unknown-hours row is excluded explicitly.",
    ["complete.cases(students[, c('study_hours','exam_score')]) identifies complete plotted pairs.", "Use ifelse(plot_data$group == 'A', 16, 17).", "Make legend colors and pch values match the plot exactly."],
    ["How would someone distinguish groups without seeing color?", "What effect does the axis range have on the impression of differences?", "Which observation was omitted, and why should you mention it?"],
    ["A legend that reverses group symbols mislabels the chart.", "Leaving 880 uncorrected makes a 0–100 score axis hide that point.", "A title claiming coffee or study causes higher scores is unsupported."],
    "students <- read.csv('Data/students_extended.csv')\nstudents$exam_score[students$student == 'Clara'] <- 88\nplot_data <- students[complete.cases(students[, c('study_hours','exam_score')]), ]\npoint_symbols <- ifelse(plot_data$group == 'A', 16, 17)\npoint_colors <- ifelse(plot_data$group == 'A', '#087E8B', '#A55224')\nplotted_count <- nrow(plot_data)\nplot(plot_data$study_hours, plot_data$exam_score, col=point_colors, pch=point_symbols, main='Fictional students: hours and scores', xlab='Study hours per week', ylab='Exam score (0-100)', ylim=c(0,100))\nlegend('topleft', legend=c('Group A','Group B'), col=c('#087E8B','#A55224'), pch=c(16,17), bty='n')",
    "Eleven complete pairs are plotted. Numeric checks confirm the row count and group-symbol mapping; the observation checklist covers title, labels, scale and legend because output values cannot prove visual quality.",
    ["plot","legend","na"], checks=[rows("plot_data",11),num("plotted_count",11),vec("point_symbols",[16,16,16,17,17,16,17,16,17,16,17])], self_checks=["My title and axis labels describe variables with units.", "My legend matches both group colors and symbols.", "All eleven plotted values are visible and I recorded the missing observation."])

lesson(13,"export-plots","Export PNG and PDF charts",
    "Direct a plot into a file and close it properly.",
    ["Use png(), pdf() and dev.off() in the right order.", "Locate and inspect both exported formats."],
    [("A device is a destination", "R draws to an active graphics device. In RStudio that is normally the Plots pane. png() opens a PNG file device; pdf() opens a PDF device. Draw after opening it, then call dev.off() to finish and close that destination. Opening a device alone does not copy a previous plot."),
     ("Choose a format and verify", "PNG is a pixel image: width and height default to pixels. PDF uses page dimensions in inches and preserves vector drawing for simple charts. A file extension alone does not guarantee its contents are valid. Open the exported file in an external viewer and check readability. RStudio's Plots Export menu is useful interactively; saved device commands reproduce exports.")],
    ["Import the five-row fixture and make a scatter in RStudio.", "Use Plots > Export > Save as Image to inspect its interactive options; cancel or choose a practice filename.", "Run the guided PNG block as one sequence: open, draw, close.", "Run the PDF block, then use Open Outputs Folder and open both practice files.", "Write the independent export commands, run the whole script and save."],
    "students <- read.csv('Data/students.csv')\ndir.create('Outputs', showWarnings=FALSE)\npng('Outputs/practice.png', width=900, height=600)\nplot(students$study_hours, students$exam_score, xlab='Study hours', ylab='Exam score', pch=19)\ndev.off()\npdf('Outputs/practice.pdf', width=7, height=5)\nplot(students$study_hours, students$exam_score, xlab='Study hours', ylab='Exam score', pch=19)\ndev.off()",
    ["Import students and ensure Outputs exists.", "Export a labeled study_hours versus exam_score scatter to Outputs/study_scatter.png at 1000 × 700 pixels. Close the device.", "Export the same scatter to Outputs/study_scatter.pdf at 7 × 5 inches. Close that device too.", "Open both files, inspect them, and save the complete export script."],
    "Both files are regenerated by the script, with valid PNG/PDF signatures. The PNG is a 1000 × 700 pixel image. File checks cannot judge whether its labels communicate well; inspect them yourself.",
    ["The order is png(...), plot(...), dev.off().", "Draw again after pdf(...); it does not copy the previous chart.", "Use distinct filenames for PNG and PDF."],
    ["What goes wrong if you open a file device but never draw a plot?", "When might a PDF be more useful than a PNG?"],
    ["Forgetting dev.off() can leave an incomplete file or send later plots to the wrong place.", "Writing png() after plot() does not export the previous plot.", "The output folder must exist before opening a file device."],
    "students <- read.csv('Data/students.csv')\ndir.create('Outputs', showWarnings=FALSE)\npng('Outputs/study_scatter.png', width=1000, height=700)\nplot(students$study_hours, students$exam_score, main='Fictional study habits', xlab='Study hours', ylab='Exam score', pch=19, col='#087E8B')\ndev.off()\npdf('Outputs/study_scatter.pdf', width=7, height=5)\nplot(students$study_hours, students$exam_score, main='Fictional study habits', xlab='Study hours', ylab='Exam score', pch=19, col='#087E8B')\ndev.off()",
    "Each export opens its own destination, redraws the chart and closes the device. The checker validates the format and fresh creation; visual inspection confirms the chart, dimensions and labels meet the task.",
    ["png","pdf","devices"], checks=[rows("students",5),export("png","Outputs/study_scatter.png"),export("pdf","Outputs/study_scatter.pdf")], self_checks=["I opened the PNG and verified its dimensions and readable labels.", "I opened the PDF and verified the chart and labels.", "I explicitly closed both devices in my saved script."])

lesson(14,"capstone","Tell a careful data story",
    "Carry an analysis from a raw CSV to verified outputs and a short explanation.",
    ["Perform an end-to-end analysis without line-by-line instructions.", "Communicate findings and limitations from reproducible work."],
    [("Your brief", "You are preparing an illustrative report on fictional study habits. Use the twelve-row extended fixture. Correct only the documented 880-to-88 score typo. Preserve unknown hours, summarize scores by group, plot complete hour-score pairs and deliver a cleaned table plus shareable charts. Your work must run from a fresh R session using only the project files."),
     ("Explain the limits", "Write three short findings that name the relevant values, the number of observations and any missingness. Explain that the data are fictional and observational patterns do not establish causation. The reference answer is available whenever you need it, but first try composing your own workflow from earlier lessons.")],
    ["Read the brief and deliverables. Plan your analysis as comments in the exercise script.", "Review earlier lessons or documentation if a step is unfamiliar. There is no new guided code in this final task.", "Run the complete script from a fresh R session, save it, inspect every export, then use Check My Work."],
    "# Plan your own workflow here.\n# Import -> inspect -> correct -> summarize -> visualize -> export -> verify.",
    ["Import Data/students_extended.csv into raw_students. Create clean_students with Clara's score corrected to 88 and a study_minutes column; preserve all twelve students and Hugo's missing hours.", "Create group_summary with group and mean exam_score, sorted A then B. Create missing_hours as the count of unknown study_hours.", "Create plot_data containing complete study_hours/exam_score pairs; make a clear group-labeled scatter with colors and symbols.", "Export clean_students to Outputs/final_clean.csv and group_summary to Outputs/final_summary.csv, without row names.", "Export the scatter to Outputs/final_chart.png and Outputs/final_chart.pdf. Close devices and verify the actual files.", "Write your findings and limitations in the reflection fields. Save the full script so it runs independently."],
    "The cleaned table has 12 rows; the scatter has 11 points. Group mean scores are A = 80 and B = 65. There is one missing hours value. Four outputs reproduce the analysis; the report explains its limitations.",
    ["Reuse the structure of the cleaning and grouped-summary lessons. Keep raw_students unchanged.", "Build plot_data using complete.cases on the plotted columns; define one draw_chart function to avoid duplicating drawing commands.", "Open a PNG or PDF device, call your chart code, then dev.off(). Reimport CSVs to verify their contents."],
    ["Report three findings, including group means, sample sizes and missingness.", "Explain the data-quality correction and what evidence supports it in this exercise.", "What can and cannot be concluded about study hours, coffee and exam scores?", "How would a new R session recreate every exported result from your saved work?"],
    ["A successful Console session can hide missing lines in a saved script.", "A stale chart or CSV is not evidence that the current script can regenerate it.", "Do not turn an invented association into a causal claim.", "Do not replace Hugo's missing hours with zero or silently drop the row from the cleaned table."],
    "raw_students <- read.csv('Data/students_extended.csv', na.strings=c('', 'NA'))\nclean_students <- raw_students\nclean_students$exam_score[clean_students$student == 'Clara'] <- 88\nclean_students$study_minutes <- clean_students$study_hours * 60\nmissing_hours <- sum(is.na(clean_students$study_hours))\ngroup_summary <- aggregate(exam_score ~ group, data=clean_students, FUN=mean)\ngroup_summary <- group_summary[order(group_summary$group), ]\nplot_data <- clean_students[complete.cases(clean_students[, c('study_hours','exam_score')]), ]\ndraw_chart <- function() {\n  colors <- ifelse(plot_data$group == 'A', '#087E8B', '#A55224')\n  symbols <- ifelse(plot_data$group == 'A', 16, 17)\n  plot(plot_data$study_hours, plot_data$exam_score, col=colors, pch=symbols, main='Fictional student study', xlab='Study hours per week', ylab='Exam score (0-100)', ylim=c(0,100))\n  legend('topleft', legend=c('Group A','Group B'), col=c('#087E8B','#A55224'), pch=c(16,17), bty='n')\n}\ndraw_chart()\ndir.create('Outputs', showWarnings=FALSE)\nwrite.csv(clean_students, 'Outputs/final_clean.csv', row.names=FALSE)\nwrite.csv(group_summary, 'Outputs/final_summary.csv', row.names=FALSE)\npng('Outputs/final_chart.png', width=1000, height=700)\ndraw_chart()\ndev.off()\npdf('Outputs/final_chart.pdf', width=7, height=5)\ndraw_chart()\ndev.off()\nstopifnot(nrow(read.csv('Outputs/final_clean.csv')) == 12)\nstopifnot(nrow(read.csv('Outputs/final_summary.csv')) == 2)",
    "This pipeline preserves the raw import, documents one known correction, carries missing hours honestly, calculates grouped means and plots eleven complete pairs. CSV exports match the working tables. Group A's mean is 80 and B's is 65, each from six invented students; that contrast is descriptive, not causal. One student's unknown hours limits the plotted comparison. The saved script and project-relative files make every result reproducible.",
    ["read","extract","aggregate","write","plot","png","pdf"], checks=[rows("clean_students",12),cols("clean_students",["student","study_hours","exam_score","coffee_cups","group","study_minutes"]),column("clean_students","exam_score",[65,78,88,55,72,72,68,65,92,60,85,70]),column("clean_students","study_minutes",[120,240,300,60,180,240,120,None,360,60,300,180]),num("missing_hours",1),rows("plot_data",11),column("group_summary","group",["A","B"]),column("group_summary","exam_score",[80,65]),export("csv","Outputs/final_clean.csv",["student","study_hours","exam_score","coffee_cups","group","study_minutes"],"clean_students"),export("csv","Outputs/final_summary.csv",["group","exam_score"],"group_summary"),export("png","Outputs/final_chart.png"),export("pdf","Outputs/final_chart.pdf")], self_checks=["My full script runs after Session > Restart R without relying on old objects.", "I opened and inspected both CSVs, the PNG and the PDF.", "My report names the correction, sample sizes, missingness, fictional data and limits on causal claims."], minutes=50)

seed = """student,study_hours,exam_score,coffee_cups
Anna,2,65,1
Ben,4,78,3
Clara,5,88,2
David,1,55,0
Emma,3,72,2
"""
extended = """student,study_hours,exam_score,coffee_cups,group
Anna,2,65,1,A
Ben,4,78,3,A
Clara,5,880,2,A
David,1,55,0,B
Emma,3,72,2,B
Farah,4,72,1,A
George,2,68,2,B
Hugo,,65,1,B
Isla,6,92,0,A
Jonas,1,60,3,B
Kai,5,85,2,A
Lina,3,70,1,B
"""
(WORKSPACE / "Data/students.csv").write_text(seed, encoding="utf-8")
(WORKSPACE / "Data/students_extended.csv").write_text(extended, encoding="utf-8")
(WORKSPACE / "Scripts/helpers.R").write_text("# Shared helper for the path lesson.\ncourse_label <- 'Fictional student study'\n", encoding="utf-8")
(WORKSPACE / "StudentStudy.Rproj").write_text("Version: 1.0\n\nRestoreWorkspace: No\nSaveWorkspace: No\nAlwaysSaveHistory: No\n\nEnableCodeIndexing: Yes\nUseSpacesForTab: Yes\nNumSpacesForTab: 2\nEncoding: UTF-8\n", encoding="utf-8")
(WORKSPACE / "READ-ME-FIRST.txt").write_text("Open StudentStudy.Rproj in RStudio. Scripts contains your exercises; Solutions contains examples. Data is fictional. Run scripts from the project root. Outputs holds exported results. The companion never overwrites existing workspace files during startup. Restore datasets only through the app's backed-up reset action.\n", encoding="utf-8")
(CONTENT / "curriculum.json").write_text(json.dumps(dict(schemaVersion=1, version="1.0.0", lessons=LESSONS), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
references = "# Curriculum references\n\nChecked against official R and Posit documentation on 2026-10-27. Lessons and fictional examples are original teaching material. Documentation links supplement the offline lessons; the app does not require internet for teaching or grading. R-devel links track the upstream manual and can evolve; use ?function_name in your installed R for version-specific help.\n\n"
for item in LESSONS:
    references += f"## {item['displayTitle'] if 'displayTitle' in item else item['id'] + ': ' + item['title']}\n\n"
    references += "\n".join(f"- [{r['title']}]({r['url']})" for r in item['references']) + "\n\n"
(ROOT / "REFERENCES.md").write_text(references, encoding="utf-8")
print(f"Authored {len(LESSONS)} lessons across {len(set(x['module'] for x in LESSONS))} modules.")
