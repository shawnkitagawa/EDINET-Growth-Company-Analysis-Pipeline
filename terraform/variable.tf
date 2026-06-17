variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "asia-northeast1"
}

variable "bucket_name" {
  description = "GCS bucket name for EDINET data"
  type        = string
}

variable "service_account_id" {
  description = "Service account ID for the pipeline runner"
  type        = string
  default     = "edinet-pipeline-runner"
}

variable "artifact_registry_repo" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "edinet-repo"
}

variable "docker_image_name" {
  description = "Docker image name"
  type        = string
  default     = "edinet-pipeline"
}

variable "cloud_run_job_name" {
  description = "Cloud Run Job name"
  type        = string
  default     = "edinet-pipeline-job"
}

variable "cloud_run_memory" {
  description = "Memory for Cloud Run Job"
  type        = string
  default     = "512Mi"
}

variable "cloud_run_cpu" {
  description = "CPU for Cloud Run Job"
  type        = string
  default     = "1"
}

variable "cloud_run_timeout" {
  description = "Cloud Run Job timeout in seconds"
  type        = string
  default     = "600s"
}

variable "scheduler_job_name" {
  description = "Cloud Scheduler job name"
  type        = string
  default     = "edinet-daily-scheduler"
}

variable "scheduler_cron" {
  description = "Cron schedule for Cloud Scheduler"
  type        = string
  default     = "0 3 * * *"
}

variable "scheduler_timezone" {
  description = "Timezone for Cloud Scheduler"
  type        = string
  default     = "Asia/Tokyo"
}

variable "edinet_api_key_secret_name" {
  description = "Secret Manager secret name for EDINET API key"
  type        = string
  default     = "EDINET_API_KEY"
}

variable "github_repo" {
  description = "GitHub repository in owner/repo format"
  type        = string
}

variable "github_branch" {
  description = "GitHub branch allowed to deploy"
  type        = string
  default     = "main"
}

variable "workload_identity_pool_id" {
  description = "Workload Identity Pool ID for GitHub Actions"
  type        = string
  default     = "github-actions-pool"
}

variable "workload_identity_provider_id" {
  description = "Workload Identity Provider ID for GitHub Actions"
  type        = string
  default     = "github-provider"
}