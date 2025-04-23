import pokebase as pb

STATIC_FOLDER = "app/static/"

CACHE_DIR = STATIC_FOLDER + ".cache/"

pb.cache.set_cache(CACHE_DIR)

from module_logger import LoggerClass

log = LoggerClass().get_logger()

def get_pokemon_id_names_by_generation(generation: int, depth=0):
    if generation < 1 or generation > 3:
        log.error("Generation must be between 1 and 3")
        raise ValueError("Generation must be between 1 and 3")
    
    if depth > 1:
        raise Exception(f"Could not fetch pokemon name list by generation id {generation}")
    
    try:
        # use cache load function !!!
        if depth == 0:
            log.info("Try loading from cache")
            gen_resource = pb.cache.load("generation", generation)
            log.info("Successfully loaded from cache")
            pokemon_list = []
            for pokemon_source in gen_resource["pokemon_species"]:
                poke_id = pokemon_source["url"].split("/")[-2] # fetch id out of url
                pokemon_list.append((poke_id, pokemon_source["name"])) # append tupel with pokemon ip and name
            return pokemon_list
        # use api load function !!!
        elif depth == 1:
            log.info("Try fetching from api")
            gen_resource = pb.generation(generation)
            log.info("Successfully fetched from api")
            pokemon_list = []
            for pokemon_source in gen_resource.pokemon_species:
                pokemon_list.append((pokemon_source.id_, pokemon_source.name))
            return pokemon_list
    # key error occurs if load function cant find a fetch for the generation value hence try api call first
    except KeyError as e:
        if depth == 0:
            log.info("Could not find name list in cache. Will try api fetch next")
            return get_pokemon_names_by_generation(generation, depth + 1)
        else:
            log.error(f"KeyError on depth != 0! Error: {e}")
            return []
    except Exception as e:
        log.error(f"Unresolfed error occured! Error:{e}")
        return []


def get_pokemon_by_id(poke_id: int, depth=0):
    # try to fetch pokemon from database
    try:
        if depth == 0:
            log.info("Try loading from cache")
            gen_resource = pb.cache.load("pokemon", poke_id)
            log.info("Successfully loaded from cache")
            return gen_resource
        # use api load function !!!
        elif depth == 1:
            log.info("Try fetching from api")
            gen_resource = pb.pokemon(poke_id)
            log.info("Successfully fetched from api")
            return gen_resource
    except KeyError as e:
        if depth == 0:
            log.info("Could not find name list in cache. Will try api fetch next")
            return get_pokemon_by_id(poke_id, depth + 1)
        else:
            log.error(f"KeyError on depth != 0! Error: {e}")
            return []
    except Exception as e:
        log.error(f"Unresolfed error occured! Error:{e}")
        return []


def get_pokesprite_url_by_id(poke_id: int, depth: int):
    if depth > 1:
        raise Exception("Could not load Pokemon sprite")
    try:
        if depth == 0:
            return pb.cache.load_sprite("pokemon", poke_id)["path"].split("static")[1].replace("\\", "/")
        if depth == 1:
            return pb.SpriteResource('pokemon', poke_id).path.split("static")[1].replace("\\", "/")
    except FileNotFoundError as e:
        return get_pokesprite_url_by_id(poke_id, depth+1)


def get_pokemon_for_generation(generation: int):
    raise NotImplementedError("Get Pokemon by Generation has not been implemented yet")


if __name__ == "__main__":
    #print(get_pokemon_id_names_by_generation(1))
    print(get_pokemon_by_id(40))