- ALB = Front Door
- Listener = Receptionist at the front door, listening on a port (e.g., 80).
- Target Group = The list of "rooms" or "services" inside your building where requests get routed.
- Targets = EC2 instances, ECS tasks, or IP addresses inside the target group.

Things to learn
- What is an ALB?
- What is a Target Group?
- What is a Target?
- What is a Listener?
- What is a Rule?
- What is a Health Check?
- What is a Load Balancer?
- What is a VPC?
- What is a Subnet?
- What is a Security Group?
- What is a Route Table?
- What is a NAT Gateway?
- What is a Route 53?
- What is a CloudFront?
- What is a CloudWatch?
- What is a CloudTrail?


Things to learn regarding ECS
- What is ECS?
- What is a Fargate?
- What is a Task?
- What is a Service?
- What is a Cluster?
- What is a Container?
- What is a Task Definition?
- What is a Service Discovery?
- What is a Load Balancer?
- What is a Service Mesh?
- What is a Service Discovery?

### ECS and Fargate

## ECS Task Definition
- The Task Definition is like a blueprint. It defines:
- Which Docker image to use
- How much CPU/memory
- Environment variables
- Networking mode
- IAM roles
- Logging (CloudWatch)
- Secrets
- Port mappings
- Volumes (optional)

### ECS Service
- Defines desired count of tasks (e.g., "I want 2 tasks running at all times.")
- Handles restarts if tasks crash.
- Handles rolling updates (zero-downtime deployments).
- Connects to load balancers.
- Makes it easier to scale (auto-scaling, service discovery).
