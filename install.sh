#!/usr/bin/env bash
echo "Type the root password"
su root -c "\
apt-get update && \
apt-get install -y git libfreetype6-dev python-dev python-pip python-tk htop tmux vim && \
\
pip install virtualenv && \
pip install virtualenvwrapper"

export WORKON_HOME=~/Envs
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv mmmdrf
workon mmmdrf
pip install -r requirements.txt

cd mmmalloc/helpers/c_dynamic_priority_queue
/usr/bin/env bash compile.sh

cd -
cd mmmalloc/tests
/usr/bin/env bash compile.sh
cd -
