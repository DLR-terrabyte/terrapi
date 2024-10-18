import os
import json
import requests

url = "https://slurmrest.terrabyte.lrz.de/slurm/v0.0.37/job/submit"

# Obtained from terrapi, please adjust both variables
access_token = "xxx"
working_directory = "/tmp"

# Define the job payload, adjust project paths i.e `current_working_directory`, `standard_output` and `standard_error`
payload = {
    "job": {
        "name": "hello-tby-slurmrest",
        "partition": "hpda2_compute",
        "ntasks":1,
        "nodes": 1,
        "current_working_directory": working_directory,
        "standard_input": "/dev/null",
        "standard_output": os.path.join(working_directory, "hello.out"),
        "standard_error": os.path.join(working_directory, "hello.error"),
        "environment": {
            "PATH": "/bin:/usr/bin/:/usr/local/bin/",
            "LD_LIBRARY_PATH": "/lib/:/lib64/:/usr/local/lib"
        }
    },
    "script": "#!/bin/bash\necho '[0xCB50B2] I am from the REST API called by Python'"
}

# Define the headers with the token
headers = {
    "Authorization": f"Bearer {access_token}"
}


# Submit the job with headers
response = requests.post(url, json=payload, headers=headers)
print(f"Response : {response.text}")
# Print the response
#print(json.loads(response.text))
