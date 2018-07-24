import config
import pydle
import logging
import os
import datetime
import codecs
import csv
import secrets

logger = logging.getLogger()

class MyOwnBot(pydle.Client):
    async def on_connect(self):
        logger.info("Succesfully connected.")

        self.awake_time = datetime.datetime.utcnow()

        self.beatmap_ids = []
        self.init_csv()

        #await self.join('#mp_44460306')

    def init_csv(self):
        with codecs.open('out.csv', 'r', 'utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.beatmap_ids.append(row['id'])

            logger.info(f"Added {len(self.beatmap_ids)} beatmaps to the list.")

    async def on_message(self, target, source, message):
        logger.info(f"{target} - {source}:{message}")
        self.check_logger()

        try:
            if message == '!f2' and source in config.REF_LIST:
                await self.select_random_map(target)

        except:
            logger.exception("Error while processing a command!")

    async def on_private_message(self,target, nick,message):
        logger.info(f"[PM]{nick}:{message}")

        try:
            if message.startswith('!join'):
                channel = message.split('!join ')[1]

                logger.info(f"Joining {channel}")
                await self.join(channel)

        except:
            logger.exception("Error while processing a command!")


    async def select_random_map(self, channel):
        if len(self.beatmap_ids) == 0:
            return
        random_beatmap_id = secrets.choice(self.beatmap_ids)

        logger.info(f"Chose beatmap {random_beatmap_id}")

        await self.message(channel, f'!mp map {random_beatmap_id}')


    def check_logger(self):
        today = datetime.datetime.now()
        if today.year != self.awake_time.year or today.month != self.awake_time.month or today.day != self.awake_time.day:
            logger.removeHandler(self.log_handler)
            self.awake_time = today
            self.log_handler = configure_logging()

def configure_logging():
    logging.basicConfig(level=logging.INFO)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(current_dir, "logs")
    handler = logging.FileHandler(filename='{}/{}.log'.format(logs_dir, datetime.datetime.now().strftime('%Y-%m-%d')),
                                  encoding='utf-8', mode='a')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

    logger = logging.getLogger()
    logger.addHandler(handler)
    return handler


if __name__ == '__main__':
    server = 'irc.ppy.sh'
    port = 6667
    user = config.IRC_USERNAME
    password = config.IRC_PASSWORD

    configure_logging()

    client = MyOwnBot(user, realname=user)
    client.run(server, port, tls=False, tls_verify=False, password = password)
