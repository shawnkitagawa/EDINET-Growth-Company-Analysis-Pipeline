project_id = "edinet-growth-pipeline"
region     = "asia-northeast1"

bucket_name = "edinet-growth-pipeline-data"

artifact_registry_repo = "edinet-repo"
docker_image_name      = "edinet-pipeline"

cloud_run_job_name = "edinet-pipeline-job"
cloud_run_memory   = "512Mi"
cloud_run_cpu      = "1"
cloud_run_timeout  = "600s"

scheduler_job_name = "edinet-daily-scheduler"
scheduler_cron     = "0 3 * * *"
scheduler_timezone = "Asia/Tokyo"

edinet_api_key_secret_name = "EDINET_API_KEY"

pipeline_runner_service_account_email = "edinet-pipeline-runner@edinet-growth-pipeline.iam.gserviceaccount.com"
scheduler_runner_service_account_email = "cloud-scheduler-runner@edinet-growth-pipeline.iam.gserviceaccount.com"
github_deployer_service_account_email  = "github-actions-deployer@edinet-growth-pipeline.iam.gserviceaccount.com"

github_repo   = "shawnkitagawa/EDINET-Growth-Company-Analysis-Pipeline"
github_branch = "main"

workload_identity_pool_id     = "github-actions-pool"
workload_identity_provider_id = "github-provider"

environment = "dev"