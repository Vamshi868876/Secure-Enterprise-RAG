# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability, please email **vamshi@example.com** instead of using the issue tracker.

## Security Guidelines

### Authentication
- JWT tokens validate all API requests
- Tokens signed with secure keys
- Tokens expire after configured duration

### Authorization
- RBAC enforced at vector retrieval level
- Role-based document filtering at database level
- Users cannot bypass security filters

### Data Protection
- TLS 1.3 for all data in transit
- AES-256 encryption at rest
- Database passwords in secure vault
- Redis password protected

### Audit Logging
- All queries logged with user role
- Failed auth attempts tracked
- Configuration changes audited
- Logs encrypted and retained per policy

## Deployment Security

1. Run container as non-root user
2. Enable read-only file systems where possible
3. Use network policies to restrict traffic
4. Enable security scanning in CI/CD

## Vulnerability Disclosure

1. Acknowledge receipt within 48 hours
2. Assess severity and impact
3. Develop and test fix
4. Release patched version
5. Publicly disclose after patch available

## Security Patches

We release security patches for currently released versions.

Check [Releases](https://github.com/Vamshi868876/Secure-Enterprise-RAG/releases) for available patches.
