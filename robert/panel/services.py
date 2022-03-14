from .. import nice_redis
from ..constants.redis_constants import DATA_CACHER_REDIS_CONSTANTS


data_cacher_redis = nice_redis.DataCacher(**DATA_CACHER_REDIS_CONSTANTS.to_dict())


def read_generated_data():
    buy_from_wallex = data_cacher_redis.read__data('buy_from_wallex').get('rates')
    buy_from_nobitex = data_cacher_redis.read__data('buy_from_nobitex').get('rates')

    data = {
        'buy_from_wallex': buy_from_wallex,
        'buy_from_nobitex': buy_from_nobitex
    }

    return data
