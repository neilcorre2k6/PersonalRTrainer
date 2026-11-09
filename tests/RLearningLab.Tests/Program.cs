using System.Text.Json;
using RLearningLab.Core;

var root = Path.GetFullPath(args.ElementAtOrDefault(0) ?? Path.Combine(AppContext.BaseDirectory, "../../../../../"));
var content = Path.Combine(root, "Content");
var testRoot = Path.Combine(root, "artifacts", "tests", "run-" + DateTime.UtcNow.ToString("yyyyMMddHHmmssfff"));
Directory.CreateDirectory(testRoot);
var tests = new List<object>();
var failures = 0;
async Task Test(string name, Func<Task> work)
{
    try { await work(); tests.Add(new { name, passed = true }); Console.WriteLine("PASS " + name); }
    catch (Exception e) { failures++; tests.Add(new { name, passed = false, error = e.ToString() }); Console.WriteLine("FAIL " + name + "\n" + e); }
}
Task Sync(Action work) { work(); return Task.CompletedTask; }
void Require(bool condition, string message) { if (!condition) throw new Exception(message); }
T Expect<T>(Action work) where T : Exception
{ try { work(); } catch (T e) { return e; } throw new Exception("Expected " + typeof(T).Name); }

Curriculum? course = null;
await Test("Complete curriculum: 23 lessons, all 15 modules and all assets", () => Sync(() =>
{
    course = CurriculumLoader.Load(content);
    Require(course.Lessons.Count == 23 && course.Lessons.Select(l => l.Module).Distinct().Order().SequenceEqual(Enumerable.Range(0,15)), "Missing lessons/modules.");
    foreach (var l in course.Lessons)
        Require(l.Concepts.Count > 0 && l.GuidedSteps.Count > 0 && l.Tasks.Count > 0 && l.Hints.Count >= 2 && l.Reflections.Count >= 2 && l.CommonErrors.Count >= 2 && l.SolutionExplanation.Length > 50, "Incomplete lesson " + l.Id);
}));
if (course is null) return 1;
await Test("Reject absolute paths and directory traversal", () => Sync(() =>
{
    Expect<InvalidDataException>(() => SafePaths.Inside(testRoot, "../outside.txt"));
    Expect<InvalidDataException>(() => SafePaths.Inside(testRoot, Path.Combine(root, "outside.txt")));
    Require(SafePaths.Inside(testRoot, "Data/students.csv").StartsWith(testRoot), "Safe path failed.");
}));
var workspace = new WorkspaceService(content, Path.Combine(testRoot, "learner space é"));
await Test("Workspace initialization preserves scripts, dataset edits and output files", () => Sync(() =>
{
    workspace.Initialize();
    var script = SafePaths.Inside(workspace.Root, "Scripts/02-variables.R");
    var csv = SafePaths.Inside(workspace.Root, "Data/students.csv");
    File.WriteAllText(script, "# My work\nprice <- 99\n");
    File.AppendAllText(csv, "Test,1,2,3\n");
    var output = SafePaths.Inside(workspace.Root, "Outputs/my-output.txt"); File.WriteAllText(output, "preserve");
    workspace.Initialize();
    Require(File.ReadAllText(script).Contains("99") && File.ReadAllText(csv).Contains("Test,1") && File.ReadAllText(output) == "preserve", "Startup overwrote work.");
}));
await Test("Dataset reset preserves backup and keeps scripts intact", () => Sync(() =>
{
    var backup = workspace.RestoreDataset("students.csv");
    Require(File.ReadAllText(backup).Contains("Test,1"), "Backup lost edits.");
    Require(!File.ReadAllText(SafePaths.Inside(workspace.Root,"Data/students.csv")).Contains("Test,1"), "Seed not restored.");
    Require(File.ReadAllText(SafePaths.Inside(workspace.Root,"Scripts/02-variables.R")).Contains("99"), "Script changed.");
    Expect<InvalidDataException>(() => workspace.RestoreDataset("../invalid"));
}));
var store = new JsonStore(Path.Combine(testRoot,"storage"));
await Test("Atomic progress save restores stable IDs, attempts, confirmations and reflections", () => Sync(() =>
{
    var p = new LearnerProgress { CurriculumVersion = "1.0.0", SelectedLessonId = "02-variables" };
    var state = p.For("02-variables"); state.AttemptCount = 3; state.Passed = true; state.Reflections["why?"] = "é: my answer"; state.Confirmations["observed"] = true;
    store.Save("progress.json", p);
    state.AttemptCount = 4; store.Save("progress.json",p);
    var restored = store.Load<LearnerProgress>("progress.json");
    Require(restored.For("02-variables").AttemptCount == 4 && restored.For("02-variables").Passed && restored.For("02-variables").Reflections["why?"] == "é: my answer", "Progress round trip failed.");
    Require(!Directory.EnumerateFiles(store.DirectoryPath,"*.tmp-*").Any(), "Temporary save left behind.");
}));
await Test("Corrupt progress recovers prior backup and preserves damaged content", () => Sync(() =>
{
    File.WriteAllText(Path.Combine(store.DirectoryPath,"progress.json"),"{ broken");
    var recovered = store.Load<LearnerProgress>("progress.json");
    Require(recovered.For("02-variables").AttemptCount == 3, "Prior backup not recovered.");
    Require(Directory.EnumerateFiles(store.DirectoryPath,"*.corrupt-*").Any(), "Damaged save not preserved.");
    store.Save("progress.json", recovered);
    Require(store.Load<LearnerProgress>("progress.json").For("02-variables").Passed, "Recovered save was not reusable.");
}));
await Test("Unsupported future save schema remains untouched", () => Sync(() =>
{
    var path = Path.Combine(store.DirectoryPath,"future.json"); const string data = "{\"schemaVersion\":42}"; File.WriteAllText(path, data);
    Expect<NotSupportedException>(() => store.Load<LearnerProgress>("future.json")); Require(File.ReadAllText(path)==data, "Future save modified.");
}));
await Test("Structurally corrupt saves are preserved and recovered", () => Sync(() =>
{
    var corruptStore = new JsonStore(Path.Combine(testRoot, "corrupt-structure"));
    var p = new LearnerProgress(); p.For("02-variables").AttemptCount = 7;
    corruptStore.Save("progress.json", p); corruptStore.Save("progress.json", p);
    File.WriteAllText(Path.Combine(corruptStore.DirectoryPath,"progress.json"), "[1,2,3]");
    Require(corruptStore.Load<LearnerProgress>("progress.json").For("02-variables").AttemptCount == 7, "Invalid structure did not recover.");
    File.WriteAllText(Path.Combine(corruptStore.DirectoryPath,"progress.json"), "{\"schemaVersion\":\"invalid\"}");
    Require(corruptStore.Load<LearnerProgress>("progress.json").For("02-variables").AttemptCount == 7, "Invalid schema type did not recover.");
}));
await Test("Unknown validation kinds are rejected", () => Sync(() =>
{
    var badRoot = Path.Combine(testRoot,"invalid-content"); Directory.CreateDirectory(badRoot);
    var malformed = JsonSerializer.Deserialize<Curriculum>(File.ReadAllText(Path.Combine(content,"curriculum.json")),JsonDefaults.Options)!;
    malformed.Lessons[0].Validation.Add(new() { Kind = "arbitraryEval", Description="unsafe", Expected=JsonSerializer.SerializeToElement(0) });
    File.WriteAllText(Path.Combine(badRoot,"curriculum.json"),JsonSerializer.Serialize(malformed,JsonDefaults.Options));
    // Link assets by copying the shipped template only into this test directory.
    foreach (var file in Directory.EnumerateFiles(Path.Combine(content,"Workspace"),"*",SearchOption.AllDirectories))
    { var destination=Path.Combine(badRoot,"Workspace",Path.GetRelativePath(Path.Combine(content,"Workspace"),file)); Directory.CreateDirectory(Path.GetDirectoryName(destination)!); File.Copy(file,destination); }
    Expect<InvalidDataException>(() => CurriculumLoader.Load(badRoot));
}));
var variableLesson = course.Lessons.Single(l => l.Id == "02-variables");
await Test("Missing R produces NotRun and preserves the saved script", async () =>
{
    var before = File.ReadAllBytes(SafePaths.Inside(workspace.Root,variableLesson.StarterScript));
    var result = await new RExecutionService().RunAsync(Path.Combine(testRoot,"missing.exe"),workspace.Root,variableLesson);
    Require(result.Outcome==RunOutcome.NotRun, "Wrong missing-R status.");
    Require(before.SequenceEqual(File.ReadAllBytes(SafePaths.Inside(workspace.Root,variableLesson.StarterScript))),"Script changed.");
});

var rscript = args.ElementAtOrDefault(1) ?? Installations.FindRscript();
var integrationRun = File.Exists(rscript);
if (integrationRun)
{
    var execution = new RExecutionService();
    var scratch = Path.Combine(testRoot,"scratch");
    Task<RunResult> Run(Lesson lesson, TimeSpan? limit=null, CancellationToken token=default) => execution.RunAsync(rscript,workspace.Root,lesson,token,limit,scratch);
    void WriteScript(Lesson lesson, string code) => File.WriteAllText(SafePaths.Inside(workspace.Root,lesson.StarterScript),code,new System.Text.UTF8Encoding(false));
    foreach (var lesson in course.Lessons.Where(l => l.Validation.Count>0))
        await Test("Real R reference solution: " + lesson.Id, async () =>
        {
            WriteScript(lesson, File.ReadAllText(SafePaths.Inside(Path.Combine(content,"Workspace"),lesson.SolutionScript)));
            var result = await Run(lesson);
            Require(result.Outcome==RunOutcome.Passed, result.Message + "\n" + result.Diagnostics + "\n" + string.Join("\n", result.Checks.Where(c=>!c.Passed).Select(c=>c.Description+": "+c.Actual)));
        });
    await Test("Real R accepts equivalent assignments and extra printed output", async () =>
    {
        WriteScript(variableLesson,"price = 5 + 5\nquantity = 6 / 2\ntotal = quantity * price\nprint('RLL1 is ordinary student output')\n");
        Require((await Run(variableLesson)).Outcome==RunOutcome.Passed,"Equivalent answer failed.");
    });
    await Test("Real R wrong value is Incorrect, without erasing script", async () =>
    {
        const string code="price <- 10\nquantity <- 3\ntotal <- 31\n"; WriteScript(variableLesson,code);
        var result=await Run(variableLesson); Require(result.Outcome==RunOutcome.Incorrect,"Wrong result status.");
        Require(File.ReadAllText(SafePaths.Inside(workspace.Root,variableLesson.StarterScript))==code,"Grader modified script.");
    });
    await Test("Real R syntax error is RunFailed with useful feedback", async () =>
    {
        WriteScript(variableLesson,"price <- (\n"); var result=await Run(variableLesson);
        Require(result.Outcome==RunOutcome.RunFailed && result.Diagnostics.Length>0,"Syntax error not distinguished.");
    });
    await Test("Real R runtime error and nonzero exit are distinguished from incorrect values", async () =>
    {
        WriteScript(variableLesson,"stop('Deliberate test error')\n"); Require((await Run(variableLesson)).Outcome==RunOutcome.RunFailed,"Runtime error status.");
        WriteScript(variableLesson,"quit(status=7)\n"); Require((await Run(variableLesson)).Outcome==RunOutcome.RunFailed,"Process exit status.");
    });
    await Test("Real R fresh process cannot reuse prior variables", async () =>
    {
        WriteScript(variableLesson,"price <- 10\nquantity <- 3\ntotal <- 30\n"); Require((await Run(variableLesson)).Outcome==RunOutcome.Passed,"Baseline did not pass.");
        WriteScript(variableLesson,"print('no assignments')\n"); Require((await Run(variableLesson)).Outcome==RunOutcome.Incorrect,"Old values leaked.");
    });
    await Test("Real R timeout and cancellation terminate execution without freezing", async () =>
    {
        WriteScript(variableLesson,"Sys.sleep(60)\n");
        Require((await Run(variableLesson,TimeSpan.FromMilliseconds(700))).Outcome==RunOutcome.TimedOut,"Timeout failed.");
        using var cancel=new CancellationTokenSource(TimeSpan.FromMilliseconds(700));
        Require((await Run(variableLesson,TimeSpan.FromSeconds(15),cancel.Token)).Outcome==RunOutcome.Cancelled,"Cancellation failed.");
    });
    await Test("Real R output is bounded while streams continue draining", async () =>
    {
        WriteScript(variableLesson,"price<-10;quantity<-3;total<-30\ncat(rep('x',50000),sep='')\n");
        var result=await Run(variableLesson); Require(result.Outcome==RunOutcome.Passed && result.Diagnostics.Length<33000,"Output drain failed.");
    });
    await Test("Real R working-directory mismatch has intelligible feedback", async () =>
    {
        WriteScript(variableLesson,"price<-10;quantity<-3;total<-30\nsetwd('Data')\n"); var result=await Run(variableLesson);
        Require(result.Outcome==RunOutcome.RunFailed && result.Diagnostics.Contains("working directory"),"Working-directory change was not reported.");
    });
    await Test("Real R rejects stale exported files", async () =>
    {
        var lesson=course.Lessons.Single(l=>l.Id=="10-export-csv");
        WriteScript(lesson,File.ReadAllText(SafePaths.Inside(Path.Combine(content,"Workspace"),lesson.SolutionScript)));
        Require((await Run(lesson)).Outcome==RunOutcome.Passed,"Fresh export failed.");
        WriteScript(lesson,"students<-read.csv('Data/students.csv')\nexported<-students[,c('student','exam_score')]\nreopened<-read.csv('Outputs/students_export.csv')\n");
        var stale=await Run(lesson); Require(stale.Outcome==RunOutcome.Incorrect && stale.Checks.Any(c=>c.Actual.Contains("not updated")),"Stale output passed.");
    });
    await Test("Real R detects wrong file signatures and malformed CSV", async () =>
    {
        var lesson=course.Lessons.Single(l=>l.Id=="13-export-plots");
        WriteScript(lesson,"students<-read.csv('Data/students.csv')\nwriteLines('fake image','Outputs/study_scatter.png')\nwriteLines('fake pdf','Outputs/study_scatter.pdf')\n");
        Require((await Run(lesson)).Outcome==RunOutcome.Incorrect,"False image signatures passed.");
        var csvLesson=course.Lessons.Single(l=>l.Id=="10-export-csv");
        WriteScript(csvLesson,"students<-read.csv('Data/students.csv')\nexported<-students[,c('student','exam_score')]\nreopened<-exported\nwriteLines('wrong;header\\n1;2','Outputs/students_export.csv')\n");
        Require((await Run(csvLesson)).Outcome==RunOutcome.Incorrect,"Malformed CSV passed.");
    });
    await Test("Real R scratch folders are cleaned after success, failure and cancellation", () => Sync(() => Require(!Directory.Exists(scratch) || !Directory.EnumerateFileSystemEntries(scratch).Any(),"Execution scratch leaked.")));
}
else Console.WriteLine("SKIP real-R integration tests: no Rscript supplied or detected.");

var report=new { timestampUtc=DateTimeOffset.UtcNow, failures, tests=tests.Count, realRIntegration=integrationRun, rscript=integrationRun?rscript:null, results=tests };
File.WriteAllText(Path.Combine(testRoot,"test-results.json"),JsonSerializer.Serialize(report,JsonDefaults.Options));
File.WriteAllText(Path.Combine(root,"artifacts","latest-test-results.json"),JsonSerializer.Serialize(report,JsonDefaults.Options));
Console.WriteLine($"\n{tests.Count-failures}/{tests.Count} passed. Report: {testRoot}");
return failures==0?0:1;
