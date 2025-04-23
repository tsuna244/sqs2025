import pokebase as pb
import os

STATIC_FOLDER = "app/static/"

CACHE_DIR = STATIC_FOLDER + ".cache/"

pb.cache.set_cache(CACHE_DIR)

class PokemonObj():
    def __init__(self, poke_id: int, name: str, gen: str, sprite_path: str):
        self.poke_id = poke_id
        self.name = name
        self.gen = gen
        self.sprite_path = sprite_path


class GenerationObj():
    def __init__(self, gen_id: int, gen_name: str, pokemon: list):
        if len(pokemon) < 1 or type(pokemon[0]) is not PokemonObj:
            raise Exception("Generation Object needs a list of PokemonObjects")
        self.gen_id = gen_id
        self.gen_name = gen_name
        self.pokemon = pokemon


def get_pokemon_names_by_generation(generation: int):
    if generation < 1 or generation > 3:
        raise Exception("Generation must be between 1 and 3")
    # use cache load function !!!
    try:
        print("load from cache")
        gen_resource = pb.cache.load("generation", generation)
        for pokemon in gen_resource["pokemon_species"]:
            print(pokemon["name"])
    except KeyError:
        print("Key Error")
        gen_resource = pb.generation(generation)
        for pokemon in gen_resource.pokemon_species:
            print(pokemon)


def get_pokesprite_url_by_id(id: int, depth: int):
    if depth > 1:
        raise Exception("Could not load Pokemon sprite")
    try:
        if depth == 0:
            return pb.cache.load_sprite("pokemon", id)["path"].split("static")[1].replace("\\", "/")
        if depth == 1:
            return pb.SpriteResource('pokemon', id).path.split("static")[1].replace("\\", "/")
    except FileNotFoundError as e:
        return get_pokesprite_url_by_id(id, depth+1)


if __name__ == "__main__":
    get_generation(2)