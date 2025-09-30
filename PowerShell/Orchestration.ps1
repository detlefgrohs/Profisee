param(
    $Name = "Export",
    [switch]$bootstrap = $false,
    [switch]$test = $false,
    [switch]$whatif = $false
)

# This is the handler script for the Orchestration class that will handle the parameters and call the class methods

$Global:ExecutionDirectory = Split-Path $MyInvocation.MyCommand.Path -Parent

. "$Global:ExecutionDirectory\ProfiseeRESTful.ps1"
. "$Global:ExecutionDirectory\Common-Functions.ps1"
. "$Global:ExecutionDirectory\Orchestration-Class.ps1"

$Global:Settings = ((Get-Content "$executionDirectory\settings.json") | ConvertFrom-Json)

$orchestration_entity_name = $Global:Settings.OrchestrationEntityName

if ($Name -eq $null -and $bootstrap -eq $false -and $test -eq $false) {
    Write-Host "Please provide a Name parameter to run an orchestration, or use the -bootstrap or -test switches."
    exit 1
}

$profisee_url = $Global:Settings.ProfiseeUrl
$client_id = $Global:Settings.ClientId
# $verify_ssl = $Global:Settings.VerifySSL # Don't need this for the PowerShell Restful Operations

$api = [ProfiseeRestful]::new($profisee_url, $client_id);

if ($test) {
    $result = $api.GetEntities();
    if ($api.StatusCode -ne 200) {
        Write-Host "Failed to connect to Profisee API at '$($profisee_url)' with ClientID '$($client_id)'. StatusCode: $($api.StatusCode). Exiting."
        exit(1)
    } else {
        Write-Host "Successfully connected to Profisee API at '$($profisee_url)' with ClientID '$($client_id)'. StatusCode: $($api.StatusCode)."
        exit(0)
    }
}

if ($bootstrap) {
    [Orchestration]::Bootstrap($api, $orchestration_entity_name);
    exit(0)
}

$orchestration = [Orchestration]::new($api, $orchestration_entity_name);
$orchestration.what_if = $whatif;
$result = $orchestration.Orchestrate($Name);

$orchestration.MinLogLevel
$orchestration.ActivityPollingInterval

if ($result.Error -eq $true) {
    Write-Host "Orchestration '$($Name)' failed with error: $($result.Message)"
    exit(1)
} else {
    Write-Host "Orchestration '$($Name)' completed successfully."
    exit(0)
}
