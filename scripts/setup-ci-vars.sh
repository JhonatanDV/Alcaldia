#!/bin/bash
# scripts/setup-ci-vars.sh

# Configuración de variables CI/CD para GitLab
# Reemplaza con tus valores reales

GITLAB_TOKEN="glpat-KO0-wTc72FZ2gQrnTHYbam86MQp1OmloemkwCw.01.120tped6q"  # Obtén de User Settings > Access Tokens
PROJECT_ID="75039991"              # Obtén de Project Settings > General

# Función para crear variable
create_variable() {
    local key=$1
    local value=$2

    echo "Creando variable: $key"
    curl --request POST --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
         --form "key=$key" --form "value=$value" \
         "https://gitlab.com/api/v4/projects/$PROJECT_ID/variables"
    echo ""
}

# Variables de Postgres
create_variable "POSTGRES_DB" "test_maintenance_db"
create_variable "POSTGRES_USER" "postgres"
create_variable "POSTGRES_PASSWORD" "postgres"
create_variable "DATABASE_URL" "postgres://postgres:postgres@postgres:5432/test_maintenance_db"

# Variables de MinIO
create_variable "MINIO_ROOT_USER" "minioadmin"
create_variable "MINIO_ROOT_PASSWORD" "minioadmin"
create_variable "MINIO_ACCESS_KEY" "minioadmin"
create_variable "MINIO_SECRET_KEY" "minioadmin"
create_variable "MINIO_ENDPOINT" "http://minio:9000"

echo "Variables configuradas. Verifica en GitLab: Settings > CI/CD > Variables"
