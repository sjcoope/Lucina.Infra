
from __future__ import print_function
import sys
import datetime
import argparse

from common import utility
from common.parameters import Parameters
from common.cf_helper import CFHelper

def main():
    # Create CFHelper
    cf_helper = CFHelper("sjcnet-lucina")

    parser = argparse.ArgumentParser()
    parser.add_argument("stack_name", help="The CFN stack to update")
    parser.add_argument("template", help="The CFN Template to update the stack")
    parser.add_argument("environment", help="The name of the environment to build")
    args = parser.parse_args()

    # Create the parameters object
    parameters = Parameters(args.environment, "Lucina", args.stack_name)

    # Validate and output args
    args.environment = args.environment.lower()
    utility.log('ARGS: ' + str(args))

     # Check if stack exists, if not create it
    if(cf_helper.stack_exists(args.stack_name)==False):
        utility.log('Stack does NOT exist')
        
        if(cf_helper.create_stack(args.stack_name, args.template, parameters)==True):
           utility.log('Stack successfully created')
        else:
            utility.log('Stack creation failed') 

    else:
        utility.log('Stack Exists')

        # Create change set name
        changeset_name = parameters.application + "-" + parameters.environment + "-Changeset-"+datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        utility.log("ChangeSet Name: " + changeset_name)

        # Create change set and check status
        if cf_helper.create_change_set(args.stack_name, args.template, changeset_name, parameters):
            status=cf_helper.get_change_set_status(args.stack_name, changeset_name)
            utility.log("Status: " + status)

            if(status=="Success"):
                if cf_helper.execute_change_set(args.stack_name, changeset_name):
                    utility.log("Stack update complete")
                else:
                    utility.log("Stack update FAILED")
                    sys.exit(1)
            else:
                if(status=="NoChanges"):
                    utility.log("No changes in CF template.")
                else:
                    sys.exit(1)
        else:
            utility.log("Create ChangeSet FAILED")
            sys.exit(1)

    #delete_s3_bucket(temp_bucket_name)

if __name__ == "__main__":
    main()