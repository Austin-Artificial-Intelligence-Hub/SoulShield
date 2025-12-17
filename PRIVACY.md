# Privacy & Security Features

## Data Protection

### Encryption
- **At Rest**: DynamoDB tables use AWS-managed encryption (AES-256)
- **In Transit**: All API calls use TLS 1.2+
- **API Keys**: Stored securely in AWS API Gateway

### Data Retention
- Configurable TTL (Time To Live) on chat history
- Default: 30 days, then automatic deletion
- No backups of chat content
- Point-in-time recovery available for accidental deletions (24 hours)

### Logging Policy
- **CloudWatch Logs**: Error-level only
- **No Content Logging**: Chat messages never logged
- **Metadata Only**: Request IDs, timestamps, error types
- **Log Retention**: 7 days maximum

## Access Controls

### API Authentication
- API Key required for all requests
- Rate limiting: 10 requests/second, burst 20
- Keys rotatable without downtime

### IAM Permissions
- Lambda: Least-privilege access to DynamoDB and Bedrock only
- No cross-account access
- No public read access to any resources

### Network Security
- API Gateway: Regional endpoint (not edge-optimized for privacy)
- No VPC required (serverless)
- Optional: Deploy in VPC for additional isolation

## Data Minimization

### What We Store
- Session ID (UUID)
- Message content (encrypted at rest)
- Timestamp
- Role (user/assistant)

### What We Don't Store
- User IP addresses
- User identifiers beyond session
- Request headers
- Geolocation data
- Device information

## Compliance Considerations

This architecture supports:
- **GDPR**: Right to deletion (via session ID), data minimization, encryption
- **CCPA**: Data deletion, no sale of data
- **HIPAA**: Encryption, access controls (requires BAA with AWS)

### Additional Steps for HIPAA
1. Sign AWS Business Associate Agreement
2. Enable CloudTrail for audit logs
3. Deploy Lambda in VPC
4. Use AWS KMS customer-managed keys
5. Implement additional access logging

## Third-Party Data Sharing

### AWS Bedrock
- Data not used for model training
- Processed in your AWS account/region
- See: https://aws.amazon.com/bedrock/data-privacy/

### OpenAI (if used)
- Data may be used for abuse monitoring (30 days)
- Not used for training by default
- See: https://openai.com/enterprise-privacy

## Recommendations

1. **Use Bedrock** for maximum privacy (data stays in AWS)
2. **Rotate API keys** regularly (every 90 days)
3. **Monitor access logs** for unusual patterns
4. **Set shortest acceptable TTL** for your use case
5. **Enable CloudTrail** for compliance auditing
6. **Use VPC deployment** for sensitive applications

## User Rights

Users can request:
- **Data Access**: Query DynamoDB by session ID
- **Data Deletion**: Delete session from DynamoDB
- **Data Export**: Export conversation history

Implement these via additional API endpoints as needed.
