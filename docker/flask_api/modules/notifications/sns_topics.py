import re
import os
import time
import boto3
from os import path
import logging.config
from logtail import LogtailHandler
from botocore.exceptions import ClientError

### LOGGING SETUP ###
handler = LogtailHandler(source_token=os.environ['LOG_SOURCE_TOKEN'])
#log_file_path = path.join(path.dirname(path.abspath(__file__)), '/app/logging/logging.ini')
#logging.config.fileConfig(log_file_path)
#logger = logging.getLogger(__name__)
#logger_list = ['boto', 'boto3', 'chardet', 'urllib3', 'botocore', 's3transfer', 'PIL']
#for i in logger_list:
#    logging.getLogger(i).setLevel(logging.CRITICAL) #sets all #logging sources to crit level

logger = logging.getLogger(__name__)
logger.handlers = []
logger.setLevel(logging.DEBUG) # Set minimal log level
logger.addHandler(handler) # asign handler to logger

class SNSTopic:
    def __init__(self):
        self.sns_client = boto3.client('sns', verify=False)

    def create_topic(self, t_name):
        """
        Creates a notification topic.

        :param name: The name of the topic to create.
        :return: The newly created topic.
        """
        self.topic_name = t_name
        try:
            topic = self.sns_client.create_topic(Name=self.topic_name)
            logger.info("Created topic %s with ARN %s.", self.topic_name, topic['TopicArn'])
            logger.debug(f"Topic Create Response: {topic}")
        except ClientError:
            logger.exception("Couldn't create topic %s.", self.topic_name)
            pass
        else:
            return topic['TopicArn']

    def list_topics(self):
        """
        Lists topics for the current account.

        :return: An iterator that yields the topics.
        """
        try:
            topics_iter = self.sns_client.list_topics()
            logger.info("Boom..Got topics.")
        except ClientError:
            logger.exception("Wha wha, Couldn't get topics.")
            pass
        else:
            return topics_iter

    def delete_topic(self,t_arn):
        """
        Delete topic from the account.

        :return: Delete response.
        """
        try:
            response = self.sns_client.delete_topic(TopicArn=t_arn)
            logger.info(f"Delete topic success: {t_arn}")
        except ClientError:
            logger.exception(f"Delete topic failed: {t_arn}")
            pass
        else:
            return response


    def topic_subscribe(self, topic_arn=None, protocol=None, endpoint=None):
        """
        Subcribe to topic passed to function.

        :return: subscribe response.
        """
        logger.debug(f"TS: {topic_arn}")
        try:
            response = self.sns_client.subscribe(TopicArn=topic_arn, Protocol=protocol, Endpoint=endpoint)
            subscription_arn = response["SubscriptionArn"]
            logger.info(f"Subscribe topic success: {topic_arn}")
        except Exception as e:
            logger.error(f"Subscribe topic failed: {topic_arn}: {e}")
            pass
        else:
            return subscription_arn


    def list_all_topic_subs(self):
        """
        List all topics subscriptions.

        :return: iterable list response.
        """
        try:
            response = self.sns_client.list_subscriptions()
            subscriptions = response["Subscriptions"]
            logger.info(f"List all topic subs success")
        except ClientError:
            logger.exception(f"List all topic subs failed")
            pass
        else:
            return response

    def list_subs_by_topic(self, t_arn):
        """
        List subscriptions from the topic arn.

        :return: subscription response.
        """
        try:
            response = self.sns_client.list_subscriptions_by_topic(TopicArn=t_arn)
            subscriptions = response["Subscriptions"]
            logger.info(f"List subs by topic success: {t_arn}")
        except ClientError:
            logger.exception(f"List subs by topic failed{t_arn}")
            pass
        else:
            return response

    def unsub_to_topic(self, s_arn):
        """
        unsubscribe to subscription arn provided to function.

        :return: unsub response.
        """
        self.sns_client.unsubscribe(SubscriptionArn=s_arn)

    def unsub_to_all_proto_subs (self, proto, subs):
        """
        unsubscribe to ALL protocol subscriptions.
        email / SMS
        :return: Delete response.
        """
        for sub in subs:
        	if sub["Protocol"] == proto:
        		self.sns_client.unsubscribe(sub["SubscriptionArn"])

    def publish_topic(self, t_arn=None, message=None, subject=None):
        """
        Publish topic message to subject or device

        :return: publish response.
        """
        try:
            response = self.sns_client.publish(TopicArn=t_arn, Message=message,\
             Subject=subject)
            logger.info(f"Topic publish success: {message}")
        except ClientError:
            logger.exception(f"Topic publish failed: {message}")
            pass
        else:
            return response

    def send_sms(self, phone=None, message=None):
        """
        Publish topic message to subject or device

        :return: publish response.
        """
        try:
            response = self.sns_client.publish(PhoneNumber=phone, Message=message)
            logger.info(f"publish SMS success: {message}")
        except ClientError:
            logger.exception(f"publish SMS failed: {message}")
            pass
        else:
            return response

def main():
    topic_name = f'demo-101-topic-{time.time_ns()}'

    st1 = SNSTopic()

    list_topics_resp = st1.list_topics()
    if list_topics_resp['ResponseMetadata']['HTTPStatusCode'] == 200:
        for arn in list_topics_resp['Topics']:
            if re.search('bkw-seventh-street-capital-494-llc-2022bk14665', arn['TopicArn']):
                subs_by_topic_resp = st1.list_subs_by_topic(arn['TopicArn'])
                if subs_by_topic_resp is not None:
                    if subs_by_topic_resp['Subscriptions']:
                        print(arn['TopicArn'])
                    else:
                        print(arn['TopicArn'])
                else:
                    pass

# MAIN
if __name__ == '__main__':
    main()
