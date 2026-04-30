variable "project_name" {
  description = "Base name for Meridian support infrastructure"
  type        = string
  default     = "meridian-support"
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "frontend_bucket_name" {
  description = "S3 bucket name for frontend static assets"
  type        = string
}

variable "memory_bucket_name" {
  description = "S3 bucket name for conversation memory storage"
  type        = string
}

variable "lambda_package_path" {
  description = "Path to the packaged backend Lambda zip"
  type        = string
  default     = "../dist/backend.zip"
}

variable "openai_api_key" {
  description = "OpenAI API key for the backend Lambda"
  type        = string
  sensitive   = true
}

variable "cors_allow_origins" {
  description = "Comma-separated or JSON-array CORS origins for the backend"
  type        = string
  default     = "http://localhost:3000"
}
