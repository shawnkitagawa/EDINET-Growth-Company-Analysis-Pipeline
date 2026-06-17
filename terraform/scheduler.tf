resource "google_cloud_scheduler_job" "edinet_daily_scheduler" {
    name          = var.scheduler_job_name
    description   = "Runs the EDINET pipeline daily"
    region        = var.region 

    schedule      = var.scheduler_cron 
    time_zone     = var.scheduler_timezone 

    http_target {
        http_method = "POST"

        uri = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${var.cloud_run_job_name}:run"


        oauth_token {
            service_account_email = google_service_account.pipeline_runner.email
        }
    }


    depends_on = [
        google_cloud_run_v2_job.edinet_pipeline_job
    ]
}