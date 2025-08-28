

function Process-InBatches {
    param ($Array, $BatchSize = 250, [ScriptBlock] $ScriptBlock)

    $offset = $batchNumber = 0;
    do {
        $subArray = $Array | SELECT -First $BatchSize -Skip $offset

        if ($subArray.Length -gt 0) {
            Invoke-Command -ScriptBlock $ScriptBlock -ArgumentList $subArray,$batchNumber
            $offset += $subArray.Length;
            $batchNumber += 1;
        }
    } while ($subArray -gt 0);
}

function Process-InPages {
    param(
        [ScriptBlock] $GetPageScriptBlock,
        [ScriptBlock] $ProcessPageScriptBlock
    )

    $pageNumber = 1;
    $array = @();
    do {
        $pageArray = Invoke-Command -ScriptBlock $GetPageScriptBlock -ArgumentList $pageNumber
        $pageNumber += 1;

        if ($pageArray.Length -gt 0) { $array += (Invoke-Command -ScriptBlock $ProcessPageScriptBlock -ArgumentList (,$pageArray)); }
    } while ($pageArray.Length -gt 0);
    return (,$array);
}

function Increment-Count {
    param($Dictionary, $Key)

    if ($Dictionary.ContainsKey($Key)) {
        $Dictionary[$Key] += 1;
    } else {
        $Dictionary.Add($Key, 1);
    }
}
