# WLCG Worker Node Environment profile.d script
#
# Copyright (c) 2012 by
#   Jan Just Keijser (janjust@nikhef.nl)
#   Nikhef
#   Amsterdam
#   The Netherlands

# Get the configuration setting from the /etc/wlcg_wn_env.conf file
eval "JOBFEATURES=`sed -n '/^jobfeatures/s/^jobfeatures *= *\(.*\)/\1/p' /etc/wlcg-wn-env.conf 2> /dev/null`"

# fallback if setting is missing
if [ -z "${JOBFEATURES}" ]
then
    JOBFEATURES=${TMPDIR:-/tmp}/jobfeatures/${PBS_JOBID}
fi


export JOBFEATURES

# if this profile.d script is called with the parameter --csh
# then a 'setenv' line is written to stdout.
# the output of this command can be evaluated by a csh-like shell.
# (currently not needed as the jobwrappers run as bash and set the
#  right env vars for all child scripts, including csh scripts)
if [ "x$1" = "x--csh" ]
then
    echo "setenv JOBFEATURES ${JOBFEATURES}"
fi

