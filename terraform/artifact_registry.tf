resource "google_artifact_registry_repository" "edinet_repo" {
  location      = var.region
  repository_id = var.artifact_registry_repo
  description   = "Docker repository for EDINET pipeline"
  format        = "DOCKER"

  labels = local.common_labels
}