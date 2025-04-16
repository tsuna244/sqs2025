import pokebase as pb
import os
import pandas as pd
import chardet

STATIC_FOLDER = "app/static/"

CACHE_DIR = STATIC_FOLDER + ".cache/"

SPRITE_POKEMON_CACHE = "sprite/pokemon/"

pb.cache.set_cache(CACHE_DIR)

class PokemonObj():
    poke_id: int
    name: str
    gen: str

    sprite_path: str

def get_generation():
    return pb.APIResource("generation", "generation-i")

def read_dat_file():
    pb.cache.load("generation", 1)

def get_sprite_by_id():
    return pb.cache.load_sprite("pokemon", 69)

def get_pokesprite_url_by_id(id: int):
    file_name = SPRITE_POKEMON_CACHE + str(id) + ".png"
    if not os.path.exists(CACHE_DIR + file_name):
        pb.SpriteResource('pokemon', id)
    return ".cache/" + file_name

if __name__ == "__main__":
    print(get_sprite_by_id())