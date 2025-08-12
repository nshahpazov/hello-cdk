#!/usr/bin/env python3
import aws_cdk as cdk

from hello_cdk.workshops.operational_excellence.stacks import BaselineResourcesStack


app = cdk.App()
BaselineResourcesStack(
    scope=app,
    construct_id="BaselineResourcesStack",
)

app.synth()
