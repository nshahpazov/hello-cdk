import aws_cdk.aws_kms as kms

from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk.aws_ec2 import IVpc
from constructs import Construct


class ECS(Construct):
    """
    Under the ECS construct, we create a
    1. A Fargate cluster
    2. A Fargate task definition
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        alb_security_group: ec2.SecurityGroup,
        alb_target_group: elbv2.ApplicationTargetGroup,
        vpc: IVpc,
        kms_key: kms.IKey,
        ecr_repository_name: str,
        rds_secret: secretsmanager.Secret,
        db_host: str,
        db_port: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        cluster = ecs.Cluster(
            scope=self,
            id="ECSCluster",
            vpc=vpc,
            default_cloud_map_namespace=ecs.CloudMapNamespaceOptions(name="my-app.local"),
            # Optional: for service discovery
        )

        self.cluster_name = cluster.cluster_name

        task_definition = ecs.FargateTaskDefinition(
            self,
            "FargateTaskDefinition",
            memory_limit_mib=1024,
            cpu=512,  # 0.25 vCPU
        )

        # we allow the task to use the KMS key for encryption and decryption
        # since the nodejs app lives in the task, we need to give the task role permission to use the KMS key
        kms_key.grant_encrypt_decrypt(task_definition.task_role)

        # we create a docker container for the task
        container = task_definition.add_container(
            id="AppContainer",
            image=ecs.ContainerImage.from_ecr_repository(
                repository=ecr.Repository.from_repository_name(
                    scope=self,
                    id="MyRepo",
                    repository_name=ecr_repository_name,
                )
            ),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs"),
            environment={
                "DBHOST": db_host,
                "DB_PORT": db_port,
                "DB_NAME": "mydb",
                "REGION": "eu-central-1",
                "KeyId": kms_key.key_id,
            },
            secrets={
                "DBUSER": ecs.Secret.from_secrets_manager(rds_secret, "username"),
                "DBPASS": ecs.Secret.from_secrets_manager(rds_secret, "password"),
            },
        )

        # Add port mapping to the container. This means that the container will listen on port 80.
        # The load balancer will forward traffic to this port.
        container.add_port_mappings(ecs.PortMapping(container_port=80))

        # we need to also add a security group to the ECS service to allow traffic from the load balancer
        self.ecs_security_group = ec2.SecurityGroup(
            scope=self,
            id="ECSSecurityGroup",
            vpc=vpc,
            description="Security group for ECS service",
        )

        # allow traffic from the ALB to the ECS service
        self.ecs_security_group.add_ingress_rule(
            peer=alb_security_group,
            connection=ec2.Port.tcp(80),
            description="Allow traffic from ALB",
        )

        self.fargate_service = ecs.FargateService(
            scope=self,
            id="AppFargateService",
            cluster=cluster,
            task_definition=task_definition,
            security_groups=[self.ecs_security_group],
            desired_count=2,  # for example, run 2 tasks
            assign_public_ip=False,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        # Attach the service to the target group so that ALB can send traffic to it
        self.fargate_service.attach_to_application_target_group(alb_target_group)
