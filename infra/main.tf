terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.30.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# -----------------------------------------------------------------------------
# 1. Enable Required GCP APIs
# -----------------------------------------------------------------------------
resource "google_project_service" "enabled_services" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "aiplatform.googleapis.com",
    "documentai.googleapis.com",
    "alloydb.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
    "secretmanager.googleapis.com",
  ])

  service            = each.key
  disable_on_destroy = false
}

# -----------------------------------------------------------------------------
# 2. Artifact Registry Docker Repository
# -----------------------------------------------------------------------------
resource "google_artifact_registry_repository" "docker_repo" {
  depends_on    = [google_project_service.enabled_services]
  location      = var.region
  repository_id = "pitchbuilder-repo"
  description   = "Docker images for Startup Pitch Builder backend"
  format        = "DOCKER"
}

# -----------------------------------------------------------------------------
# 3. VPC & Private Service Networking for AlloyDB
# -----------------------------------------------------------------------------
resource "google_compute_network" "vpc_network" {
  depends_on              = [google_project_service.enabled_services]
  name                    = "pitchbuilder-vpc"
  auto_create_subnetworks = true
}

resource "google_compute_global_address" "private_ip_alloc" {
  name          = "pitchbuilder-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc_network.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
}

# -----------------------------------------------------------------------------
# 4. AlloyDB for PostgreSQL Cluster & Instance (pgvector HNSW)
# -----------------------------------------------------------------------------
resource "google_alloydb_cluster" "alloydb_cluster" {
  depends_on = [google_service_networking_connection.private_vpc_connection]
  cluster_id = var.alloydb_cluster_id
  location   = var.region

  network_config {
    network = google_compute_network.vpc_network.id
  }

  initial_user {
    user     = "postgres"
    password = var.alloydb_password
  }
}

resource "google_alloydb_instance" "primary_instance" {
  cluster       = google_alloydb_cluster.alloydb_cluster.name
  instance_id   = "pitchbuilder-primary-instance"
  instance_type = "PRIMARY"

  machine_config {
    cpu_count = 2
  }

  availability_type = "ZONAL"
}

# -----------------------------------------------------------------------------
# 5. Document AI General Document Processor (for PDF pitch decks)
# -----------------------------------------------------------------------------
resource "google_document_ai_processor" "pitch_parser" {
  depends_on   = [google_project_service.enabled_services]
  location     = "us"
  display_name = "pitch-deck-parser"
  type         = "FORM_PARSER_PROCESSOR"
}

# -----------------------------------------------------------------------------
# 6. Service Account for Cloud Run with Vertex AI & AlloyDB Roles
# -----------------------------------------------------------------------------
resource "google_service_account" "cloud_run_sa" {
  account_id   = "pitchbuilder-cloudrun-sa"
  display_name = "Cloud Run Service Account for Startup Pitch Builder"
}

resource "google_project_iam_member" "vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "docai_user" {
  project = var.project_id
  role    = "roles/documentai.apiUser"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# -----------------------------------------------------------------------------
# 7. Cloud Run Service (FastAPI)
# -----------------------------------------------------------------------------
resource "google_cloud_run_v2_service" "api_service" {
  depends_on = [
    google_project_service.enabled_services,
    google_alloydb_instance.primary_instance
  ]
  name     = var.service_name
  location = var.region

  template {
    service_account = google_service_account.cloud_run_sa.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/backend:latest"

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }

      env {
        name  = "ENVIRONMENT"
        value = "production"
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_REGION"
        value = var.region
      }
      env {
        name  = "GEMINI_MODEL_NAME"
        value = var.gemini_model
      }
      env {
        name  = "DOCUMENT_AI_PROCESSOR_ID"
        value = google_document_ai_processor.pitch_parser.id
      }
      env {
        name  = "VECTOR_DB_TYPE"
        value = "alloydb"
      }
      env {
        name  = "CORS_ORIGINS"
        value = var.frontend_url
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# -----------------------------------------------------------------------------
# 8. Public Access for Cloud Run Service (Allow unauthenticated invocations)
# -----------------------------------------------------------------------------
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.api_service.location
  project  = var.project_id
  service  = google_cloud_run_v2_service.api_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
