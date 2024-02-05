$path_colorls    = "$HOME/.config/colorls/"
$path_lsd        = "$HOME/AppData/Roaming/lsd/"
$path_PowerShell = "$HOME/Documents/PowerShell/"
$path_neofetch   = "$HOME/.config/neofetch/"
$path_oh_my_posh = "$HOME/.config/oh-my-posh/"
$path_hyfetch    = "$HOME/.config/hyfetch.json"
$path_bat        = "$HOME/AppData/Roaming/bat/"

rclone sync --create-empty-src-dirs -v ./colorls/     $path_colorls   
rclone sync --create-empty-src-dirs -v ./lsd/         $path_lsd       
rclone sync --create-empty-src-dirs -v ./PowerShell/  $path_PowerShell --exclude 'Modules/' --exclude 'Scripts/'
rclone sync --create-empty-src-dirs -v ./neofetch/    $path_neofetch  
rclone sync --create-empty-src-dirs -v ./oh-my-posh/  $path_oh_my_posh
rclone copyto                       -v ./hyfetch.json $path_hyfetch   
rclone sync --create-empty-src-dirs -v ./bat/         $path_bat       
