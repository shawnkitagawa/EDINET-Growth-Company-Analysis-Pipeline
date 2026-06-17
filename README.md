# EDINET Financial Disclosure Data Platform with Snowflake, dbt, and AI Agents

This project is a production-style data and AI engineering platform for collecting, storing, transforming, and preparing EDINET financial disclosure data for growth company analysis and future AI-powered financial workflows.

The current focus is building a reliable cloud-based financial data pipeline using Python, GCP, Terraform, CI/CD, Snowflake, and dbt. The next direction is to extend the platform toward AI-assisted financial analysis, likely using Snowflake Cortex Agent and cost-conscious Snowflake development practices.

## Architecture

![Architecture Diagram](architecture/edinet_snowflake_rag_architecture.png)

## Project Direction

This project is being developed as a practical fintech data and AI engineering system.

The current stage focuses on:

* EDINET data ingestion
* cloud deployment with GCP
* infrastructure management with Terraform
* CI/CD with GitHub Actions
* raw financial data storage in Google Cloud Storage
* Snowflake RAW layer design
* dbt-based transformation design
* preparing the foundation for AI and agent-based financial analysis

The next stage will likely involve building AI-powered workflows with Snowflake Cortex Agent, including natural-language interaction with financial data, document/data extraction support, and quality-conscious LLM system design.

## Main Components

### EDINET External API

The pipeline retrieves financial disclosure data from the EDINET API, including filing metadata and financial statement CSV files.

### Python Ingestion Pipeline

The Python pipeline fetches EDINET metadata and document CSV files, handles retries and failures, and saves raw files into Google Cloud Storage.

The pipeline is designed to support:

* metadata collection
* financial document CSV download
* ZIP extraction
* failed document tracking
* GCS upload
* testable API key injection
* Secret Manager-based credential loading during real execution

### Google Cloud Platform

GCP is used to run and operate the ingestion pipeline in a cloud environment.

Current GCP components include:

* Cloud Run Jobs
* Cloud Scheduler
* Google Cloud Storage
* Artifact Registry
* Secret Manager
* IAM service accounts
* Workload Identity for GitHub Actions authentication

### Terraform Infrastructure

Terraform is used to manage the GCP infrastructure.

The infrastructure setup includes:

* storage bucket
* Artifact Registry repository
* Cloud Run Job
* Cloud Scheduler
* Secret Manager access
* IAM permissions
* GitHub Actions Workload Identity setup

### CI/CD with GitHub Actions

GitHub Actions is used for continuous integration and deployment preparation.

Current CI work includes:

* Python import checks
* pytest test execution
* dependency management with `uv`
* avoiding cloud credential loading during import
* making pipeline functions testable with fake API keys
* preparing the project for safe cloud deployment

### Google Cloud Storage

Google Cloud Storage is used as the raw data lake.

Raw EDINET files are stored before being loaded into Snowflake.

Example storage paths:

```text
raw/metadata/
raw/documents/
raw/reference/
```

### Snowflake RAW Layer

Snowflake is planned as the main warehouse for storing and querying EDINET data.

The RAW layer stores ingested EDINET data in its original or minimally processed form.

Expected RAW tables include:

* document metadata
* company master data
* annual report financial values

### Snowpipe

Snowpipe is planned to load newly added files from Cloud Storage into Snowflake RAW tables using cloud notifications.

This allows new EDINET files uploaded to GCS to be automatically ingested into Snowflake.

### dbt Transformations

dbt will transform RAW tables into clean, structured analytics models.

The transformation flow is organized into:

* staging
* intermediate
* marts

The dbt layer will handle cleaning, deduplication, latest-version selection, financial metric extraction, and growth company analysis.

### Snowflake MARTS Layer

The MARTS layer will contain analytics-ready tables used for growth company analysis.

Example marts include:

* `mart_company_growth`
* `mart_high_growth_companies`
* `mart_industry_growth_summary`
* `mart_company_financial_trends`

### AI / Agent Preparation

The project is moving toward AI-powered financial analysis using Snowflake and LLM-related tools.

The likely next direction is Snowflake Cortex Agent, which can support natural-language workflows over structured and semi-structured financial data.

Potential use cases include:

* asking questions over financial disclosure data
* retrieving company financial metrics
* explaining growth trends
* comparing companies or industries
* combining SQL-based retrieval with document-based context
* supporting internal financial data workflows

## Planned Cortex Agent Direction

The planned AI layer may use Snowflake Cortex Agent to allow users to interact with EDINET financial data through natural language.

Example questions:

```text
Which companies have revenue growth above 40%?
Why is this company considered high growth?
What are the main growth drivers mentioned in the filing?
Compare the growth factors of two companies.
Which industries contain the most high-growth companies?
```

The system direction is to combine:

* structured retrieval from Snowflake tables for exact financial metrics
* document or disclosure text retrieval for explanations and evidence
* agent-style workflows for financial analysis tasks
* cost-conscious usage of Snowflake AI tools

## Current Scope

The current project scope focuses on the first production-style stage:

* EDINET API ingestion
* Python data pipeline development
* GCS raw data storage
* Secret Manager integration
* Cloud Run Job deployment
* Cloud Scheduler automation
* Terraform infrastructure management
* GitHub Actions CI/CD
* pytest-based pipeline testing
* Snowflake RAW layer design
* dbt transformation planning
* AI-agent-ready data preparation

The application and agent layer can be added in the next stage.

## Technologies

* Python
* SQL
* Google Cloud Platform
* Cloud Run Jobs
* Cloud Scheduler
* Google Cloud Storage
* Artifact Registry
* Secret Manager
* Terraform
* GitHub Actions
* Workload Identity
* Docker
* pytest
* uv
* Snowflake
* Snowpipe
* dbt
* Snowflake Cortex Agent
* RAG / AI agent preparation

## Environment Variables

The pipeline uses environment variables for cloud execution.

Required variables include:

```env
GCP_PROJECT_ID=your_gcp_project_id
EDINET_API_KEY_SECRET_NAME=your_secret_name
GCS_BUCKET_NAME=your_gcs_bucket_name
```

The actual EDINET API key is stored in Google Secret Manager and loaded during real pipeline execution.

For local testing, functions are designed to accept fake API keys so tests do not require real GCP credentials.

## Local Development

Install dependencies with `uv`:

```bash
uv sync
```

Run import check:

```bash
uv run python -c "import pipeline.main; print('Pipeline import OK')"
```

Run tests:

```bash
uv run pytest tests/pipeline/
```

## Docker Execution

Build the Docker image:

```bash
docker build -t edinet-growth-platform .
```

Run the pipeline:

```bash
docker run --env-file .env edinet-growth-platform
```

## Cloud Deployment Direction

The cloud deployment direction uses:

* GitHub Actions for CI/CD
* Workload Identity for secure authentication from GitHub to GCP
* Artifact Registry for Docker images
* Cloud Run Jobs for executing the pipeline
* Cloud Scheduler for daily automation
* Secret Manager for EDINET API key storage
* GCS for raw EDINET data storage

## License

This repository is currently intended for private project development.

All rights reserved.
