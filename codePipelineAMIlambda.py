from __future__ import print_function
 
import json
import datetime
import time
import boto3
import datetime
import pprint
 
print('Loading function')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    date = datetime.datetime.utcnow().strftime('%Y%M%D-%H_%M_%S')
    imgName = "InstanceID_"+instance_id+"_Image_Backup_"+date
    newLaunchConfigName = 'LC '+ image_Id + ' ' + date
    targetAsgName = 'yourAutoscalingGroupName'


    #configuring clients
    client = boto3.client('ec2')
    autoScalingClient = boto3.client('autoscaling')
    code_pipeline = boto3.client('codepipeline')
   


#    createAMI(getSourceInstanceId(autoScalingClient,"TargetAsgName"), imgName, client)
    CreateImageResponse = client.create_image(InstanceId=getSourceInstanceId(autoScalingClient,targetAsgName), Name=imgName)
    image_Id = CreateImageResponse['ImageId']
    pprint.pprint(image_Id)

    CreateLaunchConfiguration(autoScalingClient,getSourceInstanceId(autoScalingClient,targetAsgName),targetAsgName,newLaunchConfigName, image_Id)
    
    # success notification to codepipeline else lambda will execute infinitely.
    response = code_pipeline.put_job_success_result(
        jobId=event['CodePipeline.job']['id']
    )
    return response

def getSourceInstanceId(autoScalingClient, targetAsgName):
    autoScalingResponse =  autoScalingClient.describe_auto_scaling_groups(AutoScalingGroupNames=[targetAsgName])  
    if not autoScalingResponse['AutoScalingGroups']:
        return 'No such ASG'  
    return autoScalingResponse.get('AutoScalingGroups')[0]['Instances'][0]['InstanceId']




def CreateLaunchConfiguration(autoScalingClient,sourceInstanceId,targetAsgName, newLaunchConfigName, image_Id):
    autoScalingClient.create_launch_configuration(
        InstanceId = sourceInstanceId,
        LaunchConfigurationName=newLaunchConfigName,
        ImageId= image_Id )
    # update ASG to use new LC

    response = autoScalingClient.update_auto_scaling_group(AutoScalingGroupName = targetAsgName ,LaunchConfigurationName = newLaunchConfigName)
    
    return 'Updated ASG  with new launch configuration `%s` which includes AMI `%s`.' % ( newLaunchConfigName, image_Id)

