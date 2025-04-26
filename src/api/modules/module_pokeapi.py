import pokebase as pb
from enum import Enum

STATIC_FOLDER = "app/static/"

CACHE_DIR = STATIC_FOLDER + ".cache/"

pb.cache.set_cache(CACHE_DIR)

from .module_logger import LoggerClass

log = LoggerClass().get_logger()


class PokemonRarity(Enum):
    NORMAL = "normal"
    LEGENDARY = "legendary"
    MYTHIC = "mythical"


def log_function(function_name: str, log_msg: str, log_type = "info"):
    msg = "(module_pokeapi | {:30s}) -> {}".format(function_name + "(...)", log_msg)
    if log_type == "error":
        log.error(msg)
    if log_type == "warn":
        log.warning(msg)
    else:
        log.info(msg)

# Todo set return type to list
def get_pokemon_id_names_by_generation(generation: int, depth=0):
    if generation < 1 or generation > 3:
        log_function("get_pokemon_id_names_by_generation", "Generation must be between 1 and 3", "error")
        raise ValueError("Generation must be between 1 and 3")
    
    if depth > 1:
        log_function("get_pokemon_id_names_by_generation", f"Could not fetch pokemon name list by generation id {generation}", "error")
        return []

    try:
        # use cache load function !!!
        if depth == 0:
            log_function("get_pokemon_id_names_by_generation", "Try loading from cache")
            gen_resource = pb.cache.load("generation", generation)
            log_function("get_pokemon_id_names_by_generation", "Successfully loaded from cache")
            pokemon_list = []
            for pokemon_source in gen_resource["pokemon_species"]:
                poke_id = int(pokemon_source["url"].split("/")[-2]) # fetch id out of url
                pokemon_list.append({"pokemon_id": poke_id, "pokemon_name": pokemon_source["name"]})
            return pokemon_list
        # use api load function !!!
        elif depth == 1:
            log_function("get_pokemon_id_names_by_generation", "Try fetching from api")
            gen_resource = pb.generation(generation)
            log_function("get_pokemon_id_names_by_generation", "Successfully fetched from api")
            pokemon_list = []
            for pokemon_source in gen_resource.pokemon_species:
                pokemon_list.append({"pokemon_id": pokemon_source.id_, "pokemon_name": pokemon_source.name}) # add pokemon rarity
            return pokemon_list
    # key error occurs if load function cant find a fetch for the generation value hence try api call first
    except KeyError as e:
        if depth == 0:
            log_function("get_pokemon_id_names_by_generation", "Could not find name list in cache. Will try api fetch next")
            return get_pokemon_id_names_by_generation(generation, depth + 1)
        else:
            log_function("get_pokemon_id_names_by_generation", f"KeyError on depth != 0! Error: {e.__str__()}", "error")
            return []
    except Exception as e:
        log_function("get_pokemon_id_names_by_generation", f"Unresolfed error occured! Error:{e.__str__()}", "error")
        return []


# TODO: set return type to dict check id < 0 ?
def get_pokemon_rarity_and_generation_by_id(poke_id: int, depth = 0):
    try:
        if depth == 0:
            log_function("get_pokemon_rarity_and_generation_by_id", "Loading pokemon species from cache")
            pokemon_species = pb.cache.load("pokemon-species", poke_id)
            log_function("get_pokemon_rarity_and_generation_by_id", "Loaded pokemon species from cache successful")
            rarity = PokemonRarity.NORMAL
            if pokemon_species["is_mythical"]:
                rarity = PokemonRarity.MYTHIC
            if pokemon_species["is_legendary"]:
                rarity = PokemonRarity.LEGENDARY
            pokemon_gen_id = pokemon_species["generation"]["url"].split("/")[-2]
            return {"pokemon_rarity": rarity, "pokemon_gen_id": pokemon_gen_id, "pokemon_gen_name": pokemon_species["generation"]["name"]}
        elif depth == 1:
            log_function("get_pokemon_rarity_and_generation_by_id", "Fetching pokemon species from api")
            pokemon_species = pb.pokemon_species(poke_id)
            log_function("get_pokemon_rarity_and_generation_by_id", "Fetched pokemon species from api successful")
            rarity = PokemonRarity.NORMAL
            if pokemon_species.is_mythical:
                rarity = PokemonRarity.MYTHIC
            if pokemon_species.is_legendary:
                rarity = PokemonRarity.LEGENDARY
            pokemon_gen_id = pokemon_species.generation.url.split("/")[-2]
            return {"pokemon_rarity": rarity, "pokemon_gen_id": pokemon_gen_id, "pokemon_gen_name": pokemon_species.generation.name}
    except KeyError as e:
        if depth == 0:
            log_function("get_pokemon_rarity_and_generation_by_id", "Could not find pokemon species in cache. Will try api fetch next")
            return get_pokemon_rarity_and_generation_by_id(poke_id, depth + 1)
        else:
            log_function("get_pokemon_rarity_and_generation_by_id", f"KeyError on depth != 0! Error: {e.__str__()}", "error")
            return None
    except Exception as e:
        log.error()
        log_function("get_pokemon_rarity_and_generation_by_id", f"Unresolfed error occured! Error: {e.__str__()}", "error")
        return None


# TODO: set return type to dict check id < 0?
def get_pokemon_by_id(poke_id: int, depth = 0):
    # try to fetch pokemon from database
    try:
        if depth == 0:
            log_function("get_pokemon_by_id", "Try loading from cache")
            poke_resource = pb.cache.load("pokemon", poke_id)
            log_function("get_pokemon_by_id", "Successfully loaded from cache")
            
            poke_stats = []
            
            for stat in poke_resource["stats"]:
                poke_stats.append({"stat_name": stat["stat"]["name"], "stat_value": stat["base_stat"]})
            
            return {"pokemon_id": poke_resource["id"], "pokemon_name": poke_resource["name"], "pokemon_stats": poke_stats}
        # use api load function !!!
        elif depth == 1:
            log_function("get_pokemon_by_id", "Try fetching from api")
            poke_resource = pb.pokemon(poke_id)
            log_function("get_pokemon_by_id", "Successfully fetched from api")
            
            poke_stats = []
            
            for stat in poke_resource.stats:
                poke_stats.append({"stat_name": stat.stat.__getattr__("name"), "stat_value": stat.base_stat})
            
            return {"pokemon_id": poke_resource.id, "pokemon_name": poke_resource.name, "pokemon_stats": poke_stats}
    except KeyError as e:
        if depth == 0:
            log_function("get_pokemon_by_id", "Could not find name list in cache. Will try api fetch next")
            return get_pokemon_by_id(poke_id, depth + 1)
        else:
            log_function("get_pokemon_by_id", f"KeyError on depth != 0! Error: {e}", "error")
            return None
    except Exception as e:
        log_function("get_pokemon_by_id", f"Unresolfed error occured! Error:{e}", "error")
        return None


# TODO: check id < 0
def get_pokesprite_url_by_id(poke_id: int, depth = 0) -> str:
    if depth > 1:
        log_function("get_pokesprite_url_by_id", f"Could not load sprite for pokemon with id {poke_id}", "error")
        return ""
    
    try:
        sprite_path = ""
        if depth == 0:
            log_function("get_pokesprite_url_by_id", "Loading pokemon sprite from cache")
            sprite_path = pb.cache.load_sprite("pokemon", poke_id)["path"].split("static")[1].replace("\\", "/")
            log_function("get_pokesprite_url_by_id", "Loaded pokemon sprite from cache successfuly")
            return sprite_path
        if depth == 1:
            log_function("get_pokesprite_url_by_id","Fetching pokemon sprite from api")
            sprite_path = pb.SpriteResource('pokemon', poke_id).path.split("static")[1].replace("\\", "/")
            log_function("get_pokesprite_url_by_id", "Fetched pokemon sprite from api successfuly")
        return sprite_path
    except FileNotFoundError as e:
        if depth == 0:
            log_function("get_pokesprite_url_by_id", "Loading pokemon sprite from cache failed. Sprite not found.")
            return get_pokesprite_url_by_id(poke_id, depth+1)
        else:
            log_function("get_pokesprite_url_by_id", f"KeyError on depth != 0! Error: {e}", "error")
            return ""
    except Exception as e:
        log_function("get_pokesprite_url_by_id", f"Failed fetching sprite for pokemon with id {poke_id}. Error: {e}", "error")
        return ""