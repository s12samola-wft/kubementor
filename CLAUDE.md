# CLAUDE.md

## Deployment target: terraform-aws-platform

KubeMentor will be deployed on my separate Terraform + AWS project
(github.com/s12samola-wft/terraform-aws-platform, region ca-central-1).
Keep every change compatible with this contract:

- Port: the container listens on 8000 (gunicorn). Don't change it
  without flagging that the platform's security group, load balancer
  and Kubernetes manifests must change too.
- /health = liveness (load balancer health check + K8s liveness probe).
  /ready = readiness (K8s readiness probe). Both must stay fast, need no
  auth, and return HTTP 200 when OK.
- Config only via environment variables. APP_ENV=production and
  SECRET_KEY are injected at runtime (K8s Secret first, later AWS
  Parameter Store or Vault + External Secrets). Never bake secrets
  into the image or commit them.
- Handover point: CI (Jenkins in a Docker container on the laptop,
  not built yet) must test, scan (Trivy), build and push the image to
  Docker Hub at docker.io/samayohub/kubementor with an immutable tag
  (git SHA) plus a version tag. The platform pulls that image, using
  Docker Hub credentials (imagePullSecret / docker login) to avoid
  anonymous pull rate limits behind the NAT gateway.
- Image must stay small, non-root, pinned base digest, hashed deps,
  so it fits a t3.small k3s node (2 GB RAM).
- Platform timeline: EC2 + hardening (Days 4-5), load balancer + private
  subnets + NAT (Day 8), Docker Compose on EC2 (Day 12), k3s with
  Deployment/Service/Ingress and probes (Days 13-14).

When a change I ask for would break this contract, tell me before
making it and explain the impact on the platform.
