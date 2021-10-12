from vosk import Model
from gluon.cache import lazy_cache


@lazy_cache('get_model', time_expire=3600, cache_model='ram')
def get_model(model_path):
    model = Model(model_path)
    return model
