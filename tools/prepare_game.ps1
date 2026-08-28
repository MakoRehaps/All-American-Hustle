$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Data = Join-Path $Root 'data'
$LevelDir = Join-Path $Data 'levels\paintown\levels'
$ScriptLine = '  (script python "levels/paintown/rpg.py")'

$required = @(
    (Join-Path $Root 'All American Hustle.exe'),
    (Join-Path $Root 'SDL.dll'),
    (Join-Path $Root 'alleg42.dll'),
    (Join-Path $Data 'scripts\paintown.py'),
    (Join-Path $Data 'levels\paintown\rpg.py'),
    (Join-Path $Root 'rpg_mechanics\rpg_system.py')
)

$missing = @($required | Where-Object { -not (Test-Path -LiteralPath $_) })
if ($missing.Count -gt 0) {
    throw "Missing required files:`n$($missing -join "`n")"
}
if (-not (Test-Path -LiteralPath $LevelDir -PathType Container)) {
    throw "Missing level directory: $LevelDir"
}

$patched = 0
Get-ChildItem -LiteralPath $LevelDir -Filter '*.txt' -File | Sort-Object Name | ForEach-Object {
    $path = $_.FullName
    $text = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
    if ($text -notmatch [regex]::Escape('levels/paintown/rpg.py')) {
        $match = [regex]::Match($text, '\(level\s*\r?\n')
        if (-not $match.Success) {
            throw "Not a Paintown level: $path"
        }
        $insertAt = $match.Index + $match.Length
        $text = $text.Insert($insertAt, $ScriptLine + "`n")
        [System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))
        $patched++
    }
}

Write-Host "All-American Hustle ready. RPG script enabled in $patched level(s)."
exit 0
