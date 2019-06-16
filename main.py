import argparse
from common.deployment_helper import DeploymentHelper
from common import utility
from common.parameters import Parameters

def main():
    # # Get args
    # parser = argparse.ArgumentParser()
    # parser.add_argument("service_name", help="The name of the service (used for the stack name too)")
    # parser.add_argument("template", help="The CFN Template to update the stack")
    # parser.add_argument("environment", help="The name of the environment to build")
    # parser.add_argument("config", help="The config file to use in building the stack")
    # args = parser.parse_args()

    # # Test args
    # # TODO

    # parameters = Parameters(config)
    # deploymentHelper = DeploymentHelper(args.service_name, args.template, args.environment, parameters)
    # deploymentHelper.deploy()

    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="The config file to use in building the stack")
    args = parser.parse_args()

    parameters = Parameters(args.config)
    if (parameters.isValid()):
        deploymentHelper = DeploymentHelper(args.service_name, args.template, args.environment, parameters)
        deploymentHelper.deploy()
    else:
        utility.log('Parameters are invalid.  Cannot continue')

if __name__ == "__main__":
    main()
