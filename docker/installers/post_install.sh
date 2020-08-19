# Fail on first error.
# set -e

# Install necessary packages.
# Bash git prompt.
git clone https://github.com/magicmonty/bash-git-prompt.git ~/.bash-git-prompt --depth=1
# PIP packages.
# pip install --user matplotlib numpy
                   
# Install visual studio code.
# cd ~/
# wget https://go.microsoft.com/fwlink/?LinkID=760868 -O vscode.deb
# sudo dpkg -i vscode.deb
# sudo apt-get -y -f install
# rm vscode.deb

# Configure git.
git config --global user.email "cedric_xie@hotmail.com" 
git config --global user.name "Yuesong Xie"
git config --global credential.helper "cache --timeout=36000"