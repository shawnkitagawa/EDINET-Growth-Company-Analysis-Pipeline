resource "google_service_account" "pipeline_runner" {
  account_id   = var.service_account_id
  display_name = "EDINET Pipeline Runner"
}

resource "google_storage_bucket_iam_member" "pipeline_bucket_writer" {
  bucket = google_storage_bucket.edinet_data.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.pipeline_runner.email}"
}

resource "google_secret_manager_secret_iam_member" "pipeline_secret_accessor" {
  project   = var.project_id
  secret_id = var.edinet_api_key_secret_name
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.pipeline_runner.email}"
}