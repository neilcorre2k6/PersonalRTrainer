using System.Diagnostics;
using System.Globalization;
using System.Text;
using System.Text.Json;

namespace RLearningLab.Core;

public sealed class RExecutionService
{
    public async Task<RunResult> RunAsync(string rscript, string projectRoot, Lesson lesson,
        CancellationToken cancellationToken = default, TimeSpan? timeout = null, string? scratchRoot = null)
    {
        if (!File.Exists(rscript)) return new(RunOutcome.NotRun, "Choose Rscript.exe in Setup before checking your work.", []);
        var script = SafePaths.Inside(projectRoot, lesson.StarterScript);
        if (!File.Exists(script)) return new(RunOutcome.NotRun, "The exercise script is missing. Reopen the app to restore missing starters.", []);
        var runRoot = Path.Combine(scratchRoot ?? Path.Combine(Path.GetTempPath(), "RLearningLab", "Runs"), Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(runRoot);
        var resultPath = Path.Combine(runRoot, "result.txt");
        var wrapper = Path.Combine(runRoot, "grader.R");
        var exports = lesson.Validation.Where(x => x.Kind is "file" or "csv" or "png" or "pdf")
            .Select(x => SafePaths.Inside(projectRoot, x.Path)).Distinct().ToDictionary(x => x, Stamp);
        try
        {
            await File.WriteAllTextAsync(wrapper, BuildWrapper(lesson, runRoot), new UTF8Encoding(false), cancellationToken);
            using var linked = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
            linked.CancelAfter(timeout ?? TimeSpan.FromSeconds(20));
            var info = new ProcessStartInfo(rscript) { WorkingDirectory = projectRoot, UseShellExecute = false, CreateNoWindow = true, RedirectStandardOutput = true, RedirectStandardError = true };
            info.ArgumentList.Add("--vanilla");
            info.ArgumentList.Add(wrapper);
            info.ArgumentList.Add(script);
            info.ArgumentList.Add(resultPath);
            Installations.PrepareEnvironment(info);
            using var process = new Process { StartInfo = info };
            process.Start();
            var stdout = DrainAsync(process.StandardOutput);
            var stderr = DrainAsync(process.StandardError);
            try { await process.WaitForExitAsync(linked.Token); }
            catch (OperationCanceledException)
            {
                try { process.Kill(true); } catch (InvalidOperationException) { }
                await process.WaitForExitAsync(CancellationToken.None);
                var details = await stdout + "\n" + await stderr;
                return cancellationToken.IsCancellationRequested
                    ? new(RunOutcome.Cancelled, "Check cancelled. Your saved script and earlier completion are preserved.", [], details)
                    : new(RunOutcome.TimedOut, "R took longer than the time limit. Look for a loop or a command waiting for input, then try again.", [], details);
            }
            var diagnostic = (await stdout + "\n" + await stderr).Trim();
            if (process.ExitCode != 0 || !File.Exists(resultPath) || new FileInfo(resultPath).Length > 131072)
                return new(RunOutcome.RunFailed, "R stopped before the checks finished. Run the saved script in RStudio and inspect its error message.", [], diagnostic);
            var lines = await File.ReadAllLinesAsync(resultPath, cancellationToken);
            if (lines.Length < 3 || lines[0] != "RLL1") return new(RunOutcome.RunFailed, "The grading result could not be read. Try again.", [], diagnostic);
            if (lines[1] != "OK") return new(RunOutcome.RunFailed, FriendlyError(Unhex(lines[2])), [], Unhex(lines[2]) + "\n" + diagnostic);
            if (lines.Length != lesson.Validation.Count + 3) return new(RunOutcome.RunFailed, "The grading result was incomplete. Try again.", [], diagnostic);
            var checks = new List<CheckResult>();
            for (var i = 0; i < lesson.Validation.Count; i++)
            {
                var rule = lesson.Validation[i];
                var fields = lines[i + 3].Split('\t');
                if (fields.Length != 3 || fields[0] != i.ToString(CultureInfo.InvariantCulture)) throw new InvalidDataException("Invalid check result.");
                var passed = fields[1] == "1";
                var actual = Unhex(fields[2]);
                if (rule.Kind is "file" or "csv" or "png" or "pdf")
                {
                    var path = SafePaths.Inside(projectRoot, rule.Path);
                    if (passed && Stamp(path) == exports[path]) { passed = false; actual = "This file was not updated by this run. Add the export command to your saved script."; }
                }
                checks.Add(new(passed, rule.Description, actual, passed ? "" : rule.Help));
            }
            var allPassed = checks.All(x => x.Passed);
            return new(allPassed ? RunOutcome.Passed : RunOutcome.Incorrect,
                allPassed ? "Your saved script passed the automatic checks. Complete any observation checklist below, too." : "Your script ran. A few results need another look; use the feedback below and try again.", checks, diagnostic);
        }
        catch (OperationCanceledException) { return new(RunOutcome.Cancelled, "Check cancelled.", []); }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or System.ComponentModel.Win32Exception or FormatException or InvalidDataException)
        { return new(RunOutcome.RunFailed, "The check could not finish. Confirm the Rscript path and that the project files are accessible.", [], ex.Message); }
        finally
        {
            // Only the unique scratch folder created by this invocation is removed.
            try { Directory.Delete(runRoot, true); } catch (IOException) { } catch (UnauthorizedAccessException) { }
        }
    }

    private static string Stamp(string path) => File.Exists(path) ? $"{File.GetLastWriteTimeUtc(path).Ticks}:{new FileInfo(path).Length}" : "missing";
    private static async Task<string> DrainAsync(StreamReader reader)
    {
        var buffer = new char[2048]; var text = new StringBuilder(); int count;
        while ((count = await reader.ReadAsync(buffer)) > 0)
            if (text.Length < 16000) text.Append(buffer, 0, Math.Min(count, 16000 - text.Length));
        if (text.Length == 16000) text.Append("\n[Further output omitted]");
        return text.ToString();
    }
    private static string Unhex(string text) => Encoding.UTF8.GetString(Convert.FromHexString(text));
    private static string FriendlyError(string error)
    {
        if (error.Contains("unexpected", StringComparison.OrdinalIgnoreCase)) return "R could not read part of your script. Check quotes, commas and brackets. Save your fix before trying again.";
        if (error.Contains("not found", StringComparison.OrdinalIgnoreCase)) return "R could not find a name or function. Check spelling and create each variable before using it.";
        if (error.Contains("cannot open", StringComparison.OrdinalIgnoreCase) || error.Contains("working directory", StringComparison.OrdinalIgnoreCase)) return "R could not find or open a file or folder. Check getwd(), your project, and the project-relative path. Remove hardcoded setwd() calls.";
        return "Your saved script raised an R error. Run it in RStudio, fix the first error and save, then try again. Technical details are available below.";
    }
    private static string Quote(string text) => "\"" + text.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "\\r").Replace("\n", "\\n").Replace("\t", "\\t") + "\"";
    private static string Literal(JsonElement value) => value.ValueKind switch
    {
        JsonValueKind.Number => value.GetRawText(), JsonValueKind.String => Quote(value.GetString()!),
        JsonValueKind.True => "TRUE", JsonValueKind.False => "FALSE", JsonValueKind.Null => "NA",
        JsonValueKind.Array => "c(" + string.Join(",", value.EnumerateArray().Select(Literal)) + ")",
        _ => "NULL"
    };
    private static string BuildWrapper(Lesson lesson, string runRoot)
    {
        var rules = string.Join(",\n", lesson.Validation.Select(r => $"list(kind={Quote(r.Kind)},name={Quote(r.Name)},column={Quote(r.Column)},path={Quote(r.Path)},expected={Literal(r.Expected)},tolerance={r.Tolerance.ToString("R", CultureInfo.InvariantCulture)})"));
        return "rules <- list(\n" + rules + "\n)\n" + "scratch_plot <- " + Quote(Path.Combine(runRoot, "incidental.pdf").Replace('\\', '/')) + "\n" + """
args <- commandArgs(trailingOnly=TRUE)
result_file <- args[2]
hex <- function(x) paste(sprintf("%02x", as.integer(charToRaw(enc2utf8(paste(x, collapse=" "))))), collapse="")
write_result <- function(lines) writeLines(lines, result_file, useBytes=TRUE)
student <- new.env(parent=globalenv())
initial_wd <- normalizePath(getwd(), winslash="/", mustWork=TRUE)
options(device=function(...) grDevices::pdf(file=scratch_plot))
err <- tryCatch({
  source(args[1], local=student, chdir=FALSE, encoding="UTF-8")
  if (!identical(normalizePath(getwd(), winslash="/", mustWork=TRUE), initial_wd))
    stop("The working directory changed. Reopen the RStudio Project and remove setwd() from the script.")
  grDevices::graphics.off()
  NULL
}, error=function(e) conditionMessage(e))
if (!is.null(err)) {
  write_result(c("RLL1", "ERROR", hex(err)))
} else {
  lines <- c("RLL1", "OK", "")
  for (i in seq_along(rules)) {
    r <- rules[[i]]
    outcome <- tryCatch({
      actual <- NULL
      if (r$kind %in% c("file", "csv", "png", "pdf")) {
        if (!file.exists(r$path)) stop("The expected output file does not exist.")
        if (file.info(r$path)$size < 1) stop("The output file is empty.")
        actual <- paste("File:", r$path)
        passed <- TRUE
        if (r$kind == "csv") {
          tab <- read.csv(r$path, check.names=FALSE)
          passed <- is.data.frame(tab) && nrow(tab) > 0 && identical(names(tab), as.character(r$expected))
          if (nzchar(r$name)) {
            if (!exists(r$name, envir=student, inherits=FALSE)) stop("Create the table before exporting it.")
            expected_table <- get(r$name, envir=student, inherits=FALSE)
            passed <- passed && isTRUE(all.equal(tab, expected_table, check.attributes=FALSE, tolerance=r$tolerance))
          }
          actual <- paste(nrow(tab), "rows; columns:", paste(names(tab), collapse=", "))
        }
        if (r$kind %in% c("png", "pdf")) {
          con <- file(r$path, "rb")
          signature <- readBin(con, "raw", n=8); close(con)
          passed <- if (r$kind == "png") identical(signature, as.raw(c(137,80,78,71,13,10,26,10))) else length(signature)>=5 && identical(signature[1:5], charToRaw("%PDF-"))
          if (!passed) actual <- "The file signature does not match its image format."
        }
      } else {
        if (!exists(r$name, envir=student, inherits=FALSE)) stop(paste("Create", r$name, "in the saved script."))
        x <- get(r$name, envir=student, inherits=FALSE)
        actual <- paste(capture.output(str(x, give.attr=FALSE)), collapse=" ")
        if (r$kind == "numeric") passed <- is.numeric(x) && length(x)==1 && is.finite(x) && abs(x-r$expected)<=r$tolerance
        if (r$kind == "value") passed <- isTRUE(all.equal(x, r$expected, check.attributes=FALSE, tolerance=r$tolerance))
        if (r$kind == "vector") passed <- is.atomic(x) && is.null(dim(x)) && length(x)==length(r$expected) && isTRUE(all.equal(x, r$expected, check.attributes=FALSE, tolerance=r$tolerance))
        if (r$kind == "type") passed <- identical(typeof(x), r$expected)
        if (r$kind == "rows") passed <- is.data.frame(x) && nrow(x)==r$expected
        if (r$kind == "columns") passed <- is.data.frame(x) && all(r$expected %in% names(x))
        if (r$kind == "columnValues") passed <- is.data.frame(x) && r$column %in% names(x) && isTRUE(all.equal(x[[r$column]], r$expected, check.attributes=FALSE, tolerance=r$tolerance))
      }
      list(passed=isTRUE(passed), actual=substr(actual, 1, 600))
    }, error=function(e) list(passed=FALSE, actual=conditionMessage(e)))
    lines <- c(lines, paste(i-1, as.integer(outcome$passed), hex(outcome$actual), sep="\t"))
  }
  write_result(lines)
}
""";
    }
}
