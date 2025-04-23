import pokebase as pb

STATIC_FOLDER = "app/static/"

CACHE_DIR = STATIC_FOLDER + ".cache/"

pb.cache.set_cache(CACHE_DIR)

from .module_logger import LoggerClass

log = LoggerClass.get_logger()

def get_pokemon_names_by_generation(generation: int, depth=0):
    if generation < 1 or generation > 3:
        log.error("Generation must be between 1 and 3")
        raise ValueError("Generation must be between 1 and 3")
    
    if depth > 1:
        raise Exception(f"Could not fetch pokemon name list by generation id {id}")
    
    try:
        # use cache load function !!!
        if depth == 0:
            log.info("Try loading from cache")
            gen_resource = pb.cache.load("generation", generation)
            pokemon_names = []
            for pokemon in gen_resource["pokemon_species"]:
                pokemon_names.append(pokemon["name"])
            return pokemon_names
        # use api load function !!!
        elif depth == 1:
            log.info("Try fetching from api")
            gen_resource = pb.generation(generation)
            return gen_resource.pokemon_species
    # key error occurs if load function cant find a fetch for the generation value hence try api call first
    except KeyError as e:
        if depth == 0:
            log.info("Could not find name list in cache. Will try api fetch next")
            get_pokemon_names_by_generation(generation, depth + 1)
        else:
            log.error(f"KeyError on depth != 0! Error: {e}")
            return []
    except Exception as e:
        log.error(f"Unresolfed error occured! Error:{e}")
        return []


def get_pokemon_by_name(pokemon_name: str):
    # try to fetch pokemon from database
    try:
        print("load from cache")
        
        pb.pokemon(pokemon_name)
    except:
        pass
    return None


def get_pokemon_by_id(poke_id: int):
    raise NotImplementedError("Get Pokemon By Id function has not been implemented yet")


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


def get_pokemon_for_generation(generation: int):
    raise NotImplementedError("Get Pokemon by Generation has not been implemented yet")


if __name__ == "__main__":
    get_pokemon_names_by_generation(2)