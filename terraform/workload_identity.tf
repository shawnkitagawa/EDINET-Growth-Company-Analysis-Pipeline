resource "google_iam_workload_identity_pool" "github_actions_pool" {
  workload_identity_pool_id = var.workload_identity_pool_id
  display_name              = "GitHub Actions Pool"
  description               = "Workload Identity Pool for GitHub Actions"
}

resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_actions_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = var.workload_identity_provider_id
  display_name                       = "github-actions-provider"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
    "attribute.ref"        = "assertion.ref"
  }

  attribute_condition = "assertion.repository == \"shawnkitagawa/EDINET-Growth-Company-Analysis-Pipeline\" && assertion.ref == \"refs/heads/main\""
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}