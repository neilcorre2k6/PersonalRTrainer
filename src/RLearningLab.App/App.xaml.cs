using System.IO;
using System.Windows;

namespace RLearningLab.App;

public partial class App : Application
{
    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        try
        {
            string? Option(string name) => e.Args.FirstOrDefault(x => x.StartsWith(name + "=", StringComparison.Ordinal))?[(name.Length + 1)..];
            var smokeRoot = Option("--smoke-test");
            if (smokeRoot is not null) System.Windows.Media.RenderOptions.ProcessRenderMode = System.Windows.Interop.RenderMode.SoftwareOnly;
            var dataRoot = Option("--data-root") ?? (smokeRoot is null ? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "RLearningLab") : Path.Combine(Path.GetFullPath(smokeRoot), "learner"));
            var window = new MainWindow(Path.Combine(AppContext.BaseDirectory, "Content"), dataRoot, smokeRoot);
            if (smokeRoot is null)
            {
                var area = SystemParameters.WorkArea;
                window.MinWidth = Math.Min(window.MinWidth, area.Width - 24);
                window.MinHeight = Math.Min(window.MinHeight, area.Height - 24);
                window.Width = Math.Min(window.Width, area.Width - 24);
                window.Height = Math.Min(window.Height, area.Height - 24);
            }
            MainWindow = window;
            window.Show();
        }
        catch (Exception ex)
        {
            MessageBox.Show("R Learning Lab could not open. Your existing scripts have not been overwritten.\n\n" + ex.Message + "\n\nKeep the Content folder next to RLearningLab.exe.", "R Learning Lab", MessageBoxButton.OK, MessageBoxImage.Error);
            Shutdown(1);
        }
    }
}
