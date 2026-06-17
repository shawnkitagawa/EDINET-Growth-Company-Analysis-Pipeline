provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  image_url = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/${var.docker_image_name}:latest"

  common_labels = {
    project     = "edinet-growth-pipeline"
    environment = var.environment
    managed_by  = "terraform"
  }
}