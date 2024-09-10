import requests

hr = {
    'authorization': 'undefined',
    'content-type': 'application/json'
}

sample_data = {"SOURCE_TYPE_ID":54,"SOURCE_ID":337397}

response = requests.post('https://firststop.sos.nd.gov/api/WebUserAccess/GET_USER_IS_OWNER', headers=hr, data=sample_data)
print(response.json())