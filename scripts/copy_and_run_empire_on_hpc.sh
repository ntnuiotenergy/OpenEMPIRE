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
CONFIG_FILE="$LOCAL_DIR/config/cluster.json"
SAMPLE_CONFIG_FILE="$LOCAL_DIR/config/cluster.sample.json"

# Check if config.json exists, if not, copy from sample and prompt user to edit it
if [ ! -f "$CONFIG_FILE" ]; then
    cp "$SAMPLE_CONFIG_FILE" "$CONFIG_FILE"
    echo "Config file not found. A new one has been created from the sample. Please edit $CONFIG_FILE and rerun the script."
    exit 1
fi

# Read configuration from JSON file
REMOTE_USER=$(jq -r ".$CLUSTER.REMOTE_USER" $CONFIG_FILE)
REMOTE_SERVER=$(jq -r ".$CLUSTER.REMOTE_SERVER" $CONFIG_FILE)
REMOTE_DIR=$(jq -r ".$CLUSTER.REMOTE_DIR" $CONFIG_FILE)
SCHEDULER_SCRIPT=$(jq -r ".$CLUSTER.SCHEDULER_SCRIPT" $CONFIG_FILE)

# Compress files while excluding certain directories on the local machine
cd $LOCAL_DIR
tar --exclude='./.*' \
    --exclude='./Results/*/' \
    --exclude='./docs/*/' \
    --exclude='./notebooks/*/' \
    --exclude='*__pycache__*' \
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

# 
ssh $REMOTE_USER@$REMOTE_SERVER "chmod +x $REMOTE_DIR/scripts/*"
echo "Made files in the scripts folder executable"


if [[ $CLUSTER = "Solstorm" ]]; then
    echo "Starting SGE job!"
    ssh $REMOTE_USER@$REMOTE_SERVER "cd $REMOTE_DIR && sh $SCHEDULER_SCRIPT"
elif [[ $CLUSTER = "IDUN" ]]; then
    echo "Starting SLURM job!"
    ssh $REMOTE_USER@$REMOTE_SERVER "sbatch $REMOTE_DIR/$SCHEDULER_SCRIPT"
fi
