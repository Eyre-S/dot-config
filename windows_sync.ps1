$path_colorls    = "~/.config/colorls/"
$path_lsd        = "~/AppData/Roaming/lsd/"
$path_PowerShell = "~/Documents/PowerShell/"
$path_neofetch   = "~/.config/neofetch/"
$path_oh_my_posh = "~/.config/oh-my-posh/"
$path_hyfetch    = "~/.config/hyfetch.json"
$path_bat        = "~/AppData/Roaming/bat/"

rsync -avh $path_colorls    ./colorls/   
rsync -avh $path_lsd        ./lsd/       
rsync -avh $path_PowerShell ./PowerShell/ --exclude 'Modules/' --exclude 'Scripts/'
rsync -avh $path_neofetch   ./neofetch/  
rsync -avh $path_oh_my_posh ./oh-my-posh/
rsync -avh $path_hyfetch    ./hyfetch.json
rsync -avh $path_bat        ./bat/        

rsync -avh ./colorls/     $path_colorls   
rsync -avh ./lsd/         $path_lsd       
rsync -avh ./PowerShell/  $path_PowerShell --exclude 'Modules/' --exclude 'Scripts/'
rsync -avh ./neofetch/    $path_neofetch  
rsync -avh ./oh-my-posh/  $path_oh_my_posh
rsync -avh ./hyfetch.json $path_hyfetch   
rsync -avh ./bat/         $path_bat       
