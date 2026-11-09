using System.Text.Json;
using System.Text.Json.Serialization;

namespace RLearningLab.Core;

public sealed class Curriculum
{
    public int SchemaVersion { get; set; } = 1;
    public string Version { get; set; } = "1.0.0";
    public List<Lesson> Lessons { get; set; } = [];
}

public sealed class Lesson
{
    public string Id { get; set; } = "";
    public int Module { get; set; }
    public string ModuleTitle { get; set; } = "";
    public string Title { get; set; } = "";
    public string Summary { get; set; } = "";
    public int EstimatedMinutes { get; set; }
    public List<string> Objectives { get; set; } = [];
    public List<LessonSection> Concepts { get; set; } = [];
    public List<string> GuidedSteps { get; set; } = [];
    public string GuidedCode { get; set; } = "";
    public List<string> Tasks { get; set; } = [];
    public string ExpectedObservation { get; set; } = "";
    public List<string> SelfChecks { get; set; } = [];
    public List<string> Hints { get; set; } = [];
    public List<string> Reflections { get; set; } = [];
    public List<string> CommonErrors { get; set; } = [];
    public string SolutionExplanation { get; set; } = "";
    public string StarterScript { get; set; } = "";
    public string SolutionScript { get; set; } = "";
    public List<ValidationRule> Validation { get; set; } = [];
    public List<Reference> References { get; set; } = [];
    public string DisplayTitle => $"{Module:00}  {Title}";
}

public sealed class LessonSection
{
    public string Heading { get; set; } = "";
    public string Text { get; set; } = "";
}
public sealed class Reference
{
    public string Title { get; set; } = "";
    public string Url { get; set; } = "";
}
public sealed class ValidationRule
{
    public string Kind { get; set; } = "";
    public string Name { get; set; } = "";
    public string Column { get; set; } = "";
    public string Path { get; set; } = "";
    public JsonElement Expected { get; set; }
    public double Tolerance { get; set; } = 0.000001;
    public string Description { get; set; } = "";
    public string Help { get; set; } = "";
}

public sealed class LearnerProgress
{
    public int SchemaVersion { get; set; } = 1;
    public string CurriculumVersion { get; set; } = "";
    public string SelectedLessonId { get; set; } = "";
    public Dictionary<string, LessonState> Lessons { get; set; } = [];
    public LessonState For(string id)
    {
        if (!Lessons.TryGetValue(id, out var state)) Lessons[id] = state = new();
        return state;
    }
}
public sealed class LessonState
{
    public bool Viewed { get; set; }
    public bool Passed { get; set; }
    public int AttemptCount { get; set; }
    public string LastOutcome { get; set; } = "Not run";
    public DateTimeOffset? LastCheckedUtc { get; set; }
    public Dictionary<string, bool> Confirmations { get; set; } = [];
    public Dictionary<string, string> Reflections { get; set; } = [];
}
public sealed class AppSettings
{
    public int SchemaVersion { get; set; } = 1;
    public string RscriptPath { get; set; } = "";
    public string RStudioPath { get; set; } = "";
    public bool ExecutionAcknowledged { get; set; }
}
public enum RunOutcome { NotRun, RunFailed, Incorrect, Passed, Cancelled, TimedOut }
public sealed record CheckResult(bool Passed, string Description, string Actual, string Help);
public sealed record RunResult(RunOutcome Outcome, string Message, IReadOnlyList<CheckResult> Checks, string Diagnostics = "");

public static class JsonDefaults
{
    public static readonly JsonSerializerOptions Options = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        PropertyNameCaseInsensitive = true,
        WriteIndented = true,
        Converters = { new JsonStringEnumConverter() }
    };
}
