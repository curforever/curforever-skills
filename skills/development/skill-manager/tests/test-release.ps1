$ErrorActionPreference = 'Stop'
$scriptFile = Join-Path $PSScriptRoot '../scripts/sync-skills.ps1'
$parseErrors = $null
$tokens = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    (Resolve-Path -LiteralPath $scriptFile), [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw ($parseErrors | Out-String) }
foreach ($definition in $ast.FindAll({ param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst]
}, $false)) {
    . ([scriptblock]::Create($definition.Extent.Text))
}

function Assert-True($Condition, $Message) {
    if (-not $Condition) { throw $Message }
}

$fixture = Join-Path ([System.IO.Path]::GetTempPath()) ('skill-release-test-' + [guid]::NewGuid().ToString('N'))
$source = Join-Path $fixture 'source'
$destination = Join-Path $fixture 'output/skills/design/demo'
New-Item -ItemType Directory -Path $source, $destination -Force | Out-Null
try {
    foreach ($relative in @('SKILL.md', 'LICENSE', 'NOTICE.md', 'UPSTREAM.json', 'assets/template.txt', 'reference/layout.md', 'templates/task.md', 'scripts/tool.py')) {
        $path = Join-Path $source $relative
        New-Item -ItemType Directory -Path (Split-Path -Parent $path) -Force | Out-Null
        [IO.File]::WriteAllText($path, "public fixture`n")
    }
    foreach ($relative in @('.env', '.env.local', '.local-publishing-rules.json', 'scripts/__pycache__/tool.pyc', 'node_modules/package/file.js', '__MACOSX/._SKILL.md')) {
        $path = Join-Path $source $relative
        New-Item -ItemType Directory -Path (Split-Path -Parent $path) -Force | Out-Null
        [IO.File]::WriteAllText($path, 'local-only fixture')
    }
    Copy-SkillFiles $source $destination
    foreach ($relative in @('LICENSE', 'NOTICE.md', 'UPSTREAM.json', 'assets/template.txt', 'reference/layout.md', 'templates/task.md', 'scripts/tool.py')) {
        Assert-True (Test-Path -LiteralPath (Join-Path $destination $relative)) "Missing reusable resource: $relative"
    }
    foreach ($relative in @('.env', '.env.local', '.local-publishing-rules.json', 'scripts/__pycache__/tool.pyc', 'node_modules/package/file.js', '__MACOSX/._SKILL.md')) {
        Assert-True (-not (Test-Path -LiteralPath (Join-Path $destination $relative))) "Leaked excluded resource: $relative"
    }

    $rules = [pscustomobject]@{ replacements = @(); forbiddenPatterns = @('private-fixture-value') }
    $blocked = $false
    try { Test-ReleaseText 'private-fixture-value' 'example.md' $rules } catch { $blocked = $true }
    Assert-True $blocked 'Configured forbidden value was accepted'
    $blocked = $false
    $sampleHome = '/' + 'Users' + '/example-user/material.md'
    try { Test-ReleaseText $sampleHome 'example.md' $rules } catch { $blocked = $true }
    Assert-True $blocked 'User home path was accepted'
    Test-ReleaseText ([IO.File]::ReadAllText((Resolve-Path -LiteralPath $scriptFile))) 'scripts/sync-skills.ps1' $rules
    $textFiles = @(Get-TextFiles $destination)
    Assert-True (@($textFiles | Where-Object Name -eq 'LICENSE').Count -eq 1) 'License file was not scanned'

    $readme = Join-Path $fixture 'output/README.md'
    [IO.File]::WriteAllText($readme, "# Example`n`n<!-- skill-catalog:start -->`n<!-- skill-catalog:end -->`n")
    $mappings = @(
        [pscustomobject]@{ category = 'design'; target = 'demo'; summary = 'Available' },
        [pscustomobject]@{ category = 'design'; target = 'absent'; summary = 'Not released' }
    )
    $groups = @([pscustomobject]@{ id = 'design'; title = 'Design'; categories = @('design') })
    Update-ReadmeCatalog $readme $mappings $groups
    $result = [IO.File]::ReadAllText($readme)
    Assert-True ($result.Contains('skills/design/demo')) 'Released skill missing from catalog'
    Assert-True (-not $result.Contains('absent')) 'Catalog advertises an unpublished skill'
    Write-Output 'PASS: resource preservation, local-file exclusion, forbidden values, self-scan, license scanning, selective README catalog.'
} finally {
    # Verify the generated fixture root before recursive cleanup.
    $resolvedFixture = [IO.Path]::GetFullPath($fixture)
    $resolvedTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    if (-not $resolvedFixture.StartsWith($resolvedTemp, [StringComparison]::OrdinalIgnoreCase) -or
        (Split-Path -Leaf $resolvedFixture) -notlike 'skill-release-test-*') {
        throw 'Refusing cleanup outside the generated temporary fixture'
    }
    Remove-Item -LiteralPath $resolvedFixture -Recurse -Force
}
