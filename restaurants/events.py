import json
import logging

import boto3
from decouple import config

logger = logging.getLogger(__name__)


def publish_review_event(review):
    topic_arn = config('SNS_TOPIC_ARN', default='')
    if not topic_arn:
        return
    try:
        sns = boto3.client('sns', region_name='ap-southeast-2')
        sns.publish(
            TopicArn=topic_arn,
            Subject='New DineWise review',
            Message=json.dumps({
                'review_id': review.id,
                'restaurant': review.restaurant.name,
                'user': review.user.username,
                'average_rating': review.average_rating(),
                'comment': review.comment[:200],
            }),
        )
    except Exception:
        logger.exception('Could not publish review event')