import pokebase as pb
import os

STATIC_FOLDER = "app/static/"

CACHE_DIR = STATIC_FOLDER + ".cache/"

SPRITE_POKEMON_CACHE = "sprite/pokemon/"

pb.cache.set_cache(CACHE_DIR)

def get_pokesprite_url_by_id(id: int):
    file_name = SPRITE_POKEMON_CACHE + str(id) + ".png"
    if os.path.exists(CACHE_DIR + file_name):
        return ".cache/" + SPRITE_POKEMON_CACHE + str(id) + ".png"
    return pb.SpriteResource('pokemon', id).url