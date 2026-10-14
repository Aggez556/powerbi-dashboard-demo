Add-Type -AssemblyName System.Drawing
$dest = Join-Path $PSScriptRoot '../powerbi-ledningsrapport/LedningsrapportUtanScroll.Report/StaticResources/RegisteredResources'
foreach ($ink in @('0F3163','FFFFFF','8A97A8')) {
 foreach ($kind in @('home','overview','sales','customers','budget','projects')) {
  $bmp = New-Object System.Drawing.Bitmap 96,96
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = 'AntiAlias'
  $g.ScaleTransform(4,4)
  $pen = New-Object System.Drawing.Pen ([System.Drawing.ColorTranslator]::FromHtml("#$ink")),1.7
  $pen.StartCap = 'Round'; $pen.EndCap = 'Round'; $pen.LineJoin = 'Round'
  function Line($a,$b,$c,$d) { $g.DrawLine($pen,[single]$a,[single]$b,[single]$c,[single]$d) }
  switch ($kind) {
   home { Line 19 12 5 12; Line 5 12 11 6; Line 5 12 11 18 }
   overview { $g.DrawRectangle($pen,4,12,4,8); $g.DrawRectangle($pen,10,8,4,12); $g.DrawRectangle($pen,16,4,4,16) }
   sales { Line 4 4 4 20; Line 4 20 20 20; Line 7 15 11 10; Line 11 10 15 13; Line 15 13 20 6; Line 15 6 20 6; Line 20 6 20 11 }
   customers { $g.DrawEllipse($pen,6,5,6,6); $g.DrawArc($pen,3,12,12,12,180,180); Line 3 18 3 20; Line 15 18 15 20; $g.DrawArc($pen,14,5,6,6,270,180); $g.DrawArc($pen,15,14,6,8,270,90); Line 21 18 21 20 }
   budget { $g.DrawRectangle($pen,5,3,14,18); Line 8 7 16 7; Line 8 11 11 11; Line 13 11 16 11; Line 8 15 11 15; Line 13 15 16 15; Line 8 18 11 18; Line 13 18 16 18 }
   projects { $g.DrawRectangle($pen,3,5,18,16); Line 7 3 7 7; Line 17 3 17 7; Line 3 10 21 10; Line 7 14 10 14; Line 14 14 17 14; Line 7 18 10 18 }
  }
  $bmp.Save((Join-Path $dest "navigation-$kind-$ink.png"),[System.Drawing.Imaging.ImageFormat]::Png)
  $pen.Dispose(); $g.Dispose(); $bmp.Dispose()
 }
}
