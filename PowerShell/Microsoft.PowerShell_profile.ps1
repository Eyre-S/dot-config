##
## PowerShell®
##    startup environment settings
##  user.sukazyo
## 
######

<# =================
 -   user variable
 #>
. "$HOME/OneDrive/sukazyo-pin/environment.ps1"

$ws = "S:\workspace"
$tests = "S:\__test"

$gradlearchive = "S:\Document\gradle-builds"


<# =================
 -   Alias
 #>

function profile { . $PROFILE }
function source { profile }
function nexplorer { explorer . }

function whereis {
	Get-Command $args | Format-List
}

function dos2unix { & "C:/Program Files/Git/usr/bin/dos2unix" $args }

function unix2dos { & "C:/Program Files/Git/usr/bin/unix2dos" $args }

<# == batcat == #>
Set-Alias -Name cat -Value bat

<# == lsd (colorls before) == #>
#source $(dirname $(gem which colorls))/tab_complete.sh
function cols {
	lsd $args
}
function crls {
	cols @args
}
function ccls {
	#theres no git (--gs) support due to slow performance and bugs on Windows
	crls @args
}
function cl {
	$args_new = @("-lA") + $args
	ccls @args_new
}
function cll {
	$args_new = @("-l") + $args
	ccls @args_new
}
function cla {
	$args_new = @("-la") + $args
	ccls @args_new
}
function lc {
	ccls @args
}
Set-Alias -Name ls -Value lc # override system ls
function l { cl @args }
function ll { cll @args }
function la { cla @args }
function lgg {
	$args_new = @("--tree") + $args
	ccls @args_new
}

<# == zoxide cd == #>
Invoke-Expression (& { (zoxide init powershell | Out-String) })
Remove-Alias cd
Set-Alias -Name cd -Value z
Set-Alias -Name cdi -Value zi

<# =================
 -   TOOLCHAILS
 #>

<# === Chocolatey === #>

# $ChocolateyProfile = "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
# if (Test-Path($ChocolateyProfile)) {
# 	Import-Module "$ChocolateyProfile"
# }

<# === Python Versions managered by hatch === #>

$pythons = "$HOME/AppData/Local/hatch/pythons"

function pys () {
    $version, $args_pass = $args
    $py_path = "$pythons/$version/python"
    echo "using Python version : $version"
    echo "using Python path : $py_path"
    & "$py_path/python.exe" $args_pass
}

function pysm () {
    hatch python $args
}

<# === Oh-My-Posh === #>

# $USE_POSH_THEME = "catppuccin"
# $USE_POSH_THEME = "chips"
# $USE_POSH_THEME = "emodipt-extend" # original
# $USE_POSH_THEME = "hunk"
# $USE_POSH_THEME = "multiverse-neon"
# $USE_POSH_THEME = "negligible"
# $USE_POSH_THEME = "peru"
# $USE_POSH_THEME = "pure"
# $USE_POSH_THEME = "ys"
$USE_POSH_THEME = "sukazyo"

oh-my-posh init pwsh --config "$HOME\.config\oh-my-posh\$USE_POSH_THEME.omp.json" | Invoke-Expression
# oh-my-posh init pwsh --config "$env:POSH_THEMES_PATH\$USE_POSH_THEME.omp.json" | Invoke-Expression

<# === Others Auto Generated === #>

#34de4b3d-13a8-4540-b76d-b9e8d3851756 PowerToys CommandNotFound module
Import-Module "C:\Program Files\PowerToys\WinUI3Apps\..\WinGetCommandNotFound.psd1"
#34de4b3d-13a8-4540-b76d-b9e8d3851756
