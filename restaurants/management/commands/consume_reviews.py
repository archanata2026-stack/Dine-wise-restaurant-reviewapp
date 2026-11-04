import json
import time

import boto3
from decouple import config
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Poll SQS for review events and process them'

    def handle(self, *args, **opts):
        queue_url = config('SQS_QUEUE_URL', default='')
        if not queue_url:
            self.stdout.write('SQS_QUEUE_URL not set, exiting')
            return
        sqs = boto3.client('sqs', region_name='ap-southeast-2')
        self.stdout.write('[review-worker] started')
        while True:
            try:
                resp = sqs.receive_message(
                    QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=20)
                for msg in resp.get('Messages', []):
                    event = json.loads(msg['Body'])
                    self.stdout.write(
                        f"[review-worker] {event['user']} reviewed "
                        f"{event['restaurant']} (avg {event['average_rating']})")
                    sqs.delete_message(
                        QueueUrl=queue_url, ReceiptHandle=msg['ReceiptHandle'])
            except Exception as exc:
                self.stdout.write(f'[review-worker] error: {exc}')
                time.sleep(5)