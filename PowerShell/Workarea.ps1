param($Environment = "Local")

$Global:ExecutionDirectory = Split-Path $MyInvocation.MyCommand.Path -Parent

. "$Global:ExecutionDirectory\ProfiseeRESTful.ps1"
. "$Global:ExecutionDirectory\Common-Functions.ps1"

$Global:Settings = ((Get-Content "$executionDirectory\settings.json") | ConvertFrom-Json)

$restfulAPI = [ProfiseeRestful]::new($Environment);

# $options = [GetOptions]::new();
# $records = $restfulAPI.GetRecords("Test", $options)

# $records | ForEach-Object {
#     Write-Host "Found $($_.Code) [$($_.Name)]"


    
# }


$json = '{ "Name" : "SQL Server [DQParent] Export [dbo].[tbl_DQParent]", "ActivityType" : "Database Export Activity" }'
$json

$object = $json | ConvertFrom-Json
$object


ConvertTo-Json -InputObject $object
