$path_colorls    = "$HOME/.config/colorls/"
$path_lsd        = "$HOME/AppData/Roaming/lsd/"
$path_PowerShell = "$HOME/Documents/PowerShell/"
$path_neofetch   = "$HOME/.config/neofetch/"
$path_oh_my_posh = "$HOME/.config/oh-my-posh/"
$path_hyfetch    = "$HOME/.config/hyfetch.json"
$path_bat        = "$HOME/AppData/Roaming/bat/"

rclone sync --create-empty-src-dirs -v $path_colorls    ./colorls/   
rclone sync --create-empty-src-dirs -v $path_lsd        ./lsd/       
rclone sync --create-empty-src-dirs -v $path_PowerShell ./PowerShell/ --exclude 'Modules/' --exclude 'Scripts/'
rclone sync --create-empty-src-dirs -v $path_neofetch   ./neofetch/  
rclone sync --create-empty-src-dirs -v $path_oh_my_posh ./oh-my-posh/
rclone copyto                       -v $path_hyfetch    ./hyfetch.json
rclone sync --create-empty-src-dirs -v $path_bat        ./bat/       
