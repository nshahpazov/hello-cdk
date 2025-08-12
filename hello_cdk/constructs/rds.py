import aws_cdk as core
import aws_cdk.aws_kms as kms
import aws_cdk.aws_rds as rds

from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class RDS(Construct):
    """ """

    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.IVpc,
        **kwargs,
    ) -> None:
        super().__init__(scope=scope, id=id, **kwargs)

        self.secret = secretsmanager.Secret(
            scope=self,
            id="RDSSecret",
            description="This is the secret for my RDS instance",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                # the template is the base to which we add the generated password
                secret_string_template='{"username": "niki"}',
                # here we generate a password instead of writing it ourselves
                generate_string_key="password",
                password_length=16,
                exclude_characters="\"@/\\'",
            ),
        )

        # we need a security group for the rds under the vpc
        self.security_group = ec2.SecurityGroup(
            scope=self,
            id="RDSSecurityGroup",
            vpc=vpc,
            description="Security group for RDS instance",
        )

        self.instance = rds.DatabaseInstance(
            scope=self,
            id="RDSInstance",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.security_group],
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_32
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            credentials=rds.Credentials.from_secret(self.secret),  # type: ignore[arg-type]
            database_name="mydb",
            publicly_accessible=False,
            deletion_protection=False,
            removal_policy=core.RemovalPolicy.DESTROY,
            # no backup
            backup_retention=core.Duration.days(0),
            # no monitoring
            monitoring_interval=core.Duration.minutes(0),
            # no performance insights
            enable_performance_insights=False,
        )
