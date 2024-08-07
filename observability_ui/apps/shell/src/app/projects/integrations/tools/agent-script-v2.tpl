#!/bin/bash
set -eo pipefail


SCRIPT_NAME=$(basename "$0")
DOCKER_DEPLOY_FILE="deploy-docker-agent.json"
KUBERNETES_DEPLOY_FILE="deploy-kubernetes-agent.json"
DEPLOYMENT_NAME="{{deployment_name}}"
SECRET_NAME="observability-agent-secret"
NAMESPACE="datakitchen"

print_usage() {
  cat <<EOF
Usage:
$SCRIPT_NAME
$SCRIPT_NAME [show-configuration]
$SCRIPT_NAME [deploy] [kubernetes|docker]
$SCRIPT_NAME [cleanup] [kubernetes|docker]
EOF
}


# Common
DK_AGENT_TYPE='{{agent_type}}'
DK_AGENT_KEY='{{agent_key}}'
DK_OBSERVABILITY_SERVICE_ACCOUNT_KEY='{{observability_service_account_key}}'
DK_OBSERVABILITY_BASE_URL='{{observability_base_url}}'
DK_PERIOD='{{period}}'
DK_TIMEOUT='{{timeout}}'

# Databricks
DK_DATABRICKS_HOST='{{databricks_host}}'
DK_DATABRICKS_JOBS='{{databricks_jobs}}'
DK_DATABRICKS_FAILED_WATCH_PERIOD='{{databricks_failed_watch_period}}'
DK_DATABRICKS_FAILED_WATCH_MAX_TIME='{{databricks_failed_watch_max_time}}'

# SSIS
DK_SSIS_DB_HOST='{{ssis_db_host}}'
DK_SSIS_DB_PORT='{{ssis_db_port}}'
DK_SSIS_DB_USER='{{ssis_db_user}}'
DK_SSIS_DB_PASSWORD='{{ssis_db_password}}'
DK_SSIS_POLLING_INTERVAL='{{ssis_polling_interval}}'

# Synapse
DK_SYNAPSE_ANALYTICS_WORKSPACE_NAME='{{synapse_analytics_workspace_name}}'
DK_SYNAPSE_ANALYTICS_SUBSCRIPTION_ID='{{synapse_analytics_subscription_id}}'
DK_SYNAPSE_ANALYTICS_RESOURCE_GROUP_NAME='{{synapse_analytics_resource_group_name}}'
DK_SYNAPSE_ANALYTICS_PIPELINES_FILTER='{{synapse_analytics_pipelines_filter}}'

# Airflow
DK_AIRFLOW_API_URL="{{airflow_api_url}}"

# PowerBI
DK_POWERBI_GROUPS='{{powerbi_groups}}'
DK_POWERBI_DATASETS_FETCHING_PERIOD='{{powerbi_datasets_fetching_period}}'

# Qlik
DK_QLIK_TENANT='{{qlik_tenant}}'
DK_QLIK_API_KEY='{{qlik_api_key}}'
DK_QLIK_APPS='{{qlik_apps}}'

# Azure Event Hubs
DK_AZURE_EVENTHUB_MESSAGE_TYPES='{{azure_eventhub_message_types}}'
DK_AZURE_EVENTHUB_NAME='{{azure_eventhub_name}}'
DK_AZURE_EVENTHUB_CONNECTION_STRING='{{azure_eventhub_connection_string}}'
DK_AZURE_EVENTHUB_STARTING_POSITION='{{azure_eventhub_starting_position}}'
DK_AZURE_BLOB_NAME='{{azure_blob_name}}'


# Auth
## Basic
DK_AGENT_USERNAME='{{auth_agent_username}}'
DK_AGENT_PASSWORD='{{auth_agent_password}}'

## Bearer Token
DK_AGENT_TOKEN='{{auth_agent_token}}'

## Azure Service Principal
DK_AZURE_CLIENT_ID='{{auth_azure_client_id}}'
DK_AZURE_CLIENT_SECRET='{{auth_azure_client_secret}}'
DK_AZURE_TENANT_ID='{{auth_azure_tenant_id}}'

# Azure Basic OAuth
DK_AZURE_USERNAME='{{auth_azure_username}}'
DK_AZURE_PASSWORD='{{auth_azure_password}}'


# extra
DOCKER_IMAGE='{{docker_image}}'
DOCKER_TAG='{{docker_tag}}'
DEFAULT_DEPLOYMENT_MODE='{{default_deployment_mode}}'
DOCKER_EXTRA_ENV_VARS='{{docker_extra_env_vars}}'
KUBERNETES_EXTRA_ENV_VARS='{{kubernetes_extra_env_vars}}'

deploy_agent_kubernetes() {
  echo "Creating file $KUBERNETES_DEPLOY_FILE"
  cat <<EOF > "$KUBERNETES_DEPLOY_FILE"
{
  "apiVersion": "v1",
  "kind": "Secret",
  "metadata": {
    "name": "$SECRET_NAME"
  },
  "type": "Opaque",
  "stringData": {
    "DK_AGENT_TYPE": "$DK_AGENT_TYPE",
    "DK_AGENT_KEY": "$DK_AGENT_KEY",
    "DK_OBSERVABILITY_SERVICE_ACCOUNT_KEY": "$DK_OBSERVABILITY_SERVICE_ACCOUNT_KEY",
    "DK_OBSERVABILITY_BASE_URL": "$DK_OBSERVABILITY_BASE_URL",
    "DK_TIMEOUT": "$DK_TIMEOUT",
    "DK_PERIOD": "$DK_PERIOD",
    "DK_AGENT_USERNAME": "$DK_AGENT_USERNAME",
    "DK_AGENT_PASSWORD": "$DK_AGENT_PASSWORD",
    "DK_AGENT_TOKEN": "$DK_AGENT_TOKEN",
    "DK_AZURE_CLIENT_ID": "$DK_AZURE_CLIENT_ID",
    "DK_AZURE_CLIENT_SECRET": "$DK_AZURE_CLIENT_SECRET",
    "DK_AZURE_TENANT_ID": "$DK_AZURE_TENANT_ID",
    "DK_AZURE_USERNAME": "$DK_AZURE_USERNAME",
    "DK_AZURE_PASSWORD": "$DK_AZURE_PASSWORD",
    "DK_SYNAPSE_ANALYTICS_WORKSPACE_NAME": "$DK_SYNAPSE_ANALYTICS_WORKSPACE_NAME",
    "DK_SYNAPSE_ANALYTICS_SUBSCRIPTION_ID": "$DK_SYNAPSE_ANALYTICS_SUBSCRIPTION_ID",
    "DK_SYNAPSE_ANALYTICS_RESOURCE_GROUP_NAME": "$DK_SYNAPSE_ANALYTICS_RESOURCE_GROUP_NAME",
    "DK_SYNAPSE_ANALYTICS_PIPELINES_FILTER": "$DK_SYNAPSE_ANALYTICS_PIPELINES_FILTER",
    "DK_AIRFLOW_API_URL": "$DK_AIRFLOW_API_URL",
    "DK_DATABRICKS_HOST": "$DK_DATABRICKS_HOST",
    "DK_DATABRICKS_JOBS": "$DK_DATABRICKS_JOBS",
    "DK_DATABRICKS_FAILED_WATCH_PERIOD": "$DK_DATABRICKS_FAILED_WATCH_PERIOD",
    "DK_DATABRICKS_FAILED_WATCH_MAX_TIME": "$DK_DATABRICKS_FAILED_WATCH_MAX_TIME",
    "DK_POWERBI_GROUPS": "$DK_POWERBI_GROUPS",
    "DK_POWERBI_DATASETS_FETCHING_PERIOD": "$DK_POWERBI_DATASETS_FETCHING_PERIOD",
    "DK_QLIK_TENANT": "$DK_QLIK_TENANT",
    "DK_QLIK_API_KEY": "$DK_QLIK_API_KEY",
    "DK_QLIK_APPS": "$DK_QLIK_APPS",
    "DK_AZURE_EVENTHUB_MESSAGE_TYPES": "$DK_AZURE_EVENTHUB_MESSAGE_TYPES",
    "DK_AZURE_EVENTHUB_NAME": "$DK_AZURE_EVENTHUB_NAME",
    "DK_AZURE_EVENTHUB_CONNECTION_STRING": "$DK_AZURE_EVENTHUB_CONNECTION_STRING",
    "DK_AZURE_EVENTHUB_STARTING_POSITION": "$DK_AZURE_EVENTHUB_STARTING_POSITION",
    "DK_AZURE_BLOB_NAME": "$DK_AZURE_BLOB_NAME",
    "DK_SSIS_DB_HOST": "$DK_SSIS_DB_HOST",
    "DK_SSIS_DB_PORT": "$DK_SSIS_DB_PORT",
    "DK_SSIS_DB_USER": "$DK_SSIS_DB_USER",
    "DK_SSIS_DB_PASSWORD": "$DK_SSIS_DB_PASSWORD",
    "DK_SSIS_POLLING_INTERVAL": "$DK_SSIS_POLLING_INTERVAL"${KUBERNETES_EXTRA_ENV_VARS:+,}
    $KUBERNETES_EXTRA_ENV_VARS
  }
}
{
  "apiVersion": "apps/v1",
  "kind": "Deployment",
  "metadata":{
    "name": "$DEPLOYMENT_NAME",
    "labels": {
      "app": "$DEPLOYMENT_NAME"
    }
  },
  "spec": {
    "replicas": 1,
    "selector": {
      "matchLabels": {
        "app": "$DEPLOYMENT_NAME"
      }
    },
    "template": {
      "metadata": {
        "labels": {
          "app": "$DEPLOYMENT_NAME"
        }
      },
      "spec": {
        "containers": [
          {
            "name": "$DEPLOYMENT_NAME",
            "image": "$1",
            "imagePullPolicy": "IfNotPresent",
            "envFrom": [
              {
                "secretRef": {
                  "name": "$SECRET_NAME"
                }
              }
            ]
          }
        ]
      }
    }
  }
}
EOF

  kubectl apply --namespace "$NAMESPACE" --filename "$KUBERNETES_DEPLOY_FILE"
}


kubernetes_deploy() {
  kubectl create namespace "$NAMESPACE" > /dev/null 2>&1 || true
  image="$DOCKER_IMAGE:$DOCKER_TAG"
  kubectl delete deploy "$DEPLOYMENT_NAME" --namespace "$NAMESPACE" 2> /dev/null || true
  kubectl delete secret "$SECRET_NAME" --namespace "$NAMESPACE" 2> /dev/null || true
  echo "#### Deploying DataKitchen's Observability Agent ##### "
  deploy_agent_kubernetes "$image"
}


kubernetes_cleanup() {
  echo "##### Removing DataKitchen's Observability Agent #####"
  kubectl delete deploy $DEPLOYMENT_NAME listener-agent --namespace "$NAMESPACE" 2> /dev/null || true
  kubectl delete secret $SECRET_NAME listener-secret --namespace "$NAMESPACE" 2> /dev/null || true
}


create_docker_compose_file() {
  echo "Creating file $DOCKER_DEPLOY_FILE"
  cat <<EOF > $DOCKER_DEPLOY_FILE
{
  "version": "3.8",
  "services": {
    "$DEPLOYMENT_NAME": {
      "image": "$DOCKER_IMAGE:$DOCKER_TAG",
      "container_name": "$DEPLOYMENT_NAME",
      "extra_hosts": [
        "host.docker.internal:host-gateway"
      ],
      "environment": [
        "DK_AGENT_TYPE=$DK_AGENT_TYPE",
        "DK_AGENT_KEY=$DK_AGENT_KEY",
        "DK_OBSERVABILITY_SERVICE_ACCOUNT_KEY=$DK_OBSERVABILITY_SERVICE_ACCOUNT_KEY",
        "DK_OBSERVABILITY_BASE_URL=$DK_OBSERVABILITY_BASE_URL",
        "DK_TIMEOUT=$DK_TIMEOUT",
        "DK_PERIOD=$DK_PERIOD",
        "DK_AGENT_USERNAME=$DK_AGENT_USERNAME",
        "DK_AGENT_PASSWORD=$DK_AGENT_PASSWORD",
        "DK_AGENT_TOKEN=$DK_AGENT_TOKEN",
        "DK_AZURE_CLIENT_ID=$DK_AZURE_CLIENT_ID",
        "DK_AZURE_CLIENT_SECRET=$DK_AZURE_CLIENT_SECRET",
        "DK_AZURE_TENANT_ID=$DK_AZURE_TENANT_ID",
        "DK_AZURE_USERNAME=$DK_AZURE_USERNAME",
        "DK_AZURE_PASSWORD=$DK_AZURE_PASSWORD",
        "DK_SYNAPSE_ANALYTICS_WORKSPACE_NAME=$DK_SYNAPSE_ANALYTICS_WORKSPACE_NAME",
        "DK_SYNAPSE_ANALYTICS_SUBSCRIPTION_ID=$DK_SYNAPSE_ANALYTICS_SUBSCRIPTION_ID",
        "DK_SYNAPSE_ANALYTICS_RESOURCE_GROUP_NAME=$DK_SYNAPSE_ANALYTICS_RESOURCE_GROUP_NAME",
        "DK_SYNAPSE_ANALYTICS_PIPELINES_FILTER=$DK_SYNAPSE_ANALYTICS_PIPELINES_FILTER",
        "DK_AIRFLOW_API_URL=$DK_AIRFLOW_API_URL",
        "DK_DATABRICKS_JOBS=$DK_DATABRICKS_JOBS",
        "DK_DATABRICKS_HOST=$DK_DATABRICKS_HOST",
        "DK_DATABRICKS_FAILED_WATCH_PERIOD=$DK_DATABRICKS_FAILED_WATCH_PERIOD",
        "DK_DATABRICKS_FAILED_WATCH_MAX_TIME=$DK_DATABRICKS_FAILED_WATCH_MAX_TIME",
        "DK_POWERBI_GROUPS=$DK_POWERBI_GROUPS",
        "DK_POWERBI_DATASETS_FETCHING_PERIOD=$DK_POWERBI_DATASETS_FETCHING_PERIOD",
        "DK_QLIK_TENANT=$DK_QLIK_TENANT",
        "DK_QLIK_API_KEY=$DK_QLIK_API_KEY",
        "DK_QLIK_APPS=$DK_QLIK_APPS",
        "DK_AZURE_EVENTHUB_MESSAGE_TYPES=$DK_AZURE_EVENTHUB_MESSAGE_TYPES",
        "DK_AZURE_EVENTHUB_NAME=$DK_AZURE_EVENTHUB_NAME",
        "DK_AZURE_EVENTHUB_CONNECTION_STRING=$DK_AZURE_EVENTHUB_CONNECTION_STRING",
        "DK_AZURE_EVENTHUB_STARTING_POSITION=$DK_AZURE_EVENTHUB_STARTING_POSITION",
        "DK_AZURE_BLOB_NAME=$DK_AZURE_BLOB_NAME",
        "DK_SSIS_DB_HOST=$DK_SSIS_DB_HOST",
        "DK_SSIS_DB_PORT=$DK_SSIS_DB_PORT",
        "DK_SSIS_DB_USER=$DK_SSIS_DB_USER",
        "DK_SSIS_DB_PASSWORD=$DK_SSIS_DB_PASSWORD",
        "DK_SSIS_POLLING_INTERVAL=$DK_SSIS_POLLING_INTERVAL"${DOCKER_EXTRA_ENV_VARS:+,}
        $DOCKER_EXTRA_ENV_VARS
      ]
    }
  }
}
EOF
}


docker_deploy() {
  create_docker_compose_file
  echo "#### Deploying DataKitchen's Observability Agent ##### "
  docker compose --file "$DOCKER_DEPLOY_FILE" up --detach
}


docker_cleanup() {
  create_docker_compose_file
  echo "##### Removing DataKitchen's Observability Agent #####"
  docker compose --file "$DOCKER_DEPLOY_FILE" down || true
  docker rmi "$DOCKER_IMAGE:$DOCKER_TAG" || true
}


show_configuration() {
  cat <<EOF
  DK_AGENT_TYPE: '$DK_AGENT_TYPE'
  DK_AGENT_KEY: '$DK_AGENT_KEY'
  DK_OBSERVABILITY_SERVICE_ACCOUNT_KEY: '$DK_OBSERVABILITY_SERVICE_ACCOUNT_KEY'
  DK_OBSERVABILITY_BASE_URL: '$DK_OBSERVABILITY_BASE_URL'
  DK_TIMEOUT: '$DK_TIMEOUT'
  DK_PERIOD: '$DK_PERIOD'
  DK_AGENT_USERNAME: '$DK_AGENT_USERNAME'
  DK_AGENT_PASSWORD: '$DK_AGENT_PASSWORD'
  DK_AGENT_TOKEN: '$DK_AGENT_TOKEN'
  DK_AZURE_CLIENT_ID: '$DK_AZURE_CLIENT_ID'
  DK_AZURE_CLIENT_SECRET: '$DK_AZURE_CLIENT_SECRET'
  DK_AZURE_TENANT_ID: '$DK_AZURE_TENANT_ID'
  DK_AZURE_USERNAME: '$DK_AZURE_USERNAME'
  DK_AZURE_PASSWORD: '$DK_AZURE_PASSWORD'
  DK_DATABRICKS_JOBS: '$DK_DATABRICKS_JOBS'
  DK_DATABRICKS_HOST: '$DK_DATABRICKS_HOST'
  DK_DATABRICKS_FAILED_WATCH_PERIOD: '$DK_DATABRICKS_FAILED_WATCH_PERIOD'
  DK_DATABRICKS_FAILED_WATCH_MAX_TIME: '$DK_DATABRICKS_FAILED_WATCH_MAX_TIME'
  DK_SYNAPSE_ANALYTICS_WORKSPACE_NAME: '$DK_SYNAPSE_ANALYTICS_WORKSPACE_NAME'
  DK_SYNAPSE_ANALYTICS_SUBSCRIPTION_ID: '$DK_SYNAPSE_ANALYTICS_SUBSCRIPTION_ID'
  DK_SYNAPSE_ANALYTICS_RESOURCE_GROUP_NAME: '$DK_SYNAPSE_ANALYTICS_RESOURCE_GROUP_NAME'
  DK_SYNAPSE_ANALYTICS_PIPELINES_FILTER: '$DK_SYNAPSE_ANALYTICS_PIPELINES_FILTER'
  DK_AIRFLOW_API_URL: '$DK_AIRFLOW_API_URL'
  DK_POWERBI_GROUPS: '$DK_POWERBI_GROUPS'
  DK_POWERBI_DATASETS_FETCHING_PERIOD: '$DK_POWERBI_DATASETS_FETCHING_PERIOD'
  DK_QLIK_TENANT: '$DK_QLIK_TENANT'
  DK_QLIK_API_KEY: '$DK_QLIK_API_KEY'
  DK_QLIK_APPS: '$DK_QLIK_APPS'
  DK_AZURE_EVENTHUB_MESSAGE_TYPES: '$DK_AZURE_EVENTHUB_MESSAGE_TYPES',
  DK_AZURE_EVENTHUB_NAME: '$DK_AZURE_EVENTHUB_NAME',
  DK_AZURE_EVENTHUB_CONNECTION_STRING: '$DK_AZURE_EVENTHUB_CONNECTION_STRING',
  DK_AZURE_EVENTHUB_STARTING_POSITION: '$DK_AZURE_EVENTHUB_STARTING_POSITION',
  DK_AZURE_BLOB_NAME: '$DK_AZURE_BLOB_NAME',
  DK_SSIS_DB_HOST: '$DK_SSIS_DB_HOST'
  DK_SSIS_DB_PORT: '$DK_SSIS_DB_PORT'
  DK_SSIS_DB_USER: '$DK_SSIS_DB_USER'
  DK_SSIS_DB_PASSWORD: '$DK_SSIS_DB_PASSWORD'
  DK_SSIS_POLLING_INTERVAL: '$DK_SSIS_POLLING_INTERVAL'
$KUBERNETES_EXTRA_ENV_VARS
$DOCKER_EXTRA_ENV_VARS
EOF
}


check_kubectl_cmd() {
  command -v kubectl &>/dev/null || { echo "error: command 'kubectl' is not present"; exit 1;}
}


check_docker_cmd() {
  command -v docker &>/dev/null || { echo "error: command 'docker' is not present"; exit 1;}
}


action=deploy
deploy_to=$DEFAULT_DEPLOYMENT_MODE

if [ $# -ge 1 ]
then
  action=$1
fi
if [ $# -ge 2 ]
then
  deploy_to=$2
fi
if [ $# -gt 2 ]
then
  print_usage
  exit 1
fi

case "$action##$deploy_to" in
  "show-configuration##"*)
    show_configuration
    ;;
  "deploy##kubernetes")
    check_kubectl_cmd
    kubernetes_deploy
    ;;
  "cleanup##kubernetes")
    check_kubectl_cmd
    kubernetes_cleanup
    ;;
  "deploy##docker")
    check_docker_cmd
    docker_deploy
    ;;
  "cleanup##docker")
    check_docker_cmd
    docker_cleanup
    ;;
  *)
    print_usage
    exit 1
esac
