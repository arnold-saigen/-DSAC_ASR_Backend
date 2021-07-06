import json
import boto3
import uuid
from botocore.exceptions import ClientError
import os
import logging
logger = logging.getLogger()

def lambda_handler(event,context):
# print event summary

    event_summary = json.dumps(event, indent=2)
    print(event_summary)

    # email recipient list
    ses_recipient_list = ['arnold@saigen.co.za']

    # create unique tag for session
    uniq_tag = str(uuid.uuid4()).replace('-','')

    # set default values of some variables
    optional_header_dict = {'CUSTOM_GRAPH': 'none', 'PRIV': 'yes', 'TAG': uniq_tag,
                            'OBJECT_URL': 'none', 'NUM_SPK': 1, 'CAP_PROV': 'FARGATE_SPOT',
                             'FE_API_KEY': 'none', 'JOB_ID': 'none', 'NUM_THREADS' : 4, 'RETURN_URL' : 'https://saigen.ai/jobcomplete/'}

    # check that all required variables are present in the headers
    required_headers = ['X_API_KEY', 'DEC_LANG', 'SR', 'NUM_CHANNELS', 'SAC', 'DIA',
                        'BUCKET_NAME', 'OBJECT_PATH', 'USER_ID']
    optional_headers = ['CUSTOM_GRAPH', 'PRIV', 'TAG', 'OBJECT_URL', 'NUM_SPK', 'CAP_PROV', 'FE_API_KEY', 'JOB_ID', 'NUM_THREADS', 'RETURN_URL']
    header_vals = {}

    # check required headers
    for h in required_headers:
        try:
            if event['headers'][h]:
                header_vals[h] = event['headers'][h]
        except KeyError:
            return api_gateway_response({}, 
            'Bad request: %s not present in POST headers' % h, 400)
    # check optional headers
    for h in optional_headers:
        try:
            if event['headers'][h]:
                header_vals[h] = event['headers'][h]
        except KeyError:
            print('INFO: Optional header not found, using defualt value for %s.' % h)
            header_vals[h] = optional_header_dict[h]
            continue
        
    # authenticate with X_API_KEY
    lambda_x_api_key = os.environ['X_API_KEY']
    gateway_x_api_key = header_vals['X_API_KEY']
    if lambda_x_api_key != gateway_x_api_key:
        message = 'Authentication error: Incorrect X_API_KEY'
        return api_gateway_response({}, message, 401)
    else:
        pass

    # TODO - check valid values for each ENV variable

    # TODO - check if bucket and file exists

    # get object name from path
    header_vals['OBJECT_NAME'] = (header_vals['OBJECT_PATH']).rsplit('/')[-1]

    # format headers to json object
    container_env_vars = create_container_environ_json_from_headers(header_vals)
    print(container_env_vars)

    # return api_gateway_response({}, container_env_vars, 200)
    # exit(101)

    # run fargate task with container variables
    capacity_provider = header_vals['CAP_PROV']
    client = boto3.client('ecs')
    response = client.run_task(
        capacityProviderStrategy=[{
                'capacityProvider': capacity_provider,
            },
        ],
        cluster='saigen-asr',
        taskDefinition='saigen_asr_decode:5',
        count = 1,
        platformVersion='1.4.0',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    'subnet-0fe9c845',
                    'subnet-6cec0805',
                    'subnet-60aea918'
                ],
                'securityGroups': [
                    'sg-0082d205c470c6196'
                ],
                'assignPublicIp': 'ENABLED'
            }
        },
        overrides={
            'containerOverrides': [
                {
                    'name': 'saigen_asr_decode',
                    'environment': container_env_vars
                }
            ]
        }
    )

    # response to API gateway
    message = "Fargate task started sucesfully. See %s/decoded/" % header_vals['BUCKET_NAME']
    print(message)
    return api_gateway_response({}, message, 200)


def api_gateway_response(headers, body, status_code):
    response = {
        "isBase64Encoded": True,
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(body)
    }

    return response


def s3_response(status_code):
    response = {
        "statusCode": status_code
    }
    return response


def create_container_environ_json_from_headers(header_vals):
    env_json_object = []
    for key in header_vals.keys():
        val = header_vals[key]
        env_json_object.append({'name' : key, 'value' : str(val)})

    return (env_json_object)
