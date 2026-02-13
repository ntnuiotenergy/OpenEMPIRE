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

# Read configuration from JSON file using Python
CONFIG_VALUES=$(python << EOF
import json
import os
config_file = r"$CONFIG_FILE"
# Convert Git Bash path to Windows path if needed
if config_file.startswith('/c/'):
    config_file = 'C:' + config_file[2:].replace('/', '\\\\')
with open(config_file) as f:
    config = json.load(f)
    cluster_config = config.get('$CLUSTER', {})
    print(cluster_config.get('REMOTE_USER', ''))
    print(cluster_config.get('REMOTE_SERVER', ''))
    print(cluster_config.get('REMOTE_DIR', ''))
    print(cluster_config.get('SCHEDULER_SCRIPT', ''))
EOF
)

# Parse the output into variables
REMOTE_USER=$(echo "$CONFIG_VALUES" | sed -n '1p')
REMOTE_SERVER=$(echo "$CONFIG_VALUES" | sed -n '2p')
REMOTE_DIR=$(echo "$CONFIG_VALUES" | sed -n '3p')
SCHEDULER_SCRIPT=$(echo "$CONFIG_VALUES" | sed -n '4p')

# Check if configuration was read successfully
if [ -z "$REMOTE_USER" ] || [ -z "$REMOTE_SERVER" ]; then
    echo "ERROR: Failed to read cluster configuration from $CONFIG_FILE"
    echo "Please verify the file exists and contains valid JSON for cluster '$CLUSTER'"
    exit 1
fi

echo "================================================"
echo "Running prerequisite checks..."
echo "================================================"

# Test 1: Check local script permissions
echo "Test 1: Checking local script permissions..."
if [ ! -x "$SCRIPT_DIR/copy_and_run_empire_on_hpc.sh" ]; then
    echo "ERROR: Local scripts are not executable. Fixing..."
    chmod +x "$SCRIPT_DIR"/*.sh
    echo "✓ Script permissions fixed."
else
    echo "✓ Local scripts are executable."
fi

# Test 2: Check if conda is available on remote server
echo "Test 2: Checking conda on $CLUSTER..."
if ssh $REMOTE_USER@$REMOTE_SERVER "source ~/miniconda3/etc/profile.d/conda.sh && which conda" > /dev/null 2>&1; then
    CONDA_PATH=$(ssh $REMOTE_USER@$REMOTE_SERVER "source ~/miniconda3/etc/profile.d/conda.sh && which conda")
    echo "✓ Conda found at: $CONDA_PATH"
else
    echo "WARNING: Conda not found in default PATH on $CLUSTER."
    echo "The SGE script will attempt to initialize conda automatically."
fi

echo "================================================"
echo "All prerequisite checks passed!"
echo "================================================"
echo ""

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
