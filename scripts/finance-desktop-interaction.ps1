param([int]$DesktopProcessId=9624,[ValidateSet('Kategori','Team','MonthOpen','InspectMonths','October','ClearSelection','SummaryKategori','SummaryLand')][string]$Action)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class FinanceInput { [DllImport("user32.dll")] public static extern bool SetProcessDPIAware(); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int n); [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y); [DllImport("user32.dll")] public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e); public static void Wheel(int d) { mouse_event(0x800,0,0,unchecked((uint)d),UIntPtr.Zero); } }'
[FinanceInput]::SetProcessDPIAware() | Out-Null
$root=[System.Windows.Automation.AutomationElement]::RootElement
$window=$root.FindAll([System.Windows.Automation.TreeScope]::Children,[System.Windows.Automation.Condition]::TrueCondition) | Where-Object {$_.Current.ProcessId -eq $DesktopProcessId -and $_.Current.Name -eq 'AubecoSalesFinance'} | Select-Object -First 1
if(-not $window){throw 'Report window not found'}
$handle=$window.Current.NativeWindowHandle
[FinanceInput]::ShowWindow($handle,9) | Out-Null
[FinanceInput]::SetForegroundWindow($handle) | Out-Null
Start-Sleep -Seconds 1
$window=[System.Windows.Automation.AutomationElement]::FromHandle($handle)
function FindControl([string]$name,$type){
 $condition=New-Object System.Windows.Automation.AndCondition ((New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::NameProperty,$name)),(New-Object System.Windows.Automation.PropertyCondition ([System.Windows.Automation.AutomationElement]::ControlTypeProperty,$type)))
 $control=$window.FindFirst([System.Windows.Automation.TreeScope]::Descendants,$condition)
 if(-not $control){throw "Control not found: $name"};return $control
}
function ClickControl($control,[switch]$Arrow){
 $rect=$control.Current.BoundingRectangle
 if($rect.IsEmpty -or $rect.X -lt 0 -or $rect.Y -lt 0){throw 'Control is not visible'}
 $targetX=if($Arrow){$rect.Right-8}else{$rect.X+$rect.Width/2}
 [FinanceInput]::SetCursorPos([int]$targetX,[int]($rect.Y+$rect.Height/2)) | Out-Null
 [FinanceInput]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
 [FinanceInput]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
 Start-Sleep -Seconds 2
}
if($Action -in @('Kategori','Team')){
 for($attempt=0;$attempt -lt 2;$attempt++){
  $control=FindControl $Action ([System.Windows.Automation.ControlType]::Button)
  $state=$control.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState
  if($state -eq [System.Windows.Automation.ToggleState]::On){break}
  Write-Output ("Click "+$Action+" at "+$control.Current.BoundingRectangle.ToString()+"; state "+$state)
  if($attempt -eq 0){$control.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Toggle();Start-Sleep -Seconds 1}
  $state=$control.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState
  if($state -ne [System.Windows.Automation.ToggleState]::On){ClickControl $control}
 }
 $control=FindControl $Action ([System.Windows.Automation.ControlType]::Button)
 $state=$control.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState
 if($state -ne [System.Windows.Automation.ToggleState]::On){throw 'Toggle did not change'}
 Write-Output "$Action toggle: On"
}
if($Action -eq 'MonthOpen'){
 $control=FindControl 'Månad' ([System.Windows.Automation.ControlType]::ComboBox)
 ClickControl $control -Arrow
}
if($Action -in @('SummaryKategori','SummaryLand')){
 $control=FindControl 'Gruppering' ([System.Windows.Automation.ControlType]::ComboBox)
 ClickControl $control -Arrow
 $value=if($Action -eq 'SummaryKategori'){'Kategori'}else{'Land'}
 $option=FindControl $value ([System.Windows.Automation.ControlType]::ListItem)
 $option.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
 Start-Sleep -Seconds 2
 $control=FindControl 'Gruppering' ([System.Windows.Automation.ControlType]::ComboBox)
 Write-Output ('Summary grouping: '+$control.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value)
}
if($Action -eq 'InspectMonths'){
 $controls=$window.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
 @($controls | Where-Object {$_.Current.Name -match 'oktober|Välj alla|Markera alla|Select all|januari'} | ForEach-Object {@{name=$_.Current.Name;type=$_.Current.ControlType.ProgrammaticName;bounds=$_.Current.BoundingRectangle.ToString();patterns=$_.GetSupportedPatterns().ProgrammaticName}}) | ConvertTo-Json -Depth 4
}
if($Action -eq 'October'){
 $controls=$window.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
 $control=$controls | Where-Object {$_.Current.Name -eq 'oktober' -and $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::ListItem} | Select-Object -First 1
 if(-not $control){
  $first=$controls | Where-Object {$_.Current.Name -eq 'januari' -and $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::ListItem} | Select-Object -First 1
  if(-not $first){throw 'Month list is not open'}
  $rect=$first.Current.BoundingRectangle
  [FinanceInput]::SetCursorPos([int]($rect.X+$rect.Width/2),[int]($rect.Y+$rect.Height/2)) | Out-Null
  [FinanceInput]::SetCursorPos([int]($rect.Right-3),[int]($rect.Y+110)) | Out-Null
  [FinanceInput]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
  [FinanceInput]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
  Start-Sleep -Seconds 1
  $control=FindControl 'oktober' ([System.Windows.Automation.ControlType]::ListItem)
 }
 $pattern=$control.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern)
 if($pattern.Current.ToggleState -ne [System.Windows.Automation.ToggleState]::On){$control.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()}
 Start-Sleep -Seconds 2
 $control=FindControl 'oktober' ([System.Windows.Automation.ControlType]::ListItem)
 Write-Output ('October state: '+$control.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Current.ToggleState)
 [System.Windows.Forms.SendKeys]::SendWait('{ESC}')
}
if($Action -eq 'ClearSelection','SummaryKategori','SummaryLand'){
 [System.Windows.Forms.SendKeys]::SendWait('{ESC}')
 Start-Sleep -Milliseconds 300
 [System.Windows.Forms.SendKeys]::SendWait('{ESC}')
}
[FinanceInput]::SetCursorPos(1400,150) | Out-Null
