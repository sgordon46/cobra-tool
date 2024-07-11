

import argparse
from core import main
from textwrap import dedent


def parse_arguments():
    parser = argparse.ArgumentParser(description="Terminal-based option tool",formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-c","--cloud-provider", choices=["aws", "azure", "gcp"],default="aws", help="Cloud provider to use for deployment")
    parser.add_argument("-a","--action", choices=["launch", "status", "destroy"],default="launch", help="Action to perform")
    #parser.add_argument("--simulation", action="store_true", help="Enable simulation mode")#Future add validation & assessment 
    parser.add_argument("-s","--scenario", choices=range(1, 5), default="1", type=int,help=dedent('''\
    
    1. Exploit Vulnerable Application, EC2 takeover, Credential Exfiltration & Anomalous Compute Provisioning.
    2. Rest API exploit - command injection, credential exfiltration from backend lambda and privilige escalation, rogue identity creation & persistence
    3. Compromising a web app living inside a GKE Pod, access pod secret, escalate privilege, take over the cluster
    4. Exfiltrate EC2 role credentials using IMDSv2 with least privileged access\n
    '''))
    parser.add_argument("-v","--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args()

#def main_function(cloud_provider, action, simulation, scenario):
    # Call the main function from the imported module and pass the options
#    main.main(cloud_provider, action, simulation, scenario)

if __name__ == "__main__":
    args = parse_arguments()
    
    # Convert argparse Namespace to dictionary
    #options = vars(args)
    
    # Call the main function with options
    main.main(args)
