#!/usr/bin/env pwsh
<#!
    PowerShell port of /b/happyBeeps for Windows 10+.
    Plays a cheerful ascending/descending sequence using Console.Beep.
!>

$freqs = @(784, 988, 1319)
$durationMs = 150
$shortPause = 200
$longPause = 400
$repeat = 3

for ($cycle = 0; $cycle -lt $repeat; $cycle++) {
    foreach ($freq in $freqs) {
        [Console]::Beep($freq, $durationMs)
        Start-Sleep -Milliseconds $shortPause
    }

    for ($i = $freqs.Count - 2; $i -ge 0; $i--) {
        [Console]::Beep($freqs[$i], $durationMs)
        Start-Sleep -Milliseconds $longPause
    }
}
