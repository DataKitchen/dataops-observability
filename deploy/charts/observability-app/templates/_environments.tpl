{{/*
Environment
*/}}

{{- define "observability.environment.base" -}}
- name: OBSERVABILITY_CONFIG
  value: {{ include "observability.config_type" . | quote }}
{{- end -}}

{{- define "observability.environment.pythonpath" -}}
- name: PYTHONPATH
  value: {{ include "observability.pythonpath" . | quote }}
{{- end -}}

{{- define "observability.environment.flask" -}}
- name: FLASK_DEBUG
  value: {{ .Values.observability.flask_debug | default "false" | quote }}
{{- end -}}

{{- define "observability.environment.database" -}}
{{- if eq (include "observability.config_type" .) "minikube" -}}
- name: MYSQL_USER
  value: {{ .Values.observability.mysql_user | quote }}
- name: MYSQL_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.mysql_secrets_name | quote }}
      key: mysql-password
{{- else -}}
- name: DB_HOST
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.services_secrets_name | quote }}
      key: DB_HOST
- name: DB_PORT
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.services_secrets_name | quote }}
      key: DB_PORT
- name: DB_USER
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.services_secrets_name | quote }}
      key: DB_USER
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.services_secrets_name | quote }}
      key: DB_PASSWORD
{{- end -}}
{{- end -}}


{{- define "observability.environment.kafka" -}}
{{- if eq (include "observability.config_type" .) "cloud" -}}
- name: KAFKA_CONNECTION_PARAMS
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.services_secrets_name | quote }}
      key: KAFKA_CONNECTION_PARAMS
{{- end -}}
{{- end -}}

