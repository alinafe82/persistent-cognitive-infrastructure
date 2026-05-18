{{- define "pci.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "pci.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "pci.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "pci.labels" -}}
app.kubernetes.io/name: {{ include "pci.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/part-of: persistent-cognitive-infrastructure
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

