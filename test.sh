#!/bin/sh

# Write down the current git version just for future reference.
mkdir -p .coverage-results
git log | head -1 > .coverage-results/version-stamp.txt

# This script depends on trialcoverage >= 0.3.5 and on coverage.py >= 3.3.2a1z8.
# The following lines will print an ugly warning message if those two are not
# installed.
python -c 'import pkg_resources;pkg_resources.require("trialcoverage>=0.3.6")' &&
python -c 'import pkg_resources;pkg_resources.require("coverage>=3.3.2a1z9")' &&
python -c 'import pkg_resources;pkg_resources.require("setuptools_trial")'
RETVAL=$?
if [ ${RETVAL} != 0 ] ; then
    echo "FAILED: we need trialcoverage, coverage.py, and setuptools_trial. To get the latest release of trialcoverage, run 'sudo easy_install -U trialcoverage'. To get the latest snapshot of Zooko's branch of coverage.py, run 'sudo easy_install -U http://bitbucket.org/zooko/coverage.py/get/tip.gz'. To get setuptools_trial run 'sudo easy_install setuptools_trial'."
    exit ${RETVAL}
fi

python -tt setup.py flakes
RETVAL=$?
if [ ${RETVAL} != 0 ] ; then
    echo "FAILED: pyflakes reported warnings -- exiting"
    exit ${RETVAL}
fi

PROJNAME=`python setup.py --name`

rm .coverage
python -tt setup.py trial --reporter=bwverbose-coverage --rterrors $*
RETVAL=$?
echo "To see coverage details run 'coverage report' or open htmlcov/index.html."
coverage html
if [ ${RETVAL} = 0 ]; then
  echo SUCCESS
fi
exit $RETVAL

