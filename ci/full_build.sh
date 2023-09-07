#!/usr/bin/env bash
#
# launch all needed checks against whole ALS codebase
#
###########################################################################

set -e

$(readlink -f $(dirname $(readlink -f ${0})))/pylint.sh

# run Tests
echo "**********************************************************************"
echo "******** Tests START"
echo "**********************************************************************"
python setup.py test
echo "**********************************************************************"
echo "******** Tests Done"
echo "**********************************************************************"

# build docs
echo "**********************************************************************"
echo "******** docs build START"
echo "**********************************************************************"
python setup.py docs
echo "**********************************************************************"
echo "******** docs build OK"
echo "**********************************************************************"