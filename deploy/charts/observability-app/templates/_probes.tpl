{{/*
Command-based readiness probe
*/}}

{{- define "observability.probes.readiness_cmd" -}}
readinessProbe:
  exec:
    command:
      - /dk/bin/{{ . }}
      - --check-ready
  # We are not polling this too often and also have a generous timeout because the check ready action waits the ready
  # condition to be reached when the service is not ready right away. This allows us to have a tight switch to the
  # new pod, potentially reducing the overall deployment time
  periodSeconds: 30
  timeoutSeconds: 60
{{- end -}}
