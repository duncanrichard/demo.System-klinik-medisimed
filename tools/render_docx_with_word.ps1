param(
    [Parameter(Mandatory = $true)][string]$InputDocx,
    [Parameter(Mandatory = $true)][string]$OutputPdf
)

$wordApp = $null
$document = $null

try {
    $wordApp = New-Object -ComObject Word.Application
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $document = $wordApp.Documents.Open($InputDocx, $false, $true)
    $document.ExportAsFixedFormat($OutputPdf, 17)
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
    }
    if ($null -ne $wordApp) {
        $wordApp.Quit()
    }
}
