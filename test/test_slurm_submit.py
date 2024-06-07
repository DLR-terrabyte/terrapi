import json
import requests

#url = "https://slurmrest.terrabyte.lrz.de/openapi/v3"
url = "https://slurmrest.terrabyte.lrz.de/slurm/v0.0.37/job/submit"

# Obtained from terrapi
access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ5U0ZVZHZWM2FrZXdpbzVYb1dhMThxci16eVdzZWszMjNOQkxUNnZ2Q1dFIn0.eyJleHAiOjE3MTc3NzA5MjEsImlhdCI6MTcxNzc3MDYyMSwiYXV0aF90aW1lIjoxNzE3NzU2NjAxLCJqdGkiOiJiYjIzMjdhZi02ZjBkLTRkODAtYTY5Mi0yOTAxMmY0NjY3NmMiLCJpc3MiOiJodHRwczovL2F1dGgudGVycmFieXRlLmxyei5kZS9yZWFsbXMvdGVycmFieXRlIiwiYXVkIjpbImRlLmxyei50ZXJyYWJ5dGUuc2x1cm1yZXN0IiwiYWNjb3VudCJdLCJzdWIiOiIwODMyYzVlYy0xYWVlLTQ2MGMtYjM3My1jOTNiNWUwN2Q2NjEiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJhdC5lb3guaHViLnRlcnJhYnl0ZS1hcGkiLCJzZXNzaW9uX3N0YXRlIjoiMDZjODFlMGEtMjZjNC00YmY5LTg2OTItMTBjZjdhMDFiNDY4IiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL3RlcnJhYnl0ZS1hcGkuaHViLmVveC5hdC8iLCJodHRwczovL3RlcnJhYnl0ZS1hcGkuaHViLmVveC5hdCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy10ZXJyYWJ5dGUiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgb2ZmbGluZV9hY2Nlc3MgcHJvZmlsZSBlbWFpbCBzbHVybXJlc3QiLCJzaWQiOiIwNmM4MWUwYS0yNmM0LTRiZjktODY5Mi0xMGNmN2EwMWI0NjgiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJKdWxpYW4gWmVpZGxlciIsImdyb3VwcyI6WyIvZHNzL3BuNDljaS1kc3MtMDAwMCJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJkaTkzYm9yIiwiZ2l2ZW5fbmFtZSI6Ikp1bGlhbiIsImZhbWlseV9uYW1lIjoiWmVpZGxlciIsImVtYWlsIjoianVsaWFuLnplaWRsZXJAZGxyLmRlIn0.gQta5NRk8ssFyN3p0L4uQpRVEEiO2etSdxhMCnzVDH1EduB17-0buvqQy8joqQYtEqoQC9hl_riGy0i35rStFuc0R-FViBs6nPAhYddfL6kw-RIizCevybDJp6buzouca_R9baEcDkV8CuNNxBd2gE3POTXT_ycnVhbZ0XYTybfsna3SY9694JHIx57RTDUcPIcBDeVEtJbM0S1Awao_L_bUtDeSwD4-6Kcx_jTzQPljY7uhLSGrzFnWlwjgJM4gkdFumvfY9J9MzzKFxAHVxMXvmHv5BLiJzmEI1IfNe8UqlaVLtutf11rmHHMmD6gx5lZYx6PxfLZq12QQjlbs1w"

# Define the job payload, adjust project paths i.e `current_working_directory`, `standard_output` and `standard_error`
payload = {
    "job": {
        "name": "hello-tby-slurmrest",
        "partition": "hpda2_compute",
        "ntasks":1,
        "nodes": 1,
        "current_working_directory": "/dss/dsshome1/02/di75fed/tmp",
        "standard_input": "/dev/null",
        "standard_output": "/dss/dsshome1/02/di75fed/tmp/hello.out",
        "standard_error": "/dss/dsshome1/02/di75fed/tmp/hello.error",
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
