output "cloud_run_url" {
  description = "Public URL of the deployed Cloud Run FastAPI service"
  value       = google_cloud_run_v2_service.api_service.uri
}

output "artifact_registry_repo" {
  description = "Artifact Registry Docker repository path"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}"
}

output "alloydb_cluster_name" {
  description = "Name of the created AlloyDB cluster"
  value       = google_alloydb_cluster.alloydb_cluster.name
}

output "document_ai_processor_id" {
  description = "ID of the Document AI pitch deck parser processor"
  value       = google_document_ai_processor.pitch_parser.id
}
