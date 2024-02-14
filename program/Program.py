import MQTTclient

from queue import Queue
from threading import Thread

class Program:

    def __init__(self, config, topic_dispatcher):

        self.queue = Queue()

        self.config = config
        self.topic_dispatcher = topic_dispatcher

        self.subscriber = None
        self.publisher = None
        self.subscriber = MQTTclient.Subscriber(config=self.config, queue=self.queue)
        self.publisher = MQTTclient.Publisher(config=self.config)

        processor_process = Thread(target=self.message_processor)
        processor_process.start()

    def message_processor(self):
        while True:
            # Blocking call, no CPU waste here
            message = self.queue.get()  
            if message:
                callback = self.topic_dispatcher.get(message.topic, self.handle_unknown_topic)
                # print(message.payload)
                # print(message.topic)
                callback_process = Thread(target=callback, args=(message.topic, message.payload.decode('utf8'), self.publisher, ))
                callback_process.start()
                # callback(message.topic, message.payload.decode('utf8'), self.publisher)

    def handle_unknown_topic(self, topic, data, publisher):
        # 알 수 없는 토픽 처리 로직
        print(f"Received message from unknown topic {topic}: {data}")

    
    def start(self):
        pass

        
    