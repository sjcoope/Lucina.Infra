import boto3
from common import utility
from botocore.exceptions import ClientError, WaiterError

# Globals
application_name = "sjcnet-edesia"

class CFHelper:
    def __init__(self):
        self.__getCFClient__()

    @classmethod
    def __getCFClient__(self):
        """
        Creates boto3 client.
        """
        try:
            self.cf = boto3.client('cloudformation')
        except ClientError as err:
            raise Exception("Failed to create boto3 client.\n" + str(err))
    

    @classmethod
    def create_stack(self, stack_name, template, parameters):
        
        try:
            with open(template, 'r') as myfile:
                data=myfile.read()

            self.cf.create_stack(
                StackName=stack_name, 
                TemplateBody=data,
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Parameters=parameters
            )

            result = self.wait_for_stack_create_complete(stack_name)

            return result
        except ClientError as err:
            utility.log("Failed to create stack and change set. Check CloudFormation events for more information. \n" + str(err))
            return False
        return True
        

    @classmethod
    def create_change_set(self, stack_name, template, change_set_name, parameters):
        """
        Creates a changeset and checks changes exist before performing update.
        """
        try:
            response = self.cf.create_change_set(
                StackName=stack_name,
                TemplateBody=open(template, 'r').read(),
                Capabilities=['CAPABILITY_NAMED_IAM'],
                ChangeSetName=change_set_name,
                Parameters=parameters
            )
            return response
        except ClientError as err:
            utility.log("Failed to create change set.\n" + str(err))
            return False
        except IOError as err:
            utility.log("Failed to access " + template + ".\n" + str(err))
            return False


    @classmethod
    def get_change_set_info(self, stack_name, change_set_name):
        """
        Gets the status of a changeset, i.e. if it's created successfully, failed or failed because 
        it didn't contain any changes.
        """
        try:
            response = self.cf.describe_change_set(
                ChangeSetName=change_set_name,
                StackName=stack_name
            )
            
            return response
        except ClientError as err:
            utility.log("Failed to describe change set" \
                "Check CloudFormation events for more information. \n" + str(err))
            return False
        return True 


    @classmethod
    def get_change_set_status(self, stack_name, change_set_name):
        self.wait_for_stack_create_change_set(stack_name, change_set_name)

        # Check the status of the change set.    
        response = self.get_change_set_info(stack_name, change_set_name)

        status="Failed"
        if(response["Status"]=="CREATE_COMPLETE"):
            status="Success"
        else:
            # Failed - Check why
            utility.log("Failed Reason: " + response["StatusReason"])
            if("didn't contain changes" in response["StatusReason"]):
                status="NoChanges"

        return status


    @classmethod
    def wait_for_stack_create_change_set(this, stack_name, change_set_name):
        """
        Checks the create change set status of the CFN stack
        until it either succeeds or fails
        """
        try:
            waiter = this.cf.get_waiter('change_set_create_complete')
            waiter.config.delay=5
            waiter.config.max_attempts=5
        except WaiterError as err:
            utility.log("Failed to get the waiter.\n" + str(err))
        try:
            utility.log("Waiting - Create Change Set - " + change_set_name + " " + stack_name)
            waiter.wait(
                ChangeSetName=change_set_name,
                StackName=stack_name
            )
        except WaiterError as err:
            utility.log("The Stack Create Change Set did not successfully complete.  " \
                "Check CloudFormation events for more information. \n" + str(err))


    @classmethod
    def execute_change_set(self, stack_name, change_set_name):
        """
        Executes a change set
        """
        try:
            self.cf.execute_change_set(
                StackName=stack_name,
                ChangeSetName=change_set_name,
            )

            # Wait for the update to complete
            self.wait_for_stack_update_complete(stack_name)

            # Check the stack status 
            response = self.get_stack_info(stack_name)
            if(response["Stacks"][0]["StackStatus"]=="UPDATE_COMPLETE"):
                return True
            else:
                return False

        except ClientError as err:
            utility.log("Failed to execute change set.\n" + str(err))
            return False


    @classmethod
    def wait_for_stack_create_complete(self, stack_name):
        """
        Waits for the stack to create (or fail)
        """
        try:
            waiter = self.cf.get_waiter('stack_create_complete')
            waiter.config.delay=5
            waiter.config.max_attempts=30
        except WaiterError as err:
            utility.log("Failed to get the waiter.\n" + str(err))
            return False
        try:
            utility.log("Waiting - Create Stack - " + " " + stack_name)
            waiter.wait(StackName=stack_name)
        except WaiterError as err:
            utility.log("The Stack Create did not successfully complete.  " \
                "Check CloudFormation events for more information. \n" + str(err))
            return False
        return True


    @classmethod
    def wait_for_stack_update_complete(self, stack_name):
        """
        Waits for the stack to update (or fail)
        """
        try:
            waiter = self.cf.get_waiter('stack_update_complete')
            waiter.config.delay=5
            waiter.config.max_attempts=30
        except WaiterError as err:
            utility.log("Failed to get the waiter.\n" + str(err))
        try:
            utility.log("Waiting - Update Stack - " + " " + stack_name)
            waiter.wait(
                StackName=stack_name
            )
        except WaiterError as err:
            utility.log("The Stack Update did not successfully complete.  " \
                "Check CloudFormation events for more information. \n" + str(err))


    @classmethod
    def get_stack_info(self, stack_name):
        """
        Gets the status of a changeset, i.e. if it's created successfully, failed or failed because 
        it didn't contain any changes.
        """
        try:
            response = self.cf.describe_stacks(
                StackName=stack_name
            )
            return response
        except ClientError as err:
            utility.log("Failed to describe change set" \
                "Check CloudFormation events for more information. \n" + str(err))
            return False
        return True 


    @classmethod
    def stack_exists(self, stack_name):
        stacks = self.cf.list_stacks()['StackSummaries']
        for stack in stacks:
            if stack['StackStatus'] == 'DELETE_COMPLETE':
                continue
            if stack_name == stack['StackName']:
                return True
        return False
