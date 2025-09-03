param($Environment = "Local")

$Global:ExecutionDirectory = Split-Path $MyInvocation.MyCommand.Path -Parent

. "$Global:ExecutionDirectory\ProfiseeRESTful.ps1"
. "$Global:ExecutionDirectory\Common-Functions.ps1"

$Global:Settings = ((Get-Content "$executionDirectory\settings.json") | ConvertFrom-Json)

$restfulAPI = [ProfiseeRestful]::new($Environment);



# $restfulAPI.RunConnectBatch("SQL Server [Test] Export [dbo].[tbl_Test]", "", @( ))

# $restfulAPI.RunConnectBatch("SQL Server [Test] Export [dbo].[tbl_Test]", "", @( "*Test" ))

$restfulAPI.RunConnectBatch("SQL Server [Test] Export [dbo].[tbl_Test]", 'CHANGED( [Test].[Test] )', @( ))



return

Write-Host "Clearing fields in [Test] entity"

$options = [GetOptions]::new();
$records = $restfulAPI.GetRecords("Test", $options)

$updatedRecords = @()
$records | ForEach-Object {
    $updatedRecords += @{
        Code = $_.Code
        Test = $null
        Test2 = $null
        DateAttribute = $null
        DateTimeAttribute = $null
        DBAAttribute = $null
        NumberAttribute = $null
    }
}
$restfulAPI.MergeRecords("Test", $updatedRecords)