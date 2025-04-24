import pokebase as pb
from enum import Enum

STATIC_FOLDER = "app/static/"

CACHE_DIR = STATIC_FOLDER + ".cache/"

pb.cache.set_cache(CACHE_DIR)

from module_logger import LoggerClass

log = LoggerClass().get_logger()


class PokemonRarity(Enum):
    NORMAL = "normal"
    LEGENDARY = "legendary"
    MYTHIC = "mythical"


# TODO: check if pokemon_source has is_mithical and is_legendary as parameter!!! and if they are boolean values
def get_rarity_from_pokemon_species_api_source(pokemon_source):
    rarity = PokemonRarity.NORMAL
    if pokemon_source.is_mythical:
        rarity = PokemonRarity.MYTHIC
    if pokemon_source.is_legendary:
        rarity = PokemonRarity.LEGENDARY
    return rarity


def get_pokemon_id_names_by_generation(generation: int, depth=0):
    if generation < 1 or generation > 3:
        log.error("Generation must be between 1 and 3")
        raise ValueError("Generation must be between 1 and 3")
    
    if depth > 1:
        log.error("Could not fetch pokemon name list by generation id {generation}")
        return []

    try:
        # use cache load function !!!
        if depth == 0:
            log.info("Try loading from cache")
            gen_resource = pb.cache.load("generation", generation)
            log.info("Successfully loaded from cache")
            pokemon_list = []
            for pokemon_source in gen_resource["pokemon_species"]:
                print(pokemon_source)
                poke_id = pokemon_source["url"].split("/")[-2] # fetch id out of url
                pokemon_list.append((poke_id, pokemon_source["name"])) # append tupel with pokemon ip and name (add pokemon rarity)
            return pokemon_list
        # use api load function !!!
        elif depth == 1:
            log.info("Try fetching from api")
            gen_resource = pb.generation(generation)
            log.info("Successfully fetched from api")
            pokemon_list = []
            for pokemon_source in gen_resource.pokemon_species:
                rarity = get_rarity_from_pokemon_species_api_source(pokemon_source)
                pokemon_list.append((pokemon_source.id_, pokemon_source.name, rarity)) # add pokemon rarity
            return pokemon_list
    # key error occurs if load function cant find a fetch for the generation value hence try api call first
    except KeyError as e:
        if depth == 0:
            log.info("Could not find name list in cache. Will try api fetch next")
            return get_pokemon_id_names_by_generation(generation, depth + 1)
        else:
            log.error(f"KeyError on depth != 0! Error: {e.__str__()}")
            return []
    except Exception as e:
        log.error(f"Unresolfed error occured! Error:{e.__str__()}")
        return []


def get_pokemon_rarity_by_id(poke_id: int, depth = 0):
    try:
        if depth == 0:
            log.info("Loading pokemon species from cache")
            pokemon_species = pb.cache.load("pokemon-species", poke_id)
            log.info("Loaded pokemon species from cache successful")
            rarity = PokemonRarity.NORMAL
            if pokemon_species["is_mythical"]:
                rarity = PokemonRarity.MYTHIC
            if pokemon_species["is_legendary"]:
                rarity = PokemonRarity.LEGENDARY
            return rarity
        elif depth == 1:
            log.info("Fetching pokemon species from api")
            pokemon_species = pb.pokemon_species(poke_id)
            log.info("Fetched pokemon species from api successful")
            return get_rarity_from_pokemon_species_api_source(pokemon_species)
    except KeyError as e:
        if depth == 0:
            log.info("Could not find pokemon species in cache. Will try api fetch next")
            return get_pokemon_rarity_by_id(poke_id, depth + 1)
        else:
            log.error(f"KeyError on depth != 0! Error: {e.__str__()}")
            return None
    except Exception as e:
        log.error(f"Unresolfed error occured! Error: {e.__str__()}")
        return None


def get_pokemon_by_id(poke_id: int, depth=0):
    # try to fetch pokemon from database
    try:
        if depth == 0:
            log.info("Try loading from cache")
            poke_resource = pb.cache.load("pokemon", poke_id)
            log.info("Successfully loaded from cache")
            # id - name - stats: {(name, value)}
            
            poke_stats = []
            
            for stat in poke_resource["stats"]:
                poke_stats.append((stat["stat"]["name"], stat["base_stat"]))
                
            return poke_resource["id"], poke_resource["name"], poke_stats
        # use api load function !!!
        elif depth == 1:
            log.info("Try fetching from api")
            poke_resource = pb.pokemon(poke_id)
            log.info("Successfully fetched from api")
            
            poke_stats = []
            
            for stat in poke_resource.stats:
                poke_stats.append((stat.stat.__getattr__("name"), stat.base_stat))
            
            return poke_resource.id, poke_resource.name, poke_stats
    except KeyError as e:
        if depth == 0:
            log.info("Could not find name list in cache. Will try api fetch next")
            return get_pokemon_by_id(poke_id, depth + 1)
        else:
            log.error(f"KeyError on depth != 0! Error: {e}")
            return None
    except Exception as e:
        log.error(f"Unresolfed error occured! Error:{e}")
        return None


def get_pokesprite_url_by_id(poke_id: int, depth: int):
    if depth > 1:
        log.error(f"Could not load sprite for pokemon with id {poke_id}")
        return ""
    
    try:
        sprite_path = ""
        if depth == 0:
            log.info("Loading pokemon sprite from cache")
            sprite_path = pb.cache.load_sprite("pokemon", poke_id)["path"].split("static")[1].replace("\\", "/")
            log.info("Loaded pokemon sprite from cache successfuly")
            return sprite_path
        if depth == 1:
            log.info("Fetching pokemon sprite from api")
            sprite_path = pb.SpriteResource('pokemon', poke_id).path.split("static")[1].replace("\\", "/")
            log.info("Fetched pokemon sprite from api successfuly")
        return sprite_path
    except FileNotFoundError as e:
        if depth == 0:
            log.info("Loading pokemon sprite from cache failed. Sprite not found.")
            return get_pokesprite_url_by_id(poke_id, depth+1)
        else:
            log.error(f"KeyError on depth != 0! Error: {e}")
            return ""
    except Exception as e:
        log.error(f"Failed fetching sprite for pokemon with id {poke_id}. Error: {e}")
        return ""


def get_pokemon_for_generation(generation: int):
    log.info(f"Loading id-name list for generation {generation}")
    gen = get_pokemon_id_names_by_generation(generation)
    if len(gen) > 0:
        log.info(f"Loading id-name list for pokemon in generation {generation} successful")
        
        pokemon_list = []
        
        for pokemon in gen:
            if isinstance(pokemon[0], str):
                pokemon_info = get_pokemon_by_id(int(pokemon[0]))
            elif isinstance(pokemon[0], int):
                pokemon_info = get_pokemon_by_id(pokemon[0])
            else:
                log.error(f"Pokemon idd is not of type str or int. Cannot fetch pokemon by id for id: {pokemon[0]}")
            if pokemon_info is not None:
                pokemon_list.append(pokemon_info)
        return pokemon_list
    else:
        log.info(f"Could not load id-name list for generation {generation}")
        return []


if __name__ == "__main__":
    
    print(get_pokemon_for_generation(1))