using System.Diagnostics;
using System.IO;
using System.Windows;
using Microsoft.Win32;
using RLearningLab.Core;

namespace RLearningLab.App;

public partial class SetupWindow : Window
{
    private readonly AppSettings settings;
    private readonly WorkspaceService workspace;
    private readonly JsonStore store;
    public SetupWindow(AppSettings settings, WorkspaceService workspace, JsonStore store)
    {
        InitializeComponent(); this.settings = settings; this.workspace = workspace; this.store = store;
        Height = Math.Min(Height, SystemParameters.WorkArea.Height - 24);
        Width = Math.Min(Width, SystemParameters.WorkArea.Width - 24);
        RscriptPathBox.Text = settings.RscriptPath; RStudioPathBox.Text = settings.RStudioPath;
        ExecutionAcknowledged.IsChecked = settings.ExecutionAcknowledged;
        WorkspacePathText.Text = workspace.Root + "\n\nProgress/settings: " + store.DirectoryPath;
        UpdateStatus();
    }
    private void UpdateStatus()
    {
        RStatus.Text = File.Exists(RscriptPathBox.Text) ? "Rscript found. Use Check R version to verify it starts." : "R not found. Install R, or select Rscript.exe manually.";
        RStudioStatus.Text = File.Exists(RStudioPathBox.Text) ? "RStudio executable found." : "RStudio not found. Install RStudio Desktop, or choose its executable.";
    }
    private static string? Browse(string filename)
    {
        var dialog = new OpenFileDialog { Title = "Choose " + filename, Filter = filename + "|" + filename + "|Executables|*.exe", CheckFileExists = true };
        return dialog.ShowDialog() == true ? dialog.FileName : null;
    }
    private void BrowseRClicked(object sender, RoutedEventArgs e) { var p = Browse("Rscript.exe"); if (p is not null) RscriptPathBox.Text = p; UpdateStatus(); }
    private void BrowseRStudioClicked(object sender, RoutedEventArgs e) { var p = Browse("rstudio.exe"); if (p is not null) RStudioPathBox.Text = p; UpdateStatus(); }
    private void DetectClicked(object sender, RoutedEventArgs e)
    {
        var r = Installations.FindRscript(); var ide = Installations.FindRStudio();
        if (r.Length > 0) RscriptPathBox.Text = r;
        if (ide.Length > 0) RStudioPathBox.Text = ide;
        UpdateStatus();
    }
    private async void VersionClicked(object sender, RoutedEventArgs e)
    {
        RStatus.Text = "Checking…";
        RStatus.Text = await Installations.RVersionAsync(RscriptPathBox.Text.Trim().Trim('"'));
    }
    private void SaveClicked(object sender, RoutedEventArgs e)
    {
        var r = RscriptPathBox.Text.Trim().Trim('"'); var ide = RStudioPathBox.Text.Trim().Trim('"');
        if ((r.Length > 0 && (!File.Exists(r) || !Path.GetFileName(r).Equals("Rscript.exe", StringComparison.OrdinalIgnoreCase))) ||
            (ide.Length > 0 && (!File.Exists(ide) || !Path.GetFileName(ide).Equals("rstudio.exe", StringComparison.OrdinalIgnoreCase))))
        { SetupStatus.Text = "Choose existing Rscript.exe and rstudio.exe files, or leave a path empty to configure it later."; return; }
        var updated = new AppSettings { RscriptPath = r, RStudioPath = ide, ExecutionAcknowledged = ExecutionAcknowledged.IsChecked == true };
        try
        {
            store.Save("settings.json", updated);
            settings.RscriptPath = updated.RscriptPath; settings.RStudioPath = updated.RStudioPath; settings.ExecutionAcknowledged = updated.ExecutionAcknowledged;
            Close();
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException) { SetupStatus.Text = "Settings could not be saved: " + ex.Message; }
    }
    private void CloseClicked(object sender, RoutedEventArgs e) => Close();
    private void OpenUrl(string url)
    { try { Process.Start(new ProcessStartInfo(url) { UseShellExecute = true }); } catch (System.ComponentModel.Win32Exception ex) { SetupStatus.Text = ex.Message; } }
    private void DownloadRClicked(object sender, RoutedEventArgs e) => OpenUrl("https://cran.r-project.org/bin/windows/base/");
    private void DownloadRStudioClicked(object sender, RoutedEventArgs e) => OpenUrl("https://posit.co/download/rstudio-desktop/");
    private void ResetSmallClicked(object sender, RoutedEventArgs e) => Restore("students.csv");
    private void ResetExtendedClicked(object sender, RoutedEventArgs e) => Restore("students_extended.csv");
    private void Restore(string name)
    {
        if (MessageBox.Show(this, $"Restore {name} from the shipped seed? The current CSV will first be backed up in your project's Backups folder. Your scripts and progress will stay intact.", "Restore dataset", MessageBoxButton.YesNo, MessageBoxImage.Question) != MessageBoxResult.Yes) return;
        try { SetupStatus.Text = "Restored. Previous data backup: " + workspace.RestoreDataset(name); }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException) { SetupStatus.Text = "Could not restore the dataset: " + ex.Message; }
    }
}
