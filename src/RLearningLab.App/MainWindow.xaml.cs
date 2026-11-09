using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Windows;
using System.Windows.Automation;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using RLearningLab.Core;

namespace RLearningLab.App;

public partial class MainWindow : Window
{
    private readonly MainViewModel vm;
    private readonly JsonStore store;
    private readonly WorkspaceService workspace;
    private readonly LearnerProgress progress;
    private readonly AppSettings settings;
    private readonly DispatcherTimer autosave = new() { Interval = TimeSpan.FromMilliseconds(450) };
    private CancellationTokenSource? runCancellation;
    private bool closingRequested;
    private bool saveFailed;
    private int hintIndex;
    private readonly string? smokeRoot;
    private bool smokeStarted;
    private Lesson Current => vm.Lesson!;

    public MainWindow(string contentRoot, string dataRoot, string? smokeRoot)
    {
        InitializeComponent();
        this.smokeRoot = smokeRoot;
        var curriculum = CurriculumLoader.Load(contentRoot);
        store = new(dataRoot);
        settings = store.Load<AppSettings>("settings.json");
        progress = store.Load<LearnerProgress>("progress.json");
        progress.CurriculumVersion = curriculum.Version;
        workspace = new(contentRoot, dataRoot);
        workspace.Initialize();
        if (!File.Exists(settings.RscriptPath)) settings.RscriptPath = Installations.FindRscript();
        if (!File.Exists(settings.RStudioPath)) settings.RStudioPath = Installations.FindRStudio();
        vm = new(curriculum, progress);
        DataContext = vm;
        var initial = vm.Lessons.FindIndex(x => x.Lesson.Id == progress.SelectedLessonId);
        LessonList.SelectedIndex = initial < 0 ? 0 : initial;
        autosave.Tick += (_, _) => { autosave.Stop(); Save(); };
        Closing += OnClosing;
        Loaded += OnLoaded;
        if (store.RecoveryMessage.Length > 0) StatusText.Text = store.RecoveryMessage;
        else if (!File.Exists(settings.RscriptPath) || !File.Exists(settings.RStudioPath))
            StatusText.Text = "Welcome. Read the lessons now, then use Setup & tools to connect R and RStudio.";
    }

    private async void OnLoaded(object sender, RoutedEventArgs e)
    {
        if (smokeRoot is null || smokeStarted) return;
        smokeStarted = true;
        try
        {
            Directory.CreateDirectory(smokeRoot);
            for (var i = 0; i < vm.Lessons.Count; i++)
            {
                LessonList.SelectedIndex = i;
                await Dispatcher.Yield(DispatcherPriority.ApplicationIdle);
                if (LearnContent.Children.Count == 0 || TaskContent.Children.Count == 0) throw new InvalidDataException("A lesson view was empty.");
            }
            LessonList.SelectedIndex = 0;
            LessonTabs.SelectedIndex = 0;
            await CaptureAsync(this, "01-orientation.png");
            LessonList.SelectedIndex = vm.Lessons.FindIndex(x => x.Lesson.Id == "02-variables");
            LessonTabs.SelectedIndex = 1;
            await CaptureAsync(this, "02-practice.png");
            HintClicked(this, new());
            SolutionExpander.IsExpanded = true;
            await Dispatcher.Yield(DispatcherPriority.ApplicationIdle);
            if (SolutionContent.Children.Count == 0) throw new InvalidDataException("The solution failed to render.");
            LessonTabs.SelectedIndex = 2;
            await CaptureAsync(this, "03-reflections.png");
            LessonTabs.SelectedIndex = 3;
            await CaptureAsync(this, "04-references.png");
            var setup = new SetupWindow(settings, workspace, store) { Owner = this };
            setup.Show();
            await CaptureAsync(setup, "05-setup.png");
            setup.Close();
            Width = 1024; Height = 720;
            LessonTabs.SelectedIndex = 1;
            SolutionExpander.IsExpanded = false;
            await CaptureAsync(this, "06-compact-practice.png");
            File.WriteAllText(Path.Combine(smokeRoot, "ui-smoke.json"), JsonSerializer.Serialize(new { success = true, lessonsRendered = vm.Lessons.Count, screenshots = 6, compactWidth = ActualWidth, compactHeight = ActualHeight }, JsonDefaults.Options));
            Application.Current.Shutdown(0);
        }
        catch (Exception ex)
        {
            File.WriteAllText(Path.Combine(smokeRoot, "ui-smoke-error.txt"), ex.ToString());
            Application.Current.Shutdown(2);
        }
    }
    private async Task CaptureAsync(Window window, string name)
    {
        await Dispatcher.Yield(DispatcherPriority.ApplicationIdle);
        window.UpdateLayout();
        // An offscreen shown window has a renderable WPF presentation source even when
        // the launching shell requested a hidden window. It never takes focus.
        window.ShowActivated = false;
        window.ShowInTaskbar = false;
        window.Left = -20000;
        window.Top = -20000;
        window.Hide();
        window.WindowState = WindowState.Normal;
        window.Show();
        await Dispatcher.Yield(DispatcherPriority.ApplicationIdle);
        var visual = (FrameworkElement)window.Content;
        var width = Math.Max(640, window.ActualWidth - 16);
        var height = Math.Max(480, window.ActualHeight - 40);
        visual.Measure(new Size(width, height));
        visual.Arrange(new Rect(0, 0, width, height));
        visual.UpdateLayout();
        var bitmap = new RenderTargetBitmap((int)width, (int)height, 96, 96, PixelFormats.Pbgra32);
        bitmap.Render(visual);
        var pixels = new byte[(int)width * (int)height * 4];
        bitmap.CopyPixels(pixels, (int)width * 4, 0);
        if (!Enumerable.Range(0, pixels.Length / 4).Any(i => pixels[i * 4 + 3] != 0))
            throw new InvalidOperationException("The desktop did not render the test window. Run this UI smoke test on an interactive Windows desktop.");
        var encoder = new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(bitmap));
        using var stream = File.Create(Path.Combine(smokeRoot!, name)); encoder.Save(stream);
    }

    private void LessonSelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (vm?.Lesson is null) return;
        autosave.Stop();
        progress.SelectedLessonId = Current.Id;
        progress.For(Current.Id).Viewed = true;
        RenderLesson(); Save();
    }
    private TextBlock Text(string text, double size = 16, string color = "#16343E") => new()
    { Text = text, FontSize = size, Foreground = (Brush)new BrushConverter().ConvertFromString(color)!, TextWrapping = TextWrapping.Wrap, Margin = new(0, 0, 0, 12), LineHeight = size * 1.55 };
    private TextBlock Heading(string text) => new() { Text = text, FontSize = 21, FontWeight = FontWeights.SemiBold, Margin = new(0, 0, 0, 14) };
    private Border Card(StackPanel content) => new() { Style = (Style)FindResource("Card"), Child = content };
    private static void Clear(params Panel[] panels) { foreach (var panel in panels) panel.Children.Clear(); }
    private void AddSteps(Panel panel, IEnumerable<string> steps)
    {
        var i = 0;
        foreach (var step in steps) panel.Children.Add(Text($"{++i}.  {step}"));
    }
    private Border Code(string code)
    {
        var panel = new StackPanel();
        var copy = new Button { Content = "Copy example", HorizontalAlignment = HorizontalAlignment.Right, FontSize = 12, Padding = new(10, 5, 10, 5) };
        copy.Click += (_, _) => { try { Clipboard.SetText(code); StatusText.Text = "Example copied. Paste it into RStudio Source to try it."; } catch (System.Runtime.InteropServices.COMException) { StatusText.Text = "The clipboard is busy. Try copying again."; } };
        panel.Children.Add(copy);
        var block = Text(code, 14, "#E1F0EE"); block.FontFamily = new("Consolas");
        AutomationProperties.SetName(block, "Read-only R example");
        panel.Children.Add(block);
        return new() { Child = panel, Background = new SolidColorBrush(Color.FromRgb(22, 52, 62)), Padding = new(18), CornerRadius = new(8), Margin = new(0, 8, 0, 16) };
    }
    private void RenderLesson()
    {
        Clear(LearnContent, TaskContent, SelfCheckContent, ReflectionContent, ReferenceContent, HintContent, SolutionContent, ErrorContent, FeedbackChecks);
        hintIndex = 0; HintButton.IsEnabled = true; SolutionExpander.IsExpanded = false;
        LearnScroll.ScrollToTop(); PracticeScroll.ScrollToTop();
        var goals = new StackPanel(); goals.Children.Add(Heading("What you’ll be able to do"));
        foreach (var goal in Current.Objectives) goals.Children.Add(Text("•  " + goal));
        LearnContent.Children.Add(Card(goals));
        foreach (var section in Current.Concepts)
        {
            var content = new StackPanel(); content.Children.Add(Heading(section.Heading)); content.Children.Add(Text(section.Text)); LearnContent.Children.Add(Card(content));
        }
        var guided = new StackPanel(); guided.Children.Add(Heading("Try it with guidance")); AddSteps(guided, Current.GuidedSteps);
        guided.Children.Add(Code(Current.GuidedCode));
        guided.Children.Add(Text("When you’re ready, choose Practice & check for your independent task.", 14, "#087E8B"));
        LearnContent.Children.Add(Card(guided));
        TaskContent.Children.Add(Heading("Your independent task"));
        TaskContent.Children.Add(Text("In RStudio Source: " + Current.StarterScript, 14, "#087E8B"));
        AddSteps(TaskContent, Current.Tasks);
        TaskContent.Children.Add(Heading("What to expect")); TaskContent.Children.Add(Text(Current.ExpectedObservation));
        var lesson = Current;
        var state = progress.For(lesson.Id);
        foreach (var item in lesson.SelfChecks)
        {
            var box = new CheckBox { Content = Text(item, 15), IsChecked = state.Confirmations.GetValueOrDefault(item) };
            AutomationProperties.SetName(box, item);
            box.Checked += (_, _) => { state.Confirmations[item] = true; UpdateCompletion(); Save(); };
            box.Unchecked += (_, _) => { state.Confirmations[item] = false; UpdateCompletion(); Save(); };
            SelfCheckContent.Children.Add(box);
        }
        if (lesson.SelfChecks.Count == 0) SelfCheckContent.Children.Add(Text("There is no additional observation checklist for this lesson.", 14));
        foreach (var question in lesson.Reflections)
        {
            ReflectionContent.Children.Add(Text(question, 17));
            var answer = new TextBox { Text = state.Reflections.GetValueOrDefault(question, ""), AcceptsReturn = true, TextWrapping = TextWrapping.Wrap, MinHeight = 100, MaxHeight = 230, VerticalScrollBarVisibility = ScrollBarVisibility.Auto, Margin = new(0, 0, 0, 24) };
            AutomationProperties.SetName(answer, question);
            answer.TextChanged += (_, _) => { state.Reflections[question] = answer.Text; SaveStatus.Text = "Saving…"; autosave.Stop(); autosave.Start(); };
            ReflectionContent.Children.Add(answer);
        }
        foreach (var reference in lesson.References)
        {
            var link = new Button { Content = new TextBlock { Text = reference.Title, TextWrapping = TextWrapping.Wrap }, HorizontalContentAlignment = HorizontalAlignment.Left, Padding = new(14), Margin = new(0, 0, 0, 12) };
            link.Click += (_, _) => Launch(reference.Url); ReferenceContent.Children.Add(link);
        }
        foreach (var error in lesson.CommonErrors) ErrorContent.Children.Add(Text("•  " + error, 15));
        FeedbackTitle.Text = state.AttemptCount == 0 ? "Not run yet. Take your time." : $"Last result: {state.LastOutcome} · {state.AttemptCount} attempt(s). Earlier detailed feedback is not retained.";
        DiagnosticsText.Text = ""; SaveStatus.Text = "Your reflections save locally.";
        CheckButton.Content = lesson.Validation.Count == 0 ? "Confirm this practice" : "_Check My Work";
        UpdateCompletion();
    }

    private bool Save()
    {
        try { store.Save("progress.json", progress); SaveStatus.Text = "Saved on this computer."; saveFailed = false; return true; }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        { saveFailed = true; SaveStatus.Text = "Could not save. Keep the app open and check folder permissions."; StatusText.Text = "Progress could not be saved: " + ex.Message; return false; }
    }
    private void UpdateCompletion()
    {
        vm.Refresh();
        var state = progress.For(Current.Id);
        var observed = Current.SelfChecks.Count(c => state.Confirmations.GetValueOrDefault(c));
        CompletionText.Text = vm.Selected!.Complete ? "✓ Lesson complete. You can still practice and revise your reflections."
            : $"{observed}/{Current.SelfChecks.Count} observations confirmed. " + (state.Passed ? Current.Validation.Count == 0 ? "Practice was self-confirmed; finish the observation checklist." : "Automatic checks passed." : Current.Validation.Count == 0 ? "Confirm the practice using the button above." : "Automatic checks are still needed.");
    }
    private async void CheckClicked(object sender, RoutedEventArgs e)
    {
        if (runCancellation is not null) return;
        var lesson = Current; var state = progress.For(lesson.Id);
        if (lesson.Validation.Count == 0)
        {
            if (!lesson.SelfChecks.All(c => state.Confirmations.GetValueOrDefault(c))) { FeedbackTitle.Text = "Complete the observation checklist first, then confirm your practice."; return; }
            state.Passed = true; state.AttemptCount++; state.LastOutcome = "Self-confirmed"; state.LastCheckedUtc = DateTimeOffset.UtcNow;
            FeedbackTitle.Text = "Practice self-confirmed. This records your observation, not automatic proof of RStudio actions.";
            UpdateCompletion(); Save(); return;
        }
        if (!File.Exists(settings.RscriptPath) || !settings.ExecutionAcknowledged)
        {
            SetupClicked(sender, e);
            if (!File.Exists(settings.RscriptPath) || !settings.ExecutionAcknowledged) { FeedbackTitle.Text = "Connect Rscript.exe and acknowledge local code execution in Setup before checking."; return; }
        }
        var alreadyPassed = state.Passed;
        runCancellation = new();
        CheckButton.IsEnabled = false; CancelButton.IsEnabled = true; LessonList.IsEnabled = false;
        RunProgress.Visibility = Visibility.Visible;
        FeedbackTitle.Text = "Running your saved script with R…"; FeedbackChecks.Children.Clear();
        try
        {
            var result = await new RExecutionService().RunAsync(settings.RscriptPath, workspace.Root, lesson, runCancellation.Token);
            if (result.Outcome != RunOutcome.NotRun) { state.AttemptCount++; state.LastCheckedUtc = DateTimeOffset.UtcNow; }
            state.LastOutcome = result.Outcome.ToString();
            if (result.Outcome == RunOutcome.Passed) state.Passed = true;
            FeedbackTitle.Text = result.Message + (alreadyPassed && result.Outcome != RunOutcome.Passed ? " Your earlier completion is preserved." : "");
            DiagnosticsText.Text = result.Diagnostics;
            foreach (var check in result.Checks)
            {
                FeedbackChecks.Children.Add(Text((check.Passed ? "✓  " : "↻  ") + check.Description, 15, check.Passed ? "#087E8B" : "#8B481B"));
                if (!check.Passed) { FeedbackChecks.Children.Add(Text(check.Actual, 14)); FeedbackChecks.Children.Add(Text(check.Help, 14, "#4D6570")); }
            }
            UpdateCompletion(); Save();
        }
        catch (Exception ex) { FeedbackTitle.Text = "The check could not finish. Your saved script is preserved."; DiagnosticsText.Text = ex.ToString(); }
        finally
        {
            runCancellation.Dispose(); runCancellation = null;
            CheckButton.IsEnabled = true; CancelButton.IsEnabled = false; LessonList.IsEnabled = true; RunProgress.Visibility = Visibility.Collapsed;
            if (closingRequested) Close();
        }
    }
    private void CancelClicked(object sender, RoutedEventArgs e) => runCancellation?.Cancel();
    private void HintClicked(object sender, RoutedEventArgs e)
    {
        if (hintIndex >= Current.Hints.Count) return;
        HintContent.Children.Add(Text($"Hint {hintIndex + 1}: {Current.Hints[hintIndex++]}", 15));
        HintButton.IsEnabled = hintIndex < Current.Hints.Count;
    }
    private void SolutionExpanded(object sender, RoutedEventArgs e)
    {
        if (vm?.Lesson is null || SolutionContent.Children.Count > 0) return;
        try
        {
            // Read the shipped answer, so learner edits to a workspace solution cannot change this explanation.
            SolutionContent.Children.Add(Code(File.ReadAllText(SafePaths.Inside(Path.Combine(workspace.ContentRoot, "Workspace"), Current.SolutionScript))));
            SolutionContent.Children.Add(Text(Current.SolutionExplanation));
        }
        catch (IOException ex) { StatusText.Text = "Could not read the example solution: " + ex.Message; }
    }
    private void SetupClicked(object sender, RoutedEventArgs e)
    {
        if (runCancellation is not null) return;
        new SetupWindow(settings, workspace, store) { Owner = this }.ShowDialog();
    }
    private void OpenProjectClicked(object sender, RoutedEventArgs e)
    {
        if (!File.Exists(settings.RStudioPath)) { SetupClicked(sender, e); if (!File.Exists(settings.RStudioPath)) return; }
        LaunchRStudio(Path.Combine(workspace.Root, "StudentStudy.Rproj"));
        StatusText.Text = "In RStudio, confirm StudentStudy is the active project. Write and run your code there.";
    }
    private void OpenExerciseClicked(object sender, RoutedEventArgs e)
    {
        if (!File.Exists(settings.RStudioPath)) { SetupClicked(sender, e); if (!File.Exists(settings.RStudioPath)) return; }
        LaunchRStudio(SafePaths.Inside(workspace.Root, Current.StarterScript));
        StatusText.Text = "Confirm RStudio is in StudentStudy. If a different window opens, open StudentStudy.Rproj, then use File > Open File for " + Current.StarterScript;
    }
    private void LaunchRStudio(string path)
    {
        try
        {
            var start = new ProcessStartInfo(settings.RStudioPath) { UseShellExecute = false, WorkingDirectory = workspace.Root };
            start.ArgumentList.Add(path); Process.Start(start);
        }
        catch (Exception ex) when (ex is System.ComponentModel.Win32Exception or IOException or UnauthorizedAccessException) { StatusText.Text = "RStudio could not open: " + ex.Message; }
    }
    private void OpenFolderClicked(object sender, RoutedEventArgs e) => Launch(workspace.Root);
    private void OpenOutputsClicked(object sender, RoutedEventArgs e) => Launch(Path.Combine(workspace.Root, "Outputs"));
    private void Launch(string path)
    {
        try { Process.Start(new ProcessStartInfo(path) { UseShellExecute = true }); }
        catch (System.ComponentModel.Win32Exception ex) { StatusText.Text = "Windows could not open this location: " + ex.Message; }
    }
    private void NextClicked(object sender, RoutedEventArgs e)
    {
        if (runCancellation is not null) return;
        if (LessonList.SelectedIndex < vm.Lessons.Count - 1) { LessonList.SelectedIndex++; LessonTabs.SelectedIndex = 0; LessonList.ScrollIntoView(LessonList.SelectedItem); }
        else StatusText.Text = "You reached the end of the course. Revisit any lesson whenever you want to practice.";
    }
    private void PreviousClicked(object sender, RoutedEventArgs e)
    {
        if (runCancellation is not null) return;
        if (LessonList.SelectedIndex > 0) { LessonList.SelectedIndex--; LessonTabs.SelectedIndex = 0; LessonList.ScrollIntoView(LessonList.SelectedItem); }
    }
    private void OnClosing(object? sender, CancelEventArgs e)
    {
        if (runCancellation is not null) { closingRequested = true; e.Cancel = true; runCancellation.Cancel(); return; }
        autosave.Stop();
        Save();
        if (saveFailed && smokeRoot is null)
            e.Cancel = MessageBox.Show(this, "Your latest progress could not be saved. Close anyway? Your R scripts remain saved separately.", "Unsaved progress", MessageBoxButton.YesNo, MessageBoxImage.Warning) != MessageBoxResult.Yes;
    }
}
