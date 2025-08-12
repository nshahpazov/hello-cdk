import aws_cdk as core
import pytest

from aws_cdk import Stack
from aws_cdk.aws_ec2 import SecurityGroup, Vpc
from aws_cdk.aws_elasticloadbalancingv2 import (
    ApplicationListener,
    ApplicationLoadBalancer,
    ApplicationProtocol,
    ApplicationTargetGroup,
)

from hello_cdk.constructs.load_balancer import LoadBalancer


@pytest.fixture(name="test_stack")
def mock_test_stack():
    app = core.App()
    return Stack(app, "TestStack")


class TestLoadBalancerConstruct:
    def test_init(self, test_stack: Stack) -> None:
        """ """
        vpc = Vpc(test_stack, "TestVPC", max_azs=2)
        lb = LoadBalancer(test_stack, "LoadBalancer", vpc=vpc)

        assert isinstance(lb.security_group, SecurityGroup)
        assert isinstance(lb.load_balancer, ApplicationLoadBalancer)
        assert isinstance(lb.listener, ApplicationListener)
        assert isinstance(lb.target_group, ApplicationTargetGroup)
