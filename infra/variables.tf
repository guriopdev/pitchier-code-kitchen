variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run and AlloyDB deployment"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Name of the Cloud Run FastAPI service"
  type        = string
  default     = "startup-pitch-builder-api"
}

variable "alloydb_cluster_id" {
  description = "Identifier for the AlloyDB cluster"
  type        = string
  default     = "pitchbuilder-alloydb-cluster"
}

variable "alloydb_password" {
  description = "Root password for AlloyDB database"
  type        = string
  sensitive   = true
}

variable "gemini_model" {
  description = "Gemini model version for Vertex AI generation"
  type        = string
  default     = "gemini-2.5-flash"
}

variable "frontend_url" {
  description = "Frontend origin allowed by CORS"
  type        = string
  default     = "https://pitchbuilder.app"
}
