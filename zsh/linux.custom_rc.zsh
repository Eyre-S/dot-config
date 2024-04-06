#!/bin/zsh

#=== bat (cat)
alias cat='bat'
#=== lsd
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

#=== zoxide (cd)
# zoxide must init after compinit is called
eval "$(zoxide init zsh)"
alias cd='z'
