using System.Diagnostics;
using Microsoft.Win32;

namespace RLearningLab.Core;

public static class Installations
{
    public static void PrepareEnvironment(ProcessStartInfo info)
    {
        // Unix-style C.UTF-8 inherited from development shells is not a valid
        // Windows R locale. Let R choose its native Windows UTF-8 locale instead.
        if (!OperatingSystem.IsWindows()) return;
        foreach (var key in new[] { "LANG", "LC_ALL", "LC_CTYPE", "LC_COLLATE", "LC_TIME", "LC_MONETARY" })
            if (info.Environment.TryGetValue(key, out var value) && value is "C.UTF-8" or "C.utf8") info.Environment.Remove(key);
    }
    public static string FindRscript()
    {
        var candidates = PathCandidates("Rscript.exe").ToList();
        if (OperatingSystem.IsWindows())
        {
            foreach (var hive in new[] { Registry.CurrentUser, Registry.LocalMachine })
            foreach (var keyName in new[] { @"SOFTWARE\R-core\R", @"SOFTWARE\R-core\R64" })
            {
                using var key = hive.OpenSubKey(keyName);
                if (key?.GetValue("InstallPath") is string path)
                {
                    candidates.Add(Path.Combine(path, "bin", "Rscript.exe"));
                    candidates.Add(Path.Combine(path, "bin", "x64", "Rscript.exe"));
                }
            }
        }
        foreach (var root in new[] { Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "R"), Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Programs", "R") })
        {
            if (!Directory.Exists(root)) continue;
            foreach (var folder in Directory.GetDirectories(root).OrderDescending())
            {
                candidates.Add(Path.Combine(folder, "bin", "Rscript.exe"));
                candidates.Add(Path.Combine(folder, "bin", "x64", "Rscript.exe"));
            }
        }
        return candidates.FirstOrDefault(File.Exists) ?? "";
    }
    public static string FindRStudio()
    {
        var candidates = PathCandidates("rstudio.exe").ToList();
        if (OperatingSystem.IsWindows())
        {
            foreach (var hive in new[] { Registry.CurrentUser, Registry.LocalMachine })
            {
                using var key = hive.OpenSubKey(@"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\rstudio.exe");
                if (key?.GetValue("") is string path) candidates.Add(path.Trim('"'));
            }
        }
        foreach (var root in new[] { Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Programs") })
        foreach (var folder in new[] { "RStudio", "Posit/RStudio" })
        {
            candidates.Add(Path.Combine(root, folder, "rstudio.exe"));
            candidates.Add(Path.Combine(root, folder, "bin", "rstudio.exe"));
        }
        return candidates.FirstOrDefault(File.Exists) ?? "";
    }
    private static IEnumerable<string> PathCandidates(string file) => (Environment.GetEnvironmentVariable("PATH") ?? "").Split(Path.PathSeparator).Where(x => !string.IsNullOrWhiteSpace(x)).Select(x => Path.Combine(x.Trim('"'), file));
    public static async Task<string> RVersionAsync(string path)
    {
        if (!File.Exists(path)) return "R not found. Install R, then browse to its Rscript.exe.";
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(5));
        using var process = new Process { StartInfo = new(path) { UseShellExecute = false, CreateNoWindow = true, RedirectStandardOutput = true, RedirectStandardError = true } };
        process.StartInfo.ArgumentList.Add("--version");
        PrepareEnvironment(process.StartInfo);
        try
        {
            process.Start();
            var output = process.StandardOutput.ReadToEndAsync(timeout.Token);
            var error = process.StandardError.ReadToEndAsync(timeout.Token);
            await process.WaitForExitAsync(timeout.Token);
            return process.ExitCode == 0 ? (await output + " " + await error).Trim() : "Rscript did not start successfully. Choose another installation.";
        }
        catch (OperationCanceledException) { try { process.Kill(true); } catch (InvalidOperationException) { } return "Rscript did not respond within five seconds."; }
        catch (System.ComponentModel.Win32Exception) { return "This file could not be launched as Rscript.exe."; }
    }
}
