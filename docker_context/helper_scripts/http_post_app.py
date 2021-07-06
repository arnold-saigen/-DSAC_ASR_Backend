import requests
import json
import argparse
import os

def arg_parse():
    parser = argparse.ArgumentParser(
            description='Publish HTTP post to inform front-end where decoding is located.')
    parser.add_argument('-front_end_url', action='store', required=True,
            help='URL to make post to.')
    parser.add_argument('-s3_decoded_path', action='store', required=True,
            help='Path to where decoded file is located on S3.')
    parser.add_argument('-decoded_file_path', action='store', required=True,
            help='Path to where decoded file is located on locally.')
    parser.add_argument('-user_id', action='store', required=True,
            help='User ID.')
    parser.add_argument('-job_id', action='store', required=True,
            help='Job ID.')
    parser.add_argument('-x_api_key', action='store', required=True,
            help='Frontend API key.')
    
    return parser.parse_args()


def main():
    args = arg_parse()
    url = args.front_end_url
    loc_path = args.decoded_file_path
    s3_path = args.s3_decoded_path
    user_id = args.user_id
    job_id = args.job_id
    x_api_key = args.x_api_key
    fin = open(loc_path, 'rb')
    files = {'file': fin}
    retry_attempts = 3
    
    try:
        for k in range(0, retry_attempts):
            headers={'X-API-KEY': x_api_key,
                                        'USER-ID' : user_id, 
                                        'JOB-ID' : job_id,
                                        'S3-PATH' : s3_path,
                                        'STATUS' : 'SUCCESS'}
            print(headers)
            req = requests.post(url, files=files, headers=headers)
            print(req.status_code)
            if req.status_code == 200:
                print('Done sending data to %s' % url)
                break

            print('ERROR: Response retry timeout.\n'
                  'Tried to send to front-end %i times.' % retry_attempts)
    except:
        print('ERROR: Something went wrong when returning decoding to frontend.')
        print('Status: %s' % str(req.status_code))
        print('Text: %s' % req.text)
    finally:
        fin.close()


if __name__ == "__main__":
    main()
    print("Info: Done.")

