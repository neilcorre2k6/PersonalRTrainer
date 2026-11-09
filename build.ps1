param(
    [switch]$FrameworkDependent,
    [string]$Rscript = "",
    [switch]$SkipTests,
    [string]$RuntimeVersion = "8.0.33"
)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    dotnet build RLearningLab.sln -c Release
    if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }
    if (-not $SkipTests) {
        if ($Rscript) { dotnet run --project tests/RLearningLab.Tests -c Release --no-build -- $PSScriptRoot $Rscript }
        else { dotnet run --project tests/RLearningLab.Tests -c Release --no-build -- $PSScriptRoot }
        if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }
    }
    if ($FrameworkDependent) {
        dotnet publish src/RLearningLab.App -c Release --self-contained false -o dist-framework-dependent
    } else {
        dotnet publish src/RLearningLab.App -c Release -r win-x64 --self-contained true "-p:RuntimeFrameworkVersion=$RuntimeVersion" "-p:RestorePackagesPath=$PSScriptRoot/tools/.runtime/nuget" -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -p:EnableCompressionInSingleFile=true -p:DebugType=embedded -o dist
    }
    if ($LASTEXITCODE -ne 0) { throw 'Publish failed.' }
    $outputFolder = if ($FrameworkDependent) { 'dist-framework-dependent' } else { 'dist' }
    Copy-Item -LiteralPath 'START-HERE.txt','README.md','REFERENCES.md','TESTING.md' -Destination $outputFolder
    if (-not $FrameworkDependent) {
        $licenseFolder = Join-Path $outputFolder 'Licenses'
        New-Item -ItemType Directory -Path $licenseFolder -Force | Out-Null
        Copy-Item -LiteralPath "tools/.runtime/nuget/microsoft.netcore.app.runtime.win-x64/$RuntimeVersion/LICENSE.TXT" -Destination (Join-Path $licenseFolder 'dotnet-LICENSE.txt')
        Copy-Item -LiteralPath "tools/.runtime/nuget/microsoft.netcore.app.runtime.win-x64/$RuntimeVersion/THIRD-PARTY-NOTICES.TXT" -Destination (Join-Path $licenseFolder 'dotnet-THIRD-PARTY-NOTICES.txt')
        Copy-Item -LiteralPath "tools/.runtime/nuget/microsoft.windowsdesktop.app.runtime.win-x64/$RuntimeVersion/LICENSE" -Destination (Join-Path $licenseFolder 'windowsdesktop-LICENSE.txt')
    }
    $exeHash = (Get-FileHash -LiteralPath (Join-Path $outputFolder 'RLearningLab.exe') -Algorithm SHA256).Hash
    Set-Content -LiteralPath (Join-Path $outputFolder 'SHA256.txt') -Value "$exeHash  RLearningLab.exe" -Encoding ascii
    Write-Output "Ready: $outputFolder\RLearningLab.exe"
} finally { Pop-Location }
