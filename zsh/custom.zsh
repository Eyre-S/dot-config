#!/bin/zsh

#--- zshrc ---#

profile () {
	source $profile
}
profile-edit () {
	$POPUP_EDIT $profile
	profile
}

#--- custom CLI tools ---#

# Fast run a command in background with no log
bg () {
	eval "$@" &>/dev/null &disown
}

# Execute an AppImage and automaticly +x it
appimage() {
	chmod a+x $1
	$1
}

# Set file meta (like icons) in linux fs
file-set-icon () {
	gio set $1 metadata::custom-icon $2
}
file-rm-icon () {
	gio set -d $1 metadata::custom-icon
}
cat-desktop-ini () {
	cat "$1/desktop.ini"
}

# # where proxy
# proxy () {
# 	export http_proxy="http://127.0.0.1:7890"
# 	export https_proxy="http://127.0.0.1:7890"
# 	echo "HTTP Proxy on"
# }

# # where noproxy
# noproxy () {
# 	unset http_proxy
# 	unset https_proxy
# 	echo "HTTP Proxy off"
# }

#--- enhanced CLI tools aliases ---#

# cat is bat
alias cat='bat'
# ls is lsd
alias cols='lsd'
alias crls='cols'
alias ccls='crls -g'
alias cl='ccls -lA'
alias cll='ccls -l'
alias cla='ccls -la'
alias lc='ccls'
alias ls='lc'
alias l='cl'
alias ll='cll'
alias la='cla'
alias lgg='ccls --tree'
# cd is zoxide
# zoxide must init after compinit is called
eval "$(zoxide init zsh)"
alias cd='z'
# fuck
eval $(thefuck --alias)

#--- other toolchain alias ---#

# gcc c++ complier
alias gpp="g++"
alias gxx="g++"