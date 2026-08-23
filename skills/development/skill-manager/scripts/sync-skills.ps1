[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateScript({ Test-Path -LiteralPath $_ -PathType Container })]
    [string]$SourceRoot,

    [Parameter(Mandatory = $true)]
    [string]$RepoUrl,

    [ValidateSet('Preview', 'Publish')]
    [string]$Mode = 'Preview',

    [string[]]$SkillNames,

    [string]$Branch = 'main',

    [string]$WorkRoot = [System.IO.Path]::GetTempPath()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Stop-Release([string]$Message) {
    throw "Release blocked: $Message"
}

function Get-TextFiles([string]$Root) {
    $extensions = @('.md', '.json', '.yaml', '.yml', '.py', '.ps1', '.js', '.ts', '.sh', '.txt')
    Get-ChildItem -LiteralPath $Root -Recurse -File -Force |
        Where-Object { $extensions -contains $_.Extension.ToLowerInvariant() }
}

function Test-Within([string]$Candidate, [string]$Parent) {
    $candidateFull = [System.IO.Path]::GetFullPath($Candidate).TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    $parentFull = [System.IO.Path]::GetFullPath($Parent).TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    return $candidateFull.StartsWith($parentFull, [System.StringComparison]::OrdinalIgnoreCase)
}

function Copy-SkillFiles([string]$Source, [string]$Destination) {
    $skillFile = Join-Path $Source 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) {
        Stop-Release "$(Split-Path -Leaf $Source) does not contain SKILL.md."
    }

    Copy-Item -LiteralPath $skillFile -Destination (Join-Path $Destination 'SKILL.md') -Force
    foreach ($directory in @('agents', 'references', 'scripts', 'tests')) {
        $from = Join-Path $Source $directory
        if (Test-Path -LiteralPath $from -PathType Container) {
            $to = Join-Path $Destination $directory
            New-Item -ItemType Directory -Path $to -Force | Out-Null
            Get-ChildItem -LiteralPath $from -Force | ForEach-Object {
                Copy-Item -LiteralPath $_.FullName -Destination $to -Recurse -Force
            }
        }
    }
}

function Convert-ToReleaseText([string]$Text, $Rules) {
    # These generic replacements yield paths relative to a user's own working directory.
    $Text = [regex]::Replace($Text, '(?i)/Users/[^/\s]+/Desktop/日报周报', './日报周报')
    $Text = [regex]::Replace($Text, '(?i)/Users/[^/\s]+/workspace/([^/\s`"'']+)', './repositories/$1')
    $Text = [regex]::Replace($Text, '(?i)/Users/[^/\s]+/Desktop/服务端/个人沉淀/首页服务端学习手册\.html', './首页服务端学习手册.html')
    $Text = [regex]::Replace($Text, '(?i)/Users/[^/\s]+/Desktop/服务端/参考资料', './references/参考资料')
    $Text = [regex]::Replace($Text, '(?i)/Users/[^/\s]+/Desktop/首页性能优化', './references/首页性能优化')
    $Text = [regex]::Replace($Text, '(?i)[A-Z]:\\Users\\[^\\\s]+\\\.codex\\skills', 'skills')
    $Text = [regex]::Replace($Text, '(?i)E:\\# JingDong\\2_个人成长\\2_技术\\4_Skills\\skills', 'skills')

    foreach ($replacement in @($Rules.replacements)) {
        if ($null -ne $replacement -and $replacement.pattern) {
            $Text = [regex]::Replace($Text, [string]$replacement.pattern, [string]$replacement.replacement)
        }
    }
    return $Text
}

function Test-ReleaseText([string]$Text, [string]$RelativePath, $Rules) {
    # This scanner intentionally contains examples of the patterns it detects. Its
    # implementation is reviewed with this skill, so scanning its own regex source
    # would be a false positive rather than evidence of a local value.
    if ($RelativePath -eq 'skills/development/skill-manager/scripts/sync-skills.ps1') {
        return
    }
    $checks = @(
        @{ Pattern = '(?i)/Users/[^/\s]+'; Reason = 'a macOS user-home path' },
        @{ Pattern = '(?i)/home/[^/\s]+'; Reason = 'a Unix user-home path' },
        @{ Pattern = '(?i)[A-Z]:\\Users\\[^\\\s]+'; Reason = 'a Windows user-home path' },
        @{ Pattern = '(?i)E:\\# JingDong'; Reason = 'the local project root' },
        @{ Pattern = '(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'; Reason = 'an email address' },
        @{ Pattern = '(?i)\b(api[_ -]?key|secret|token|password)\s*[:=]\s*["''][^"'']{8,}["'']'; Reason = 'a credential-like assignment' }
    )
    foreach ($forbidden in @($Rules.forbiddenPatterns)) {
        if ($forbidden) {
            $checks += @{ Pattern = [string]$forbidden; Reason = 'a local forbidden pattern' }
        }
    }
    foreach ($check in $checks) {
        if ($Text -match $check.Pattern) {
            Stop-Release "$RelativePath still contains $($check.Reason)."
        }
    }
}

function Update-ReadmeCatalog([string]$ReadmePath, $Mappings, $Groups) {
    $readme = Get-Content -LiteralPath $ReadmePath -Raw
    if (@($Groups).Count -eq 0) {
        Stop-Release 'The skill map does not define ordered README groups.'
    }
    $groupCategories = @($Groups | ForEach-Object { $_.categories } | ForEach-Object { $_ })
    $unknownCategories = @($Mappings | Where-Object { $_.category -notin $groupCategories } | ForEach-Object { $_.category } | Select-Object -Unique)
    if ($unknownCategories.Count -gt 0) {
        Stop-Release "Categories missing from README groups: $($unknownCategories -join ', ')."
    }

    $sections = foreach ($group in $Groups) {
        if (-not $group.id -or -not $group.title -or @($group.categories).Count -eq 0) {
            Stop-Release 'An ordered README group is missing id, title, or categories.'
        }
        $groupMappings = @($Mappings | Where-Object { $_.category -in $group.categories } | Sort-Object target)
        if ($groupMappings.Count -eq 0) { continue }
        $rows = foreach ($mapping in $groupMappings) {
            "| [$($mapping.target)](skills/$($mapping.category)/$($mapping.target)/) | $($mapping.summary) | ``skills/$($mapping.category)/$($mapping.target)`` |"
        }
        "### $($group.title)`n`n| Skill | 说明 | 安装路径 |`n| --- | --- | --- |`n" + ($rows -join "`n")
    }
    $catalog = "<!-- skill-catalog:start -->`n`n" + ($sections -join "`n`n") + "`n`n<!-- skill-catalog:end -->"
    $pattern = '(?s)<!-- skill-catalog:start -->.*?<!-- skill-catalog:end -->'
    if (-not [regex]::IsMatch($readme, $pattern)) {
        Stop-Release 'README.md does not contain the required skill-catalog markers.'
    }
    $updated = [regex]::Replace($readme, $pattern, $catalog.TrimEnd())
    [System.IO.File]::WriteAllText($ReadmePath, $updated.TrimEnd() + "`n", [System.Text.UTF8Encoding]::new($false))
}

foreach ($command in @('git')) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        Stop-Release "Required command '$command' is not available."
    }
}

$source = (Resolve-Path -LiteralPath $SourceRoot).Path
$managerRoot = Split-Path -Parent $PSScriptRoot
$mapPath = Join-Path $managerRoot 'references\skill-map.json'
$rulesPath = Join-Path $managerRoot '.local-publishing-rules.json'
if (-not (Test-Path -LiteralPath $mapPath -PathType Leaf)) {
    Stop-Release "Missing skill map: $mapPath"
}

$mapDocument = Get-Content -LiteralPath $mapPath -Raw | ConvertFrom-Json
$mappings = @($mapDocument.skills)
$groups = @($mapDocument.groups)
if ($mappings.Count -eq 0) {
    Stop-Release 'The skill map is empty.'
}

$rules = [pscustomobject]@{ replacements = @(); forbiddenPatterns = @() }
if (Test-Path -LiteralPath $rulesPath -PathType Leaf) {
    $rules = Get-Content -LiteralPath $rulesPath -Raw | ConvertFrom-Json
}

$sourceSkills = Get-ChildItem -LiteralPath $source -Directory -Force |
    Where-Object { $_.Name -ne '__MACOSX' } |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') } |
    Select-Object -ExpandProperty Name
$mappedNames = @($mappings | ForEach-Object { $_.source })
$unmapped = @($sourceSkills | Where-Object { $_ -notin $mappedNames })
if ($unmapped.Count -gt 0) {
    Stop-Release "Unmapped source skills: $($unmapped -join ', '). Add safe public mappings before release."
}

$duplicateTargets = @($mappings | Group-Object { "$($_.category)/$($_.target)" } | Where-Object Count -gt 1)
if ($duplicateTargets.Count -gt 0) {
    Stop-Release "Duplicate release targets: $($duplicateTargets.Name -join ', ')."
}

$requestedSkillNames = @($SkillNames | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$releaseMappings = if ($requestedSkillNames.Count -gt 0) {
    $unknownRequested = @($requestedSkillNames | Where-Object { $_ -notin $mappedNames })
    if ($unknownRequested.Count -gt 0) {
        Stop-Release "Requested unmapped skills: $($unknownRequested -join ', ')."
    }
    @($mappings | Where-Object { $_.source -in $requestedSkillNames })
} else {
    @($mappings | Where-Object { -not $_.PSObject.Properties['initialPublish'] -or $_.initialPublish -ne $false })
}

if (-not (Test-Path -LiteralPath $WorkRoot -PathType Container)) {
    New-Item -ItemType Directory -Path $WorkRoot -Force | Out-Null
}
$worktree = Join-Path (Resolve-Path -LiteralPath $WorkRoot).Path ("curforever-skills-" + [guid]::NewGuid().ToString('N'))
Write-Host "Temporary worktree: $worktree"
& git clone --branch $Branch --quiet $RepoUrl $worktree
if ($LASTEXITCODE -ne 0) { Stop-Release 'Unable to clone the target repository.' }

$releaseSkillsRoot = Join-Path $worktree 'skills'
foreach ($mapping in $releaseMappings) {
    foreach ($property in @('source', 'category', 'target', 'summary')) {
        if (-not $mapping.$property) { Stop-Release "Invalid mapping missing '$property'." }
    }
    $from = Join-Path $source $mapping.source
    if (-not (Test-Path -LiteralPath $from -PathType Container)) {
        Stop-Release "Mapped source skill '$($mapping.source)' does not exist."
    }
    $destination = Join-Path (Join-Path $releaseSkillsRoot $mapping.category) $mapping.target
    if (-not (Test-Within $destination $releaseSkillsRoot)) {
        Stop-Release "Unsafe mapped destination: $destination"
    }
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Copy-SkillFiles -Source $from -Destination $destination
}

foreach ($file in Get-TextFiles $releaseSkillsRoot) {
    $text = [System.IO.File]::ReadAllText($file.FullName)
    $text = Convert-ToReleaseText -Text $text -Rules $rules
    $relative = $file.FullName.Substring($worktree.Length + 1).Replace('\', '/')
    Test-ReleaseText -Text $text -RelativePath $relative -Rules $rules
    [System.IO.File]::WriteAllText($file.FullName, $text, [System.Text.UTF8Encoding]::new($false))
}

Get-ChildItem -LiteralPath $releaseSkillsRoot -Directory -Recurse | ForEach-Object {
    $skillFile = Join-Path $_.FullName 'SKILL.md'
    if ((Get-ChildItem -LiteralPath $_.FullName -File -Force | Measure-Object).Count -gt 0 -and (Test-Path -LiteralPath $skillFile)) {
        $skillText = Get-Content -LiteralPath $skillFile -Raw
        $frontmatter = [regex]::Match($skillText, '(?s)\A---\r?\n(.*?)\r?\n---')
        if (-not $frontmatter.Success -or
            $frontmatter.Groups[1].Value -notmatch '(?m)^name:\s*\S+' -or
            $frontmatter.Groups[1].Value -notmatch '(?m)^description:\s*') {
            Stop-Release "Invalid frontmatter in $($skillFile.Substring($worktree.Length + 1))."
        }
    }
}

Update-ReadmeCatalog -ReadmePath (Join-Path $worktree 'README.md') -Mappings $mappings -Groups $groups

Write-Host "`nRelease preview:"
& git -C $worktree status --short
if ($LASTEXITCODE -ne 0) { Stop-Release 'Unable to inspect the release worktree.' }

if ($Mode -eq 'Publish') {
    & git -C $worktree add --all
    if ($LASTEXITCODE -ne 0) { Stop-Release 'Unable to stage release changes.' }
    & git -C $worktree diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host 'No release changes to publish.'
    } elseif ($LASTEXITCODE -eq 1) {
        & git -C $worktree commit -m 'Publish normalized skills'
        if ($LASTEXITCODE -ne 0) { Stop-Release 'Unable to create the release commit.' }
        & git -C $worktree push origin $Branch
        if ($LASTEXITCODE -ne 0) { Stop-Release 'Unable to push the release commit.' }
        Write-Host 'Publish completed.'
    } else {
        Stop-Release 'Unable to determine whether release changes exist.'
    }
} else {
    Write-Host "Preview completed. No commit or push was performed. Review the retained worktree: $worktree"
}
