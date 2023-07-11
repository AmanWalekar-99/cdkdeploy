import aws_cdk as core
import aws_cdk.assertions as assertions

from simple_deploy.simple_deploy_stack import SimpleDeployStack

# example tests. To run these tests, uncomment this file along with the example
# resource in simple_deploy/simple_deploy_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SimpleDeployStack(app, "simple-deploy")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
