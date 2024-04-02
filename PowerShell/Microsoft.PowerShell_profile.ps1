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

# =============================================================================
#
# Utility functions for zoxide.
#

# Call zoxide binary, returning the output as UTF-8.
function global:__zoxide_bin {
    $encoding = [Console]::OutputEncoding
    try {
        [Console]::OutputEncoding = [System.Text.Utf8Encoding]::new()
        $result = zoxide @args
        return $result
    } finally {
        [Console]::OutputEncoding = $encoding
    }
}

# pwd based on zoxide's format.
function global:__zoxide_pwd {
    $cwd = Get-Location
    if ($cwd.Provider.Name -eq "FileSystem") {
        $cwd.ProviderPath
    }
}

# cd + custom logic based on the value of _ZO_ECHO.
function global:__zoxide_cd($dir, $literal) {
    $dir = if ($literal) {
        Set-Location -LiteralPath $dir -Passthru -ErrorAction Stop
    } else {
        if ($dir -eq '-' -and ($PSVersionTable.PSVersion -lt 6.1)) {
            Write-Error "cd - is not supported below PowerShell 6.1. Please upgrade your version of PowerShell."
        }
        elseif ($dir -eq '+' -and ($PSVersionTable.PSVersion -lt 6.2)) {
            Write-Error "cd + is not supported below PowerShell 6.2. Please upgrade your version of PowerShell."
        }
        else {
            Set-Location -Path $dir -Passthru -ErrorAction Stop
        }
    }
}

# =============================================================================
#
# Hook configuration for zoxide.
#

# Hook to add new entries to the database.
$global:__zoxide_oldpwd = __zoxide_pwd
function global:__zoxide_hook {
    $result = __zoxide_pwd
    if ($result -ne $global:__zoxide_oldpwd) {
        if ($null -ne $result) {
            zoxide add -- $result
        }
        $global:__zoxide_oldpwd = $result
    }
}

# Initialize hook.
$global:__zoxide_hooked = (Get-Variable __zoxide_hooked -ErrorAction SilentlyContinue -ValueOnly)
if ($global:__zoxide_hooked -ne 1) {
    $global:__zoxide_hooked = 1
    $global:__zoxide_prompt_old = $function:prompt

    function global:prompt {
        if ($null -ne $__zoxide_prompt_old) {
            & $__zoxide_prompt_old
        }
        $null = __zoxide_hook
    }
}

# =============================================================================
#
# When using zoxide with --no-cmd, alias these internal functions as desired.
#

# Jump to a directory using only keywords.
function global:__zoxide_z {
    if ($args.Length -eq 0) {
        __zoxide_cd ~ $true
    }
    elseif ($args.Length -eq 1 -and ($args[0] -eq '-' -or $args[0] -eq '+')) {
        __zoxide_cd $args[0] $false
    }
    elseif ($args.Length -eq 1 -and (Test-Path $args[0] -PathType Container)) {
        __zoxide_cd $args[0] $true
    }
    else {
        $result = __zoxide_pwd
        if ($null -ne $result) {
            $result = __zoxide_bin query --exclude $result -- @args
        }
        else {
            $result = __zoxide_bin query -- @args
        }
        if ($LASTEXITCODE -eq 0) {
            __zoxide_cd $result $true
        }
    }
}

# Jump to a directory using interactive search.
function global:__zoxide_zi {
    $result = __zoxide_bin query -i -- @args
    if ($LASTEXITCODE -eq 0) {
        __zoxide_cd $result $true
    }
}

# =============================================================================
#
# Commands for zoxide. Disable these using --no-cmd.
#

Set-Alias -Name z -Value __zoxide_z -Option AllScope -Scope Global -Force
Set-Alias -Name zi -Value __zoxide_zi -Option AllScope -Scope Global -Force
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
