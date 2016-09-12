# In consumers.py
from channels import Group


def thing_consumer(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    print "hello", dir(message)
    print 'item', message.items()
    print 'content', message.content
    print 'channel', message.channel
    print 'reply_channel', message.reply_channel
    print 'keys', message.keys()
    print 'values', message.values()
    print 'channel_layer', message.channel_layer
    from time import sleep
    sleep(15)
    print "goodbye"
    
    # message.reply_channel.send({
    #     "text": message.content['text'],
    # })


from channels.generic import BaseConsumer

class ConceptConsumer(BaseConsumer):
    method_mapping = {
        'item.updates': "method_name",
        "channel.name.here2": "method_name",
    }

    def method_name(self, message, **kwargs):
        pass
