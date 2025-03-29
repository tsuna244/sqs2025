import pokebase as pb
import os

CACHE_DIR="static/.cache"

SPRITE_POKEMON_CACHE = "/sprite/pokemon/"

pb.cache.set_cache(CACHE_DIR)

def get_pokesprite_url_by_id(id: int):
    cached_file_name = CACHE_DIR + SPRITE_POKEMON_CACHE + str(id) + ".png"
    if os.path.exists(cached_file_name):
        return cached_file_name
    return pb.SpriteResource('pokemon', id).url