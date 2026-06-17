resource "google_storage_bucket" "edinet_data" {
  name                        = var.bucket_name
  location                    = var.region
  uniform_bucket_level_access = true

  labels = local.common_labels
}