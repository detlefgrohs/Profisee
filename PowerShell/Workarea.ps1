param($Environment = "Local")

$Global:ExecutionDirectory = Split-Path $MyInvocation.MyCommand.Path -Parent

. "$Global:ExecutionDirectory\ProfiseeRESTful.ps1"
. "$Global:ExecutionDirectory\Common-Functions.ps1"

$Global:Settings = ((Get-Content "$executionDirectory\settings.json") | ConvertFrom-Json)

$restfulAPI = [ProfiseeRestful]::new($Environment);

$options = [GetOptions]::new();
$records = $restfulAPI.GetRecords("Test", $options)

$records | ForEach-Object {
    Write-Host "Found $($_.Code) [$($_.Name)]"

}