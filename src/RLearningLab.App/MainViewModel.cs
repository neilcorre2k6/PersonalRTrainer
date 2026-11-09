using System.ComponentModel;
using System.Runtime.CompilerServices;
using RLearningLab.Core;

namespace RLearningLab.App;

public sealed class LessonItem(Lesson lesson, LearnerProgress progress) : INotifyPropertyChanged
{
    public Lesson Lesson { get; } = lesson;
    public string Title => Lesson.Title;
    public string ModuleLabel => $"MODULE {Lesson.Module:00} · {Lesson.ModuleTitle}";
    public string Marker => Complete ? "✓" : progress.For(Lesson.Id).Viewed ? "◦" : "·";
    public bool Complete => progress.For(Lesson.Id).Passed && Lesson.SelfChecks.All(c => progress.For(Lesson.Id).Confirmations.GetValueOrDefault(c));
    public event PropertyChangedEventHandler? PropertyChanged;
    public void Refresh() => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(""));
}

public sealed class MainViewModel(Curriculum curriculum, LearnerProgress progress) : INotifyPropertyChanged
{
    public List<LessonItem> Lessons { get; } = curriculum.Lessons.Select(l => new LessonItem(l, progress)).ToList();
    public string CourseProgress => $"{Lessons.Count(x => x.Complete)} of {Lessons.Count} lessons complete";
    public double ProgressPercent => 100.0 * Lessons.Count(x => x.Complete) / Lessons.Count;
    private LessonItem? selected;
    public LessonItem? Selected { get => selected; set { selected = value; Notify(); Notify(nameof(Lesson)); Notify(nameof(ModuleLabel)); Notify(nameof(LessonMeta)); } }
    public Lesson? Lesson => Selected?.Lesson;
    public string ModuleLabel => Selected?.ModuleLabel ?? "";
    public string LessonMeta => Lesson is null ? "" : $"{Lesson.EstimatedMinutes} min · {(Lesson.Validation.Count == 0 ? "Observation practice" : "Real R checks + observations")}";
    public event PropertyChangedEventHandler? PropertyChanged;
    private void Notify([CallerMemberName] string? name = null) => PropertyChanged?.Invoke(this, new(name));
    public void Refresh() { foreach (var item in Lessons) item.Refresh(); Notify(nameof(CourseProgress)); Notify(nameof(ProgressPercent)); }
}
