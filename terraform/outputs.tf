output "bucket_name" {
  description = "Name of the GCS bucket used for EDINET data"
  value       = google_storage_bucket.edinet_data.name
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository for Docker images"
  value       = google_artifact_registry_repository.edinet_repo.name
}

output "docker_image_url" {
  description = "Docker image URL used by the Cloud Run Job"
  value       = local.image_url
}

output "pipeline_runner_service_account_email" {
  description = "Service account used by the EDINET pipeline Cloud Run Job"
  value       = google_service_account.pipeline_runner.email
}

output "cloud_run_job_name" {
  description = "Name of the Cloud Run Job"
  value       = google_cloud_run_v2_job.edinet_pipeline_job.name
}

output "scheduler_job_name" {
  description = "Name of the Cloud Scheduler job"
  value       = google_cloud_scheduler_job.edinet_daily_scheduler.name
}

output "secret_name" {
  description = "Name of the EDINET API key secret"
  value       = google_secret_manager_secret.edinet_api_key.secret_id
}