using System.Text.Json;

namespace RLearningLab.Core;

public static class SafePaths
{
    public static string Inside(string root, string relative)
    {
        if (string.IsNullOrWhiteSpace(relative) || System.IO.Path.IsPathRooted(relative))
            throw new InvalidDataException("A content path must be project-relative.");
        var fullRoot = System.IO.Path.GetFullPath(root).TrimEnd(System.IO.Path.DirectorySeparatorChar) + System.IO.Path.DirectorySeparatorChar;
        var full = System.IO.Path.GetFullPath(System.IO.Path.Combine(fullRoot, relative));
        if (!full.StartsWith(fullRoot, StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("A content path escapes its project folder.");
        return full;
    }
}

public sealed class JsonStore(string directory)
{
    public string DirectoryPath { get; } = System.IO.Path.GetFullPath(directory);
    public string RecoveryMessage { get; private set; } = "";

    public T Load<T>(string name) where T : new()
    {
        var path = SafePaths.Inside(DirectoryPath, name);
        if (!File.Exists(path)) return new T();
        try { return Read<T>(path); }
        catch (Exception ex) when (ex is JsonException or InvalidDataException)
        {
            File.Copy(path, path + ".corrupt-" + DateTime.UtcNow.ToString("yyyyMMddHHmmssfff"), false);
            if (File.Exists(path + ".bak"))
            {
                try
                {
                    var recovered = Read<T>(path + ".bak");
                    RecoveryMessage = "A damaged save was preserved; the previous backup was recovered.";
                    // Restore the good backup before the next save so it cannot be replaced by the corrupt primary.
                    File.Copy(path + ".bak", path, true);
                    return recovered;
                }
                catch (Exception backupError) when (backupError is JsonException or InvalidDataException) { }
            }
            RecoveryMessage = "A damaged save was preserved beside the original. A new save will be started.";
            File.Move(path, path + ".unreadable-" + Guid.NewGuid().ToString("N"));
            return new T();
        }
    }

    private static T Read<T>(string path)
    {
        using var doc = JsonDocument.Parse(File.ReadAllText(path));
        if (doc.RootElement.ValueKind != JsonValueKind.Object || !doc.RootElement.TryGetProperty("schemaVersion", out var v) || v.ValueKind != JsonValueKind.Number || !v.TryGetInt32(out var schemaVersion))
            throw new InvalidDataException("The save has no valid schema version.");
        if (schemaVersion != 1)
            throw new NotSupportedException("This save uses an unsupported schema. It has not been changed.");
        var result = JsonSerializer.Deserialize<T>(doc.RootElement, JsonDefaults.Options)
            ?? throw new InvalidDataException("The save is empty.");
        if (result is LearnerProgress p && (p.Lessons is null || p.Lessons.Values.Any(x => x is null || x.Confirmations is null || x.Reflections is null)))
            throw new InvalidDataException("The progress structure is incomplete.");
        return result;
    }

    public void Save<T>(string name, T value)
    {
        Directory.CreateDirectory(DirectoryPath);
        var path = SafePaths.Inside(DirectoryPath, name);
        var temp = path + ".tmp-" + Guid.NewGuid().ToString("N");
        try
        {
            using (var stream = new FileStream(temp, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                JsonSerializer.Serialize(stream, value, JsonDefaults.Options);
                stream.Flush(true);
            }
            if (File.Exists(path)) File.Replace(temp, path, path + ".bak");
            else File.Move(temp, path);
        }
        finally { if (File.Exists(temp)) File.Delete(temp); }
    }
}

public sealed class WorkspaceService(string contentRoot, string dataRoot)
{
    public string Root { get; } = System.IO.Path.Combine(dataRoot, "Workspaces", "Default", "StudentStudy");
    public string ContentRoot { get; } = contentRoot;
    public void Initialize()
    {
        Directory.CreateDirectory(Root);
        CopyMissing(System.IO.Path.Combine(ContentRoot, "Workspace"), Root);
        Directory.CreateDirectory(System.IO.Path.Combine(Root, "Outputs"));
        Directory.CreateDirectory(System.IO.Path.Combine(Root, "Backups"));
    }
    private static void CopyMissing(string source, string target)
    {
        foreach (var file in Directory.EnumerateFiles(source, "*", SearchOption.AllDirectories))
        {
            var destination = SafePaths.Inside(target, System.IO.Path.GetRelativePath(source, file));
            Directory.CreateDirectory(System.IO.Path.GetDirectoryName(destination)!);
            if (!File.Exists(destination)) File.Copy(file, destination, false);
        }
    }
    public string RestoreDataset(string name)
    {
        if (name is not ("students.csv" or "students_extended.csv")) throw new InvalidDataException("Unknown dataset.");
        var target = SafePaths.Inside(Root, "Data/" + name);
        var backup = SafePaths.Inside(Root, "Backups/" + System.IO.Path.GetFileNameWithoutExtension(name) + "-" + DateTime.UtcNow.ToString("yyyyMMddHHmmssfff") + "-" + Guid.NewGuid().ToString("N")[..6] + ".csv");
        if (File.Exists(target)) File.Copy(target, backup);
        File.Copy(SafePaths.Inside(ContentRoot, "Workspace/Data/" + name), target, true);
        return backup;
    }
}

public static class CurriculumLoader
{
    public static readonly HashSet<string> Kinds = ["numeric", "value", "vector", "type", "rows", "columns", "columnValues", "file", "csv", "png", "pdf"];
    public static Curriculum Load(string contentRoot)
    {
        var course = JsonSerializer.Deserialize<Curriculum>(File.ReadAllText(System.IO.Path.Combine(contentRoot, "curriculum.json")), JsonDefaults.Options)
            ?? throw new InvalidDataException("The curriculum is empty.");
        if (course.SchemaVersion != 1 || course.Lessons.Count == 0) throw new InvalidDataException("Unsupported curriculum schema or no lessons.");
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var l in course.Lessons)
        {
            if (string.IsNullOrWhiteSpace(l.Id) || !ids.Add(l.Id) || string.IsNullOrWhiteSpace(l.Title) || l.Tasks.Count == 0 || l.Hints.Count == 0 || l.Reflections.Count == 0 || l.References.Count == 0)
                throw new InvalidDataException("Lesson content is incomplete or has duplicate IDs.");
            foreach (var path in new[] { l.StarterScript, l.SolutionScript })
                if (!File.Exists(SafePaths.Inside(System.IO.Path.Combine(contentRoot, "Workspace"), path))) throw new InvalidDataException("Missing lesson asset: " + path);
            foreach (var check in l.Validation)
            {
                if (!Kinds.Contains(check.Kind) || string.IsNullOrWhiteSpace(check.Description)) throw new InvalidDataException("Unsupported validation rule.");
                if (check.Kind is "file" or "csv" or "png" or "pdf")
                {
                    SafePaths.Inside("C:/RLearningLab-validation", check.Path);
                    if (!check.Path.Replace('\\', '/').StartsWith("Outputs/", StringComparison.Ordinal)) throw new InvalidDataException("Export checks must use Outputs/.");
                }
                else if (string.IsNullOrWhiteSpace(check.Name) || check.Expected.ValueKind is JsonValueKind.Undefined or JsonValueKind.Null)
                    throw new InvalidDataException("A validation rule is missing its name or expected value.");
            }
            foreach (var reference in l.References)
                if (!Uri.TryCreate(reference.Url, UriKind.Absolute, out var uri) || uri.Scheme != "https") throw new InvalidDataException("Invalid documentation link.");
        }
        return course;
    }
}
