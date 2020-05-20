import asyncio
import argparse
from slixmpp import ClientXMPP

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('echobot')


class Client(ClientXMPP):

    def __init__(self, jid, password):
        super().__init__(jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

        self.ready = asyncio.Future()

    async def session_start(self, event):
        self.send_presence()
        await self.get_roster()

        self.ready.set_result(True)

    def connect(self, *args, **kwargs) -> None:
        super().connect(*args, **kwargs)

        return self.ready

    async def message(self, msg):
        logger.info(f'Got message {msg}')
        body = msg['body']

        if body.startswith('[info]'):
            return

        if msg['type'] in ('chat', 'normal'):
            await asyncio.sleep(2)
            msg.reply(f'Echoing {body}').send()
            logger.info('Replied!')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('jid', type=str)
    parser.add_argument('password', type=str)

    args = parser.parse_args()

    async def main():
        client = Client(args.jid, args.password)
        await client.connect(('ip-jabber.olark.com', 5222))
        logger.info(f'Connected {client.boundjid.full}')

    loop = asyncio.get_event_loop()
    loop.create_task(main())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
