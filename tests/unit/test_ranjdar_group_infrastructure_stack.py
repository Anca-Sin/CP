import aws_cdk as core
import aws_cdk.assertions as assertions

from ranjdar_group_infrastructure.ranjdar_group_infrastructure_stack import RanjdarGroupInfrastructureStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ranjdar_group_infrastructure/ranjdar_group_infrastructure_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RanjdarGroupInfrastructureStack(app, "ranjdar-group-infrastructure")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
