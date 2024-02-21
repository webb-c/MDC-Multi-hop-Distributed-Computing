import MQTTclient

from queue import Queue
from threading import Thread
from pyprnt import prnt

class Program:

    def __init__(self, sub_config, pub_configs, topic_dispatcher):

        self.queue = Queue()

        self.sub_config = sub_config
        self.pub_configs = pub_configs
        self.topic_dispatcher = topic_dispatcher

        self.subscriber = None
        self.publisher = []
        self.processor_thread = None

        self.init_subscriber()
        self.init_publisher()
        self.init_processor()

        prnt({"sub_config" : sub_config, "pub_configs" : pub_configs})
    
    def init_subscriber(self):
        if self.sub_config != None:
            self.subscriber = MQTTclient.Subscriber(config=self.sub_config, queue=self.queue)

    def init_publisher(self):
        for config in self.pub_configs:
            self.publisher.append(MQTTclient.Publisher(config=config))

    def init_processor(self):
        if self.sub_config != None:
            self.processor_thread = Thread(target=self.message_processor)
            self.processor_thread.start()

    def message_processor(self):
        while True:
            # Blocking call, no CPU waste here
            message = self.queue.get()  
            if message:
                callback = self.topic_dispatcher.get(message.topic, self.handle_unknown_topic)
                # callback_thread = Thread(target=callback, args=(message.topic, message.payload, self.publisher, ))
                # callback_thread.start()
                callback(message.topic, message.payload, self.publisher)

    def handle_unknown_topic(self, topic, data, publisher):
        # 알 수 없는 토픽 처리 로직
        print(f"Received message from unknown topic {topic}: {data}")

    
    def start(self):
        pass

        
    