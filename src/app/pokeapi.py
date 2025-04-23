import pokebase as pb
import os

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
    print(pb.APIResource("generation", "generation-i"))

def read_dat_file():
    print(pb.cache.load("generation", 7))

def get_sprite_by_id(id: int):
    #pb.SpriteResource('pokemon', 69)
    print()

def get_pokesprite_url_by_id(id: int, depth: int):
    if depth > 1:
        raise Exception("Could not load Pokemon sprite")
    try:
        return pb.cache.load_sprite("pokemon", id)["path"].split("static")[1].replace("\\", "/")
    except FileNotFoundError as e:
        pb.SpriteResource('pokemon', id)
        return get_pokesprite_url_by_id(id, depth+1)

if __name__ == "__main__":
    #get_generation()
    #read_dat_file()
    get_sprite_by_id()