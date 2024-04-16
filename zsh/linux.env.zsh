#!/bin/zsh

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
if [[ -n $SSH_CONNECTION ]]; then
  export EDITOR='code'
else
  export EDITOR='vim'
fi

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

# System Related Path Variables
export profile="$HOME/.zshrc"
export config="$HOME/.config"
# Workspaces
export ws="$HOME/documents/worksapce"
export tests="$HOME/documents/__test"
