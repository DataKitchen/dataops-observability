{{/*
Environment
*/}}

{{- define "observability.environment.base" -}}
- name: OBSERVABILITY_CONFIG
  value: {{ .Values.observability.config_type | quote }}
{{- end -}}

{{- define "observability.environment.pythonpath" -}}
- name: PYTHONPATH
  value: {{ .Values.observability.pythonpath | quote }}
{{- end -}}

{{- define "observability.environment.flask" -}}
- name: FLASK_DEBUG
  value: {{ .Values.observability.flask_debug | quote }}
{{- end -}}

{{- define "observability.environment.database" -}}
{{- if eq .Values.observability.config_type "minikube" -}}
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
{{- if eq .Values.observability.config_type "cloud" -}}
- name: KAFKA_CONNECTION_PARAMS
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.services_secrets_name | quote }}
      key: KAFKA_CONNECTION_PARAMS
{{- end -}}
{{- end -}}

{{- define "observability.environment.smtp" -}}
{{- if eq .Values.observability.config_type "cloud" -}}
- name: SMTP_ENDPOINT
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.services_secrets_name | quote }}
      key: SMTP_ENDPOINT
- name: SMTP_PORT
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.services_secrets_name | quote }}
      key: SMTP_PORT
- name: SMTP_USER
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.services_secrets_name | quote }}
      key: SMTP_USER
- name: SMTP_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.services_secrets_name | quote }}
      key: SMTP_PASSWORD
- name: SMTP_FROM_ADDRESS
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.services_secrets_name | quote }}
      key: SMTP_FROM_ADDRESS
      optional: true
{{- else if .Values.observability.smtp -}}
- name: SMTP_ENDPOINT
  value: {{ .Values.observability.smtp.endpoint | quote }}
- name: SMTP_PORT
  value: {{ .Values.observability.smtp.port | quote }}
- name: SMTP_USER
  value: {{ .Values.observability.smtp.user | quote }}
- name: SMTP_PASSWORD
  value: {{ .Values.observability.smtp.password | quote }}
- name: SMTP_FROM_ADDRESS
  value: {{ .Values.observability.smtp.from_address | quote }}
{{- end -}}
{{- end -}}
