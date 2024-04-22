#!/bin/zsh

#--- System Environments ---#

# export MANPATH="/usr/local/man:$MANPATH"

#- You may need to manually set your language environment
# export LANG=en_US.UTF-8

#- Compilation flags
# export ARCHFLAGS="-arch x86_64"

#- Fix ^M when enter Enter
# stty icrnl

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

#--- messing configs ---#

# jetbrains netfilter vmoption
___MY_VMOPTIONS_SHELL_FILE="${HOME}/.jetbrains.vmoptions.sh"; if [ -f "${___MY_VMOPTIONS_SHELL_FILE}" ]; then . "${___MY_VMOPTIONS_SHELL_FILE}"; fi

# yay别名，用于自定义仿apt命令
yat() {
	
	if [ -z "$1" ];then
		yay;
	else
		if [ "$1" = "install" ];then                      # 安装软件
			yay -S $2;
		elif [ "$1" = "update" ];then                     # 更新数据库
			yay -Sy;
		elif [ "$1" = "upgrade" ];then                    # 升级整个系统，y是更新数据库，u是升级软件
			yay -Syu;
		elif [ "$1" = "search" ];then                     # 在包数据库中查询软件
			yay -Ss $2;
		elif [ "$1" = "show" ];then                       # 显示软件的详细信息
			yay -Si $2;
		elif [ "$1" = "info" ];then                       # 显示已安装的软件的详细信息 *
			yay -Qi $2;
		elif [ "$1" = "path" ];then                       # 列出已安装的软件使用的文件夹 *
			yay -Ql $2;
		elif [ "$1" = "clear" ];then                      # 清除软件缓存，即/var/cache/pacman/pkg目录下的文件
			yay -Sc;
		elif [ "$1" = "clean" ];then                      # alias ^
			yay -Sc;
		elif [ "$1" = "remove" ];then                     # 删除单个软件
			yay -R $2;
		elif [ "$1" = "autoremove" ];then                 # 删除指定软件及其没有被其他已安装软件使用的依赖关系
			if [ -z "$2" ]
			then
				yay -c;
			else
				yay -Rs $2;
			fi
		elif [ "$1" = "list" ];then                       # 查询已安装的软件包
			yay -Qs $2;
		elif [ "$1" = "dpkg" ];then                       # 从本地文件安装
			yay -U $2;
		else                                              # 默认命令参数
			yay $1;
		fi
	fi
	
}


# minecraft
minecraft () {
	pwd_curr = pwd
	cd /data/Game/Minecraft/
	java -jar /data/Game/Minecraft/HMCL.jar
	cd $pwd_curr
}

#--- Welcome Message! ---#
# May only works in some system

if [ -z "$RC_LOADED" ];then
	lolcat "/etc/motd.backup"
else
	lolcat "$HOME/.config/motd/100-rc"
fi

RC_LOADED=1
