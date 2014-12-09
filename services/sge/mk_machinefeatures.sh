#!/bin/sh

#-------------------------------------------------------------------------------
#
#  Nmae:
#	/root/bin/mk_machinefeatures.sh
#
#  Function:
#	Implementation of "Machine Features" [1] with files "hs06" and
#	"shutdowntime" in an extra directory "/etc/machinefeatures".
#	Note: the HS06 score is per job slot.
#
#	[1] Several talks by Tony Cass at the WLCG Grid Deployment Board
#
#  Details:
#	https://twiki.cern.ch/twiki/bin/view/LCG/WMTEGEnvironmentVariables
#
#  Author:
#	Manfred Alef, KIT-SCC (GridKa)
#
#  Version:
#	2012-07-19
#	2012-07-24	Extended set of features implemented.
#
#-------------------------------------------------------------------------------


umask 22


[ -d /etc/machinefeatures ] || mkdir /etc/machinefeatures || exit 1


cd /etc/machinefeatures

processor=$(grep -m 1 "^model name" /proc/cpuinfo)
#sockets=$(grep "^physical id" /proc/cpuinfo | sort -u | wc -l)
cores=$(grep -c "^model name" /proc/cpuinfo)

case ${cores}/${processor#model name	*: } in

  24/"AMD Opteron(tm) Processor 6168")		
		echo 183.1 > hs06
		echo 24    > jobslots
		echo 24    > phys_cores
		echo  0    > log_cores
		;;
  48/"AMD Opteron(tm) Processor 6174")		
		echo 399.9 > hs06
		echo 48    > jobslots
		echo 48    > phys_cores
		echo  0    > log_cores
		;;
  32/"AMD Opteron(TM) Processor 6276")		
		echo 314.0 > hs06
		echo 32    > jobslots
		echo 32    > phys_cores
		echo  0    > log_cores
		;;
  64/"AMD Opteron(TM) Processor 6276")		
		echo 467.8 > hs06
		echo 64    > jobslots
		echo 32    > phys_cores
		echo 64    > log_cores
		;;
   8/"Intel(R) Xeon(R) CPU           L5420  @ 2.50GHz")
		echo 70.77 > hs06
		echo  8    > jobslots
		echo  8    > phys_cores
		echo  0    > log_cores
		;;
   8/"Intel(R) Xeon(R) CPU           E5430  @ 2.66GHz")
		echo 72.99 > hs06
		echo  8    > jobslots
		echo  8    > phys_cores
		echo  0    > log_cores
		;;
  16/"Intel(R) Xeon(R) CPU           E5520  @ 2.27GHz")
		echo 107.9 > hs06
		echo 12    > jobslots
		echo  8    > phys_cores
		echo 16    > log_cores
		;;
  16/"Intel(R) Xeon(R) CPU           L5520  @ 2.27GHz")
		echo 119.9 > hs06
		echo 16    > jobslots
		echo  8    > phys_cores
		echo 16    > log_cores
		;;
  16/"Intel(R) Xeon(R) CPU           E5630  @ 2.53GHz")
		echo 121.0 > hs06
		echo 12    > jobslots
		echo  8    > phys_cores
		echo 16    > log_cores
		;;
  32/*"Intel(R) Xeon(R) CPU E5-2665 0 @ 2.40GHz")
		echo 294.0 > hs06
		echo 24    > jobslots
		echo 16    > phys_cores
		echo 32    > log_cores
		;;
  *)	logger -t machinefeatures -- "New CPU type (${processor#model name    *: }), unknown HS06 score" ;;

esac

#touch /etc/machinefeatures/shutdowntime

cat <<++ > /etc/machinefeatures/README
JOB FEATURES AND MACHINE FEATURES

The job features and the machine features provide details of the site
specific worker node configurations to the user.

This allows user payload to access meta information, independent of the
current batch system, to access information like the performance of the
node or calculate the remaining run time for the current job.

Details:
- https://twiki.cern.ch/twiki/bin/view/LCG/WMTEGEnvironmentVariables
- https://twiki.cern.ch/twiki/bin/view/LCG/MachineJobFeatures
++


#-------------------------------------------------------------------------------
