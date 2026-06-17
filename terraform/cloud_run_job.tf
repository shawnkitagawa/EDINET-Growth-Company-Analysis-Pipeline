resource "google_cloud_run_v2_job" "edinet_pipeline_job" {
  name     = var.cloud_run_job_name
  location = var.region

  template {
    template {
      service_account = "edinet-pipeline-runner@edinet-growth-pipeline.iam.gserviceaccount.com"

      containers {
        image = local.image_url

        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }

        env {
          name  = "GCS_BUCKET_NAME"
          value = var.bucket_name
        }

        env {
          name  = "EDINET_API_KEY_SECRET_NAME"
          value = var.edinet_api_key_secret_name
        }

        resources {
          limits = {
            cpu    = var.cloud_run_cpu
            memory = var.cloud_run_memory
          }
        }
      }

      timeout = var.cloud_run_timeout
      max_retries = 1
    }
  }
  labels = local.common_labels

  depends_on = [
    google_artifact_registry_repository.edinet_repo,
    google_service_account.pipeline_runner,
    google_secret_manager_secret_iam_member.pipeline_secret_accessor,
    google_storage_bucket_iam_member.pipeline_bucket_writer
]
}