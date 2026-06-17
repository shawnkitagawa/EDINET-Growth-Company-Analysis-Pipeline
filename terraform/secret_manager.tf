resource "google_secret_manager_secret" "edinet_api_key" {
  secret_id = var.edinet_api_key_secret_name

  replication {
    auto {}
  }

  labels = local.common_labels
}