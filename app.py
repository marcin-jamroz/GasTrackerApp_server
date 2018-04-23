from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()

pnconfig.subscribe_key = 'sub-c-1938ea76-4712-11e8-8bb7-3ab51ec5ed79'
pnconfig.publish_key = 'pub-c-030537aa-affc-4e27-ad09-b5a5f33b866b'

pubnub = PubNub(pnconfig)


def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            pubnub.publish().channel("awesomeChannel").message("hello!!").async(my_publish_callback)
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.

    def message(self, pubnub, message):
        # Handle new message stored in message.message
        print(dir(message))
        print(f'channel: {message.channel}, message: {message.message}, '
              f'publisher: {message.publisher}, subscription: {message.subscription},'
              f'timetoken: {message.timetoken}, user_metadata: {message.user_metadata}')



pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels('awesomeChannel').execute()


def publish_callback(result, status):
    pass
    # Handle PNPublishResult and PNStatus


pubnub.publish().channel('awesomeChannel').message(['hello', 'there']).async(publish_callback)