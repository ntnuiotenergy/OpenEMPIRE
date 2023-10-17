#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $(basename $0) <cluster_name>"
    echo "Cluster name should be one of: Solstorm, IDUN"
    exit 1
fi

CLUSTER="$1"

# Specify directories and server details
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOCAL_DIR="$SCRIPT_DIR/.."

REMOTE_USER="martihj"
if [[ $CLUSTER = "Solstorm" ]]; then
    REMOTE_SERVER="solstorm-login.iot.ntnu.no"
    REMOTE_DIR="/home/martihj/OpenEMPIRE"
    SCHEDULER_SCRIPT="scripts/norway_analysis_sge.sh"
elif [[ $CLUSTER = "IDUN" ]]; then
    REMOTE_SERVER="idun-login1.hpc.ntnu.no"
    REMOTE_DIR="/cluster/home/martihj/OpenEMPIRE"
    SCHEDULER_SCRIPT="scripts/norway_analysis_slurm.sh"
fi



# Compress files while excluding certain directories on the local machine
cd $LOCAL_DIR
tar --exclude='./.*' \
    --exclude='./Results/*/' \
    --exclude='./docs/*/' \
    --exclude='./notebooks/*/' \
    -cvzf myfiles.tar.gz *
    
# Transfer the compressed file to the remote server
scp myfiles.tar.gz $REMOTE_USER@$REMOTE_SERVER:$REMOTE_DIR

# Decompress the files on the remote server and then remove the tarball
ssh $REMOTE_USER@$REMOTE_SERVER << EOF
    cd $REMOTE_DIR
    tar -xvzf myfiles.tar.gz
    rm myfiles.tar.gz
EOF

# Optionally, remove the tarball from the local machine
rm $LOCAL_DIR/myfiles.tar.gz

echo "Transfer complete!"


# if [[ $CLUSTER = "Solstorm" ]]; then
#     echo "Starting SGE job!"
# elif [[ $CLUSTER = "IDUN" ]]; then
#     echo "Starting SLURM job!"
# fi

# ssh $REMOTE_USER@$REMOTE_SERVER "sbatch $REMOTE_DIR/$SCHEDULER_SCRIPT"