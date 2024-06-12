import asyncio
from binance import AsyncClient, DepthCacheManager
import datetime
from db_handler import insert_into_table, get_values
import json
import telegram
import logging


with open('settings.json') as settings_file:
    SETTINGS = json.load(settings_file)

    API_KEY = SETTINGS['binance_api_key']
    SECRET_KEY = SETTINGS['binance_secret_key']
    CONNECTION = SETTINGS['database_connection']
    DB_NAME = SETTINGS['database_name']
    PERIOD_OF_TIME = SETTINGS['period_of_time']
    VOLUMES_DIFF_LIMIT = SETTINGS['vol_diff_limit']

    TOKEN = SETTINGS['tg_bot_token']
    CHAT_ID = SETTINGS['tg_chat_id']

logging.basicConfig(filename='performance.log', level=logging.INFO)


def calculate_weight(record_at):
    max_weight = 1
    min_weight = 0.2
    record_age_seconds = (datetime.datetime.now() - record_at).total_seconds()
    weight = max_weight - ((max_weight - min_weight) * record_age_seconds) / (PERIOD_OF_TIME * 60)
    return max(min_weight, weight)


bot = telegram.Bot(token=TOKEN)


async def send_message(text, chat_id):
    async with bot:
        await bot.send_message(text=text, chat_id=chat_id)


async def monitoring(client, symbol):
    dcm = DepthCacheManager(client, symbol, refresh_interval=180)

    async with dcm as dcm_socket:
        while True:
            start_time = datetime.datetime.now()
            depth_cache = await dcm_socket.recv()
            end_time = datetime.datetime.now()
            logging.info(f"Binance data {symbol} retrieval time: {end_time - start_time} seconds")
            time = datetime.datetime.now().strftime("%H:%M:%S")

            bids = depth_cache.get_bids()[:100]
            asks = depth_cache.get_asks()[:100]

            best_bids_price, best_bids_vol = depth_cache.get_bids()[0]
            best_ask_price, best_ask_vol = depth_cache.get_asks()[0]

            avg_price = (best_bids_price + best_ask_price) / 2

            avg_price_plus_2 = avg_price * 1.02
            avg_price_minus_2 = avg_price * 0.98

            volumes_plus_2 = 0
            volumes_minus_2 = 0

            for item in bids:
                if avg_price_plus_2 >= item[0]:
                    volumes_plus_2 += item[1]

            for item in asks:
                if avg_price_minus_2 <= item[0]:
                    volumes_minus_2 += item[1]

            values = (symbol, avg_price, volumes_plus_2, volumes_minus_2)
            start_time = datetime.datetime.now()
            insert_into_table(conn=CONNECTION, database_name=DB_NAME, table_name=symbol, val=values)
            end_time = datetime.datetime.now()
            logging.info(f"Data storage time: {end_time - start_time} seconds")

            start_time = datetime.datetime.now()
            volumes = get_values(conn=CONNECTION, database_name=DB_NAME, table_name=symbol, intrvl=PERIOD_OF_TIME)
            sum_bids_vol = 0
            sum_asks_vol = 0
            weight_count = 0
            for volume in volumes:
                bids_vol, asks_vol, record_time = volume
                weight = calculate_weight(record_time)
                sum_bids_vol += float(bids_vol) * weight
                sum_asks_vol += float(asks_vol) * weight
                weight_count += weight

            avg_weighted_vol_bids = sum_bids_vol / weight_count
            avg_weighted_vol_asks = sum_asks_vol / weight_count

            with open("notification_template.txt", "r", encoding="utf-8") as f:
                notification_template = f.read()
        
            vol_deviation_bids = (abs(avg_weighted_vol_bids - volumes_plus_2)/avg_weighted_vol_bids) * 100
            vol_deviation_asks = (abs(avg_weighted_vol_asks - volumes_minus_2) / avg_weighted_vol_asks) * 100
            if vol_deviation_bids >= VOLUMES_DIFF_LIMIT or vol_deviation_asks >= VOLUMES_DIFF_LIMIT:
                print(vol_deviation_asks, vol_deviation_bids, VOLUMES_DIFF_LIMIT)
                notification_message = notification_template.format(
                    pair=symbol,
                    timestamp=time,
                    current_volume_plus=volumes_plus_2,
                    avg_volume_plus=avg_weighted_vol_bids,
                    deviation_plus=vol_deviation_bids,
                    current_volume_minus=volumes_minus_2,
                    avg_volume_minus=avg_weighted_vol_asks,
                    deviation_minus=vol_deviation_asks,
                    period=PERIOD_OF_TIME
                )
                loop.call_soon(asyncio.create_task, send_message(text=notification_message, chat_id=CHAT_ID))
            end_time = datetime.datetime.now()
            logging.info(f"Checking for deviations in volume data from the weighted average: {end_time - start_time} seconds")

async def main():
    client = await AsyncClient.create(api_key=API_KEY, api_secret=SECRET_KEY)
    await asyncio.gather(
        monitoring(client, symbol='BTCUSDT'),
        monitoring(client, symbol='ETHUSDT'),
        monitoring(client, symbol='SOLUSDT'))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())



