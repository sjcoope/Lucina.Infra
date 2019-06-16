import datetime
import sys
from common import utility
from common.parameters import Parameters
from common.cf_helper import CFHelper

class DeploymentHelper:
    def __init__(self, service_name, template, environment, parameters):
        self.service_name = service_name
        self.template = template
        self.environment = environment
        self.parameters = parameters
        self.cf_helper = CFHelper()

    def deploy(self):

        # Check if stack exists, if not create it
        if(self.cf_helper.stack_exists(self.service_name)==False):
            utility.log('Stack does NOT exist')
            
            if(self.cf_helper.create_stack(self.parameters.service_name, self.template, self.parameters)==True):
                utility.log('Stack successfully created')
            else:
                utility.log('Stack creation failed') 

        else:
            utility.log('Stack Exists')

            # Create change set name
            changeset_name = self.parameters.application + "-" + self.parameters.environment + "-Changeset-"+datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
            utility.log("ChangeSet Name: " + changeset_name)

            # Create change set and check status
            if self.cf_helper.create_change_set(self.service_name, self.template, changeset_name, self.parameters):
                status=self.cf_helper.get_change_set_status(self.service_name, changeset_name)
                utility.log("Status: " + status)

                if(status=="Success"):
                    if self.cf_helper.execute_change_set(self.service_name, changeset_name):
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
