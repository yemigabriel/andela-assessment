output "frontend_bucket_name" {
  value = aws_s3_bucket.frontend.bucket
}

output "memory_bucket_name" {
  value = aws_s3_bucket.memory.bucket
}

output "api_gateway_url" {
  value = aws_apigatewayv2_api.backend.api_endpoint
}

output "cloudfront_domain_name" {
  value = aws_cloudfront_distribution.frontend.domain_name
}
