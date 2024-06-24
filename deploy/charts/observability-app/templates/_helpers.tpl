{{/*
Chart name
*/}}
{{- define "observability.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "observability.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "observability.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "observability.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "observability.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "observability.labels" -}}
helm.sh/chart: {{ include "observability.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "observability.selectorLabels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "observability.scaledownPreDeploy" -}}
scaledown-pre-deploy: {{ default "no" .scaledownPreDeploy | quote }}
{{- end }}

{{/*
Generic image setup
*/}}
{{- define "observability.image" }}
{{- $top := (index . 0) -}}
{{- $image := (index . 1).image -}}
{{- with (default ($top.Values.observability.image).repository $image.repository) -}}
{{- . | trimSuffix "/" | printf "%s/" -}}
{{- end }}
{{- $image.name -}}:{{- tpl (coalesce $image.tag ($top.Values.observability.image).tag "latest") $top -}}
{{- end }}

{{/*
Observability API
*/}}
{{- define "observability.observability_api.name" -}}
observability-api
{{- end -}}

{{- define "observability.observability_api.selectorLabels" -}}
{{ include "observability.selectorLabels" . }}
app.kubernetes.io/name: observability-api
{{- end }}

{{- define "observability.observability_api.image" }}
{{- include "observability.image" (list . .Values.observability_api) }}
{{- end }}

{{/*
Observability UI
*/}}
{{- define "observability.observability_ui.name" -}}
observability-ui
{{- end -}}

{{- define "observability.observability_ui.selectorLabels" -}}
{{ include "observability.selectorLabels" . }}
app.kubernetes.io/name: observability-ui
{{- end }}

{{- define "observability.observability_ui.image" }}
{{- include "observability.image" (list . .Values.observability_ui) }}
{{- end }}

{{/*
Event API
*/}}
{{- define "observability.event_api.name" -}}
event-api
{{- end -}}

{{- define "observability.event_api.selectorLabels" -}}
{{ include "observability.selectorLabels" . }}
app.kubernetes.io/name: event-api
{{- end }}

{{- define "observability.event_api.image" }}
{{- include "observability.image" (list . .Values.event_api) }}
{{- end }}

{{/*
Agent API
*/}}
{{- define "observability.agent_api.name" -}}
agent-api
{{- end -}}

{{- define "observability.agent_api.selectorLabels" -}}
{{ include "observability.selectorLabels" . }}
app.kubernetes.io/name: agent-api
{{- end }}

{{- define "observability.agent_api.image" }}
{{- include "observability.image" (list . .Values.agent_api) }}
{{- end }}

{{/*
Run Manager
*/}}
{{- define "observability.run_manager.name" -}}
run-manager
{{- end -}}

{{- define "observability.run_manager.selectorLabels" -}}
{{ include "observability.selectorLabels" . }}
app.kubernetes.io/name: run-manager
{{- end }}

{{- define "observability.run_manager.image" }}
{{- include "observability.image" (list . .Values.run_manager) }}
{{- end }}

{{/*
Rules Engine
*/}}
{{- define "observability.rules_engine.name" -}}
rules-engine
{{- end -}}

{{- define "observability.rules_engine.selectorLabels" -}}
{{ include "observability.selectorLabels" . }}
app.kubernetes.io/name: rules-engine
{{- end }}

{{- define "observability.rules_engine.image" }}
{{- include "observability.image" (list . .Values.rules_engine) }}
{{- end }}

{{/*
Scheduler
*/}}
{{- define "observability.scheduler.name" -}}
scheduler
{{- end -}}

{{- define "observability.scheduler.selectorLabels" -}}
{{ include "observability.selectorLabels" . }}
app.kubernetes.io/name: scheduler
{{- end }}

{{- define "observability.scheduler.image" }}
{{- include "observability.image" (list . .Values.scheduler) }}
{{- end }}

{{/*
CLI Hook
*/}}
{{- define "observability.cli_hook.image" }}
{{- include "observability.image" (list . .Values.cli_hook) }}
{{- end }}
