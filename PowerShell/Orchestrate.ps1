param($Name = "Matching")

$Global:ExecutionDirectory = Split-Path $MyInvocation.MyCommand.Path -Parent

. "$Global:ExecutionDirectory\ProfiseeRESTful.ps1"
. "$Global:ExecutionDirectory\Common-Functions.ps1"
. "$Global:ExecutionDirectory\OrchestrationRunner.ps1"

$Global:Settings = ((Get-Content "$executionDirectory\settings.json") | ConvertFrom-Json)

$api = [ProfiseeRestful]::new("Local");

$orchestrationRunner = [OrchestrationRunner]::new($api);

$response = $orchestrationRunner.Orchestrate($Name);
$response