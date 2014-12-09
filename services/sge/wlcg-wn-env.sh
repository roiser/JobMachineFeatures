#-------------------------------------------------------------------------------
#
#  Name:
#	/etc/profile.d/wlcg-wn-env.sh
#
#  Function:
#	Implementation of "Job Features" [1] in a batch farm managed by
#	PBS Professional or Grid Engine.
#
#	[1] Several talks by Tony Cass at the WLCG Grid Deployment Board
#
#  Details:
#	PBS as well as Grid Engine report the CPU limit of the batch queue by
#	setting the appropriate shell limit. We copy that number (multiplied
#	with the number of cores in case of multi-core jobs) to the
#	cpu_limit_secs output file and also to the wall_limit_secs file as
#	the CPU and the walltime limits of all queues at GridKa are identical.
#	[https://twiki.cern.ch/twiki/bin/view/LCG/WMTEGEnvironmentVariables]
#
#  Author:
#	Manfred Alef, KIT-SCC (GridKa)
#
#  Version:
#	2012-07-17	Implementation for PBS Professional.
#	2012-07-18	Implementation for Grid Engine.
#	2012-07-24	New job features implemented.
#	2012-09-12	WIKI DRAFT 0.9 (13/9/2012).
#	2012-10-06	WIKI DRAFT 0.95 (19/09/2012).
#
#-------------------------------------------------------------------------------


export MACHINEFEATURES=/etc/machinefeatures


#-------------------------------------------------------------------------------


if [ "$PBS_JOBID" -a ! "$JOBFEATURES" ]; then			# PBS branch

  export JOBFEATURES=${TMPDIR:-/tmp}/jobfeatures.$PBS_JOBID
  ncores=$NCPUS

elif [ "$JOB_ID" -a ! "$JOBFEATURES" ]; then			# GE branch

  export JOBFEATURES=${TMPDIR:-/tmp}/jobfeatures.$JOB_ID
  ncores=$NSLOTS

fi


if [ "$JOBFEATURES" ]; then

  if mkdir $JOBFEATURES 2>/dev/null ; then


#  CPU factor - normalization factor as used by the batch system:

    cpufactor_lrms=1.0
    echo $cpufactor_lrms > $JOBFEATURES/cpufactor_lrms


#  Job start - UNIX time stamp (in seconds) of the time when
#				the job started in the batch farm:

    date +%s --utc > $JOBFEATURES/jobstart_secs


#  Allocated CPUs - number of allocated cores to the current job:

    echo $ncores > $JOBFEATURES/allocated_CPU


#  CPU batch queue limit in seconds:
#
#  - Real time:

    let cpu_limit_secs=ncores*$(ulimit -t)
    echo $cpu_limit_secs > $JOBFEATURES/cpu_limit_secs

#  - Normalized:

    cpu_limit_secs_lrms=$(echo "$cpu_limit_secs*$cpufactor_lrms" | bc)
    echo ${cpu_limit_secs_lrms%.*} > $JOBFEATURES/cpu_limit_secs_lrms


#  Walltime batch queue limit in seconds:
#
#  - Real time:
    
    wall_limit_secs=$(ulimit -t)
    echo $wall_limit_secs > $JOBFEATURES/wall_limit_secs

#  - Normalized:

    wall_limit_secs_lrms=$(echo "$wall_limit_secs*$cpufactor_lrms" | bc)
    echo ${wall_limit_secs_lrms%.*} > $JOBFEATURES/wall_limit_secs_lrms


#  RAM limit - memory limit (if any) in MB
#		(count with 1,000 not 1,024, that is 4 GB = 4,000 MB):

    echo 2000 > $JOBFEATURES/mem_limit_MB


#  Disk limit - scratch space limit in GB (if any)
#		(counting is 1 GB = 1,000 MB = 1,000,000,000 Bytes):

    echo 30 > $JOBFEATURES/disk_limit_GB


#  README:

    cat <<++ > $JOBFEATURES/README
JOB FEATURES AND MACHINE FEATURES

Within the HEPiX virtualization group a mechanism was discussed which allows
to access detailed information about the current host and the current job from
a unified place on the worker node. This allows user payload to access meta
information, independent of the current batch system, to access information
like the performance of the node or calculate the remaining run time for the
current job.

See https://twiki.cern.ch/twiki/bin/view/LCG/WMTEGEnvironmentVariables for a
more verbose description of job features and machine features.
++

  fi

  unset ncores cpufactor_lrms cpu_limit_secs cpu_limit_secs_lrms wall_limit_secs wall_limit_secs_lrms

fi


#-------------------------------------------------------------------------------
