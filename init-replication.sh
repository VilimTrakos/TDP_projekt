#!/bin/sh

# Wait for CouchDB instances to be fully up
echo "Waiting for CouchDB instances to start..."
sleep 15

# Function to create database and verify
create_db_medical() {
    HOST=$1
    echo "Creating database on $HOST..."
    RESPONSE=$(curl -s -X PUT http://admin:password@$HOST:5984/medical_records)
    echo "Response from $HOST: $RESPONSE"
}
create_db_users() {
    HOST=$1
    echo "Creating database on $HOST..."
    RESPONSE=$(curl -s -X PUT http://admin:password@$HOST:5984/_users)
    echo "Response from $HOST: $RESPONSE"
}

# Function to set up replication
setup_replication() {
    SOURCE=$1
    TARGET=$2
    TARGET_HOST=$3
    echo "Setting up replication from $SOURCE to $TARGET on $TARGET_HOST..."
    
    RESPONSE=$(curl -s -X POST http://admin:password@$TARGET_HOST:5984/_replicate \
        -H "Content-Type: application/json" \
        -d "{
            \"source\": \"http://admin:password@$SOURCE:5984/medical_records\",
            \"target\": \"http://admin:password@$TARGET:5984/medical_records\",
            \"continuous\": true
        }")
    echo "Replication response: $RESPONSE"
}

# Create databases
create_db_medical "couch_a"
create_db_medical "couch_b"
create_db_medical "couch_c"
create_db_users "couch_a"
create_db_users "couch_b"
create_db_users "couch_c"

# Wait a bit for databases to be fully created
sleep 5

# Set up replications
setup_replication "couch_c" "couch_b" "couch_b"
setup_replication "couch_b" "couch_a" "couch_a"

# Verify replication tasks
echo "\nChecking active tasks on couch_a:"
curl -s http://admin:password@couch_a:5984/_active_tasks

echo "\nChecking active tasks on couch_b:"
curl -s http://admin:password@couch_b:5984/_active_tasks

# Test replication with a document
echo "\nCreating test document on couch_c..."
curl -s -X PUT \
    http://admin:password@couch_c:5984/medical_records/test_doc \
    -H "Content-Type: application/json" \
    -d '{"test": "replication test", "timestamp": "datum i vrijeme"}'

echo "Setup completed. Please check logs for any errors."