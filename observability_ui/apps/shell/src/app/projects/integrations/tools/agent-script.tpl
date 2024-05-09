#!/bin/bash

set -eo pipefail

SCRIPT_NAME=$(basename "$0")

print_usage() {
  cat <<EOF
Usage:
$SCRIPT_NAME 
$SCRIPT_NAME [show-configuration]
$SCRIPT_NAME [kubernetes|docker]
$SCRIPT_NAME [cleanup] [kubernetes|docker]
EOF
}

EVENTS_API_HOST="{{events_api_host}}"
EVENTS_API_KEY="{{events_api_key}}"
EVENT_HUB_CONN_STR="{{event_hub_conn_str}}"
EVENT_HUB_NAME="{{event_hub_name}}"
AZURE_STORAGE_CONN_STR="{{azure_storage_conn_str}}"
BLOB_CONTAINER_NAME="{{blob_container_name}}"
EXTERNAL_PLUGINS_PATH="{{external_plugins_path}}"
ENABLED_PLUGINS="{{enabled_plugins}}"
PUBLISH_EVENTS="{{publish_events}}"
AIRFLOW_PASSWORD="{{airflow_password}}"
AIRFLOW_USERNAME="{{airflow_username}}"
BASE_AIRFLOW_API_URL="{{base_airflow_api_url}}"
DOCKER_IMAGE="{{docker_image}}"
DOCKER_TAG="{{docker_tag}}"
DOCKER_EXTRA_ENV_VARS="{{docker_extra_env_vars}}"
KUBERNETES_EXTRA_ENV_VARS="{{kubernetes_extra_env_vars}}"
DEFAULT_DEPLOYMENT_MODE="{{default_deployment_mode}}"
TARGET_SERVICE="{{target_service}}"

deploy_agent_kubernetes() {
  echo "Creating file deploy-kubernetes-$TARGET_SERVICE.yaml"
  cat <<EOF > "deploy-kubernetes-$TARGET_SERVICE.yaml"
---
apiVersion: v1
kind: Secret
metadata:
  namespace: datakitchen
  name: $TARGET_SERVICE-secret
type: Opaque
stringData:
  EVENTS_API_HOST: '$EVENTS_API_HOST'
  EVENTS_API_KEY: '$EVENTS_API_KEY'
  EVENT_HUB_CONN_STR: '$EVENT_HUB_CONN_STR'
  EVENT_HUB_NAME: '$EVENT_HUB_NAME'
  AZURE_STORAGE_CONN_STR: '$AZURE_STORAGE_CONN_STR'
  BLOB_CONTAINER_NAME: '$BLOB_CONTAINER_NAME'
  EXTERNAL_PLUGINS_PATH: '$EXTERNAL_PLUGINS_PATH'
  ENABLED_PLUGINS: '$ENABLED_PLUGINS'
  PUBLISH_EVENTS: '$PUBLISH_EVENTS'
  AIRFLOW_PASSWORD: '$AIRFLOW_PASSWORD'
  AIRFLOW_USERNAME: '$AIRFLOW_USERNAME'
  BASE_AIRFLOW_API_URL: '$BASE_AIRFLOW_API_URL'
$KUBERNETES_EXTRA_ENV_VARS
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $TARGET_SERVICE-agent
  namespace: datakitchen
  labels:
    app: $TARGET_SERVICE-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: $TARGET_SERVICE-agent
  template:
    metadata:
      labels:
        app: $TARGET_SERVICE-agent
    spec:
      containers:
      - name: $TARGET_SERVICE-agent
        image: $1
        imagePullPolicy: IfNotPresent
        envFrom:
        - secretRef:
            name: $TARGET_SERVICE-secret
EOF

  kubectl apply -f "deploy-kubernetes-$TARGET_SERVICE.yaml"
}

kubernetes_deploy() {
  command -v kubectl &>/dev/null || { echo "error: command 'kubectl' is not present"; exit 1;}
  kubectl create ns datakitchen > /dev/null 2>&1 || true
  image="$DOCKER_IMAGE:$DOCKER_TAG"
  kubectl delete deploy "$TARGET_SERVICE-agent" -n datakitchen 2> /dev/null || true
  kubectl delete secret "$TARGET_SERVICE-secret" -n datakitchen 2> /dev/null || true
  echo "#### Deploying DataKitchen's $TARGET_SERVICE Agent ##### "
  deploy_agent_kubernetes "$image"
  
}

kubernetes_cleanup() {
  command -v kubectl &>/dev/null || { echo "error: command 'kubectl' is not present"; exit 1;}
  echo "##### Removing DataKitchen's $TARGET_SERVICE Agent #####"
  kubectl delete deploy $TARGET_SERVICE-agent listener-agent -n datakitchen 2> /dev/null || true
  kubectl delete secret $TARGET_SERVICE-secret listener-secret -n datakitchen 2> /dev/null || true
}


create_docker_compose_file() {
  image="$DOCKER_IMAGE:$DOCKER_TAG"

  echo "Creating file deploy-docker-$TARGET_SERVICE.yaml"
  cat <<EOF > deploy-docker-$TARGET_SERVICE.yaml
version: "3.8"

services:
  $TARGET_SERVICE:
    image: $image
    container_name: $TARGET_SERVICE
    extra_hosts:
      - host.docker.internal:host-gateway
    environment:
      - EVENTS_API_HOST='$EVENTS_API_HOST'
      - EVENTS_API_KEY='$EVENTS_API_KEY'
      - EVENT_HUB_CONN_STR='$EVENT_HUB_CONN_STR'
      - EVENT_HUB_NAME='$EVENT_HUB_NAME'
      - AZURE_STORAGE_CONN_STR='$AZURE_STORAGE_CONN_STR'
      - BLOB_CONTAINER_NAME='$BLOB_CONTAINER_NAME'
      - EXTERNAL_PLUGINS_PATH='$EXTERNAL_PLUGINS_PATH'
      - ENABLED_PLUGINS='$ENABLED_PLUGINS'
      - PUBLISH_EVENTS='$PUBLISH_EVENTS'
      - AIRFLOW_PASSWORD='$AIRFLOW_PASSWORD'
      - AIRFLOW_USERNAME='$AIRFLOW_USERNAME'
      - BASE_AIRFLOW_API_URL='$BASE_AIRFLOW_API_URL'
$DOCKER_EXTRA_ENV_VARS

EOF
}

docker_deploy() {
  command -v docker &>/dev/null || { echo "error: command 'docker' is not present"; exit 1;}
  create_docker_compose_file
  echo "#### Deploying DataKitchen's $TARGET_SERVICE Agent ##### "
  docker compose -f deploy-docker-$TARGET_SERVICE.yaml up -d
}

docker_cleanup() {
  create_docker_compose_file
  echo "##### Removing DataKitchen's $TARGET_SERVICE Agent #####"
  docker compose -f  deploy-docker-$TARGET_SERVICE.yaml down || true
  docker rmi $DOCKER_IMAGE:$DOCKER_TAG || true
}

show_configuration() {
  cat <<EOF
  EVENTS_API_HOST: '$EVENTS_API_HOST'
  EVENTS_API_KEY: '$EVENTS_API_KEY'
  EVENT_HUB_CONN_STR: '$EVENT_HUB_CONN_STR'
  EVENT_HUB_NAME: '$EVENT_HUB_NAME'
  AZURE_STORAGE_CONN_STR: '$AZURE_STORAGE_CONN_STR'
  BLOB_CONTAINER_NAME: '$BLOB_CONTAINER_NAME'
  EXTERNAL_PLUGINS_PATH: '$EXTERNAL_PLUGINS_PATH' 
  ENABLED_PLUGINS: '$ENABLED_PLUGINS'
  PUBLISH_EVENTS: '$PUBLISH_EVENTS'
  AIRFLOW_PASSWORD: '$AIRFLOW_PASSWORD'
  AIRFLOW_USERNAME: '$AIRFLOW_USERNAME'
  BASE_AIRFLOW_API_URL: '$BASE_AIRFLOW_API_URL'
$KUBERNETES_EXTRA_ENV_VARS
EOF
}



deployment_option=$DEFAULT_DEPLOYMENT_MODE

if [ -n "$2" ]; then
  deployment_option="$2"
elif [ -n "$1" ]; then
  deployment_option="$1"
fi

if [ "$1" == "show-configuration" ]; then
  show_configuration
elif  [ "$1" == "cleanup" ]; then
  if [ "$deployment_option" == "kubernetes" ]; then
    kubernetes_cleanup
  elif [ "$deployment_option" == "docker" ]; then
    docker_cleanup
  else
    print_usage
    exit 1
  fi
elif [ "$deployment_option" == "kubernetes" ]; then
  kubernetes_deploy
elif [ "$deployment_option" == "docker" ]; then
  docker_deploy
else
  print_usage
  exit 1
fi