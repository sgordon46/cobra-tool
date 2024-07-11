import os
import pyfiglet
import time
import subprocess
import json
from tqdm import tqdm
from time import sleep
from termcolor import colored
from .report import gen_report
from .report import gen_report_2
from scenarios.scenario_1.scenario_1 import scenario_1_execute
from scenarios.scenario_2.scenario_2 import scenario_2_execute
from scenarios.scenario_2.scenario_2 import scenario_2_destroy
from scenarios.scenario_3.scenario_3 import scenario_3_execute
from scenarios.scenario_4.scenario_4 import scenario_4_execute

def loading_animation():
    chars = "/—\\|"
    for _ in range(10):
        for char in chars:
            print(f"\rLoading {char}", end="", flush=True)
            time.sleep(0.1)


def print_ascii_art(text):
    ascii_art = pyfiglet.figlet_format(text)
    print(colored(ascii_art, color="cyan"))


def get_credentials():
    while True:
        try:
            access_key = input(colored("Enter Access Key: ", color="yellow"))
            if not access_key:
                raise ValueError(colored("Access Key cannot be empty.", color="red"))
            secret_key = input(colored("Enter Secret Key: ", color="yellow"))
            if not secret_key:
                raise ValueError(colored("Secret Key cannot be empty.", color="red"))
            return access_key, secret_key
        except ValueError as e:
            print(e)

def execute_scenario(x):
    try:
        # Call the scenario function from the imported module
        if x == 1:
            scenario_1_execute()
        elif x == 2:
            scenario_2_execute()
        elif x == 3:
            scenario_3_execute()
        elif x == 4:
            scenario_4_execute()
        else: 
            print("Invalid Scenario Selected")
        print(colored("Scenario executed successfully!", color="green"))
    except Exception as e:
        print(colored("Error executing scenario:", color="red"), str(e))

def main(args):

    if(args.verbose is True):print(args)

    tool_name = "C O B R A"
    print("Cloud Provider: "+str(args.cloud_provider))
    print("Scenerio #"+str(args.scenario))
    print("Action: "+str(args.action))
    print_ascii_art(tool_name)

    stack=str(args.cloud_provider)+"-scenario-"+str(args.scenario)
    if(args.verbose is True):print("Pulumi Stack Name: "+str(stack))

    if args.action == "launch":
        subprocess.call("pulumi -C scenarios/scenario_"+str(args.scenario)+"/infra/ stack init "+stack, shell=True)
        execute_scenario(int(args.scenario))
    elif args.action == "status": 
        subprocess.call("pulumi -C scenarios/scenario_"+str(args.scenario)+"/infra/ stack ls -s "+stack, shell=True)
    elif args.action == "destroy": 
        subprocess.call("pulumi -C scenarios/scenario_"+str(args.scenario)+"/infra/ destroy --remove --yes -s "+stack, shell=True)



if __name__ == "__main__":
    main()

