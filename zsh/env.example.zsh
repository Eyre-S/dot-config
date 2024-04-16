#!/bin/zsh

#--- System Environments ---#

# export MANPATH="/usr/local/man:$MANPATH"

#- You may need to manually set your language environment
# export LANG=en_US.UTF-8

#- Compilation flags
# export ARCHFLAGS="-arch x86_64"

#--- Editor (for normal system local/remote) ---#
if [[ -n $SSH_CONNECTION ]]; then
  export EDITOR='code'
  export POPUP_EDIT='code -n -w'
else
  export EDITOR='vim'
  export POPUP_EDIT='vim'
fi
#--- Editor: EMacs as Code (for termux only) ---#
alias vim='nvim'
export PATH="$PATH:$HOME/.config/doom/bin"
alias code='emacs'
export EDITOR='code'
export POPUP_EDIT='code'

#--- Environment Variables ---#

# System Mounts
export windows="/mnt/c"
export data="/mnt/s"
export external="/storage/54D5-A5C0"
# Home Configs
export profile="$HOME/.zshrc"
export config="$HOME/.config"
# Workspaces
export ws="$HOME/documents/workspaces"
export tests="$data/__test"
