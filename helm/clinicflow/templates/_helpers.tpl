{{- define "clinicflow.labels" -}}
app.kubernetes.io/part-of: clinicflow
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{- define "clinicflow.databaseUrl" -}}
postgresql+psycopg://$(DB_USER):$(DB_PASSWORD)@postgres:5432/{{ .Values.postgres.database }}
{{- end }}
