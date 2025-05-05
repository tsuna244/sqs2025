import pokebase as pb
from enum import Enum

STATIC_FOLDER = "api/static/"

CACHE_DIR = STATIC_FOLDER + ".cache/"

pb.cache.set_cache(CACHE_DIR)

from .module_logger import log_function

MODULE_NAME="module_pokeapi"

class PokemonRarity(Enum):
    NORMAL = "normal"
    LEGENDARY = "legendary"
    MYTHIC = "mythical"


# utility function: check function for integer values (poke_id and depth)
def check_input(function_name: str, input, val_name: str) -> int:
    try:
        return int(input)
    except ValueError:
        log_function(MODULE_NAME, function_name, f"{val_name} must be an integer or a string containing an integer!!! {val_name} = {input}", "error")
        return -1


def get_pokemon_id_names_by_generation(generation: int, depth=0) -> list:
    # declare func_name for logging
    func_name = "get_pokemon_id_names_by_generation"
    
    generation = check_input(func_name, generation, "generation")
    depth = check_input(func_name, depth, "depth")
    
    # check if poke id and depth are positive integers (pokemon id must be 1 or above)
    if generation < 0 or depth < 0:
        return []
    
    if generation < 1 or generation > 3:
        log_function(MODULE_NAME, func_name, "Generation must be between 1 and 3", "error")
        return []
    
    if depth > 1:
        log_function(MODULE_NAME, func_name, f"Could not fetch pokemon name list by generation id {generation}", "error")
        return []

    try:
        # use cache load function !!!
        if depth == 0:
            log_function(MODULE_NAME, func_name, "Try loading from cache")
            gen_resource = pb.cache.load("generation", generation)
            log_function(MODULE_NAME, func_name, "Successfully loaded from cache")
            pokemon_list = []
            for pokemon_source in gen_resource["pokemon_species"]:
                poke_id = int(pokemon_source["url"].split("/")[-2]) # fetch id out of url
                pokemon_list.append({"pokemon_id": poke_id, "pokemon_name": pokemon_source["name"]})
            return pokemon_list
        # use api load function !!!
        elif depth == 1:
            log_function(MODULE_NAME, func_name, "Try fetching from api")
            gen_resource = pb.generation(generation)
            log_function(MODULE_NAME, func_name, "Successfully fetched from api")
            pokemon_list = []
            for pokemon_source in gen_resource.pokemon_species:
                pokemon_list.append({"pokemon_id": pokemon_source.id_, "pokemon_name": pokemon_source.name}) # add pokemon rarity
            return pokemon_list
    # key error occurs if load function cant find a fetch for the generation value hence try api call first
    except KeyError as e:
        if depth == 0:
            log_function(MODULE_NAME, func_name, "Could not find name list in cache. Will try api fetch next")
            return get_pokemon_id_names_by_generation(generation, depth + 1)
        else:
            log_function(MODULE_NAME, func_name, f"KeyError on depth != 0! Error: {e.__str__()}", "error")
            return []
    except Exception as e:
        log_function(MODULE_NAME, func_name, f"Unresolfed error occured! Error:{e.__str__()}", "error")
        return []


def get_pokemon_rarity_and_generation_by_id(poke_id: int, depth = 0) -> dict:
    # declare func_name for logging
    func_name = "get_pokemon_rarity_and_generation_by_id"
    
    poke_id = check_input(func_name, poke_id, "poke_id")
    depth = check_input(func_name, depth, "depth")
    
    # check if poke id and depth are positive integers (pokemon id must be 1 or above)
    if poke_id < 1 or depth < 0:
        return {}
    
    # check depth
    if depth > 1:
        log_function(MODULE_NAME, func_name, f"Could not load pokemon with id {poke_id}", "error")
        return {}
    
    try:
        if depth == 0:
            log_function(MODULE_NAME, func_name, "Loading pokemon species from cache")
            pokemon_species = pb.cache.load("pokemon-species", poke_id)
            log_function(MODULE_NAME, func_name, "Loaded pokemon species from cache successful")
            rarity = PokemonRarity.NORMAL
            if pokemon_species["is_mythical"]:
                rarity = PokemonRarity.MYTHIC
            if pokemon_species["is_legendary"]:
                rarity = PokemonRarity.LEGENDARY
            pokemon_gen_id = pokemon_species["generation"]["url"].split("/")[-2]
            return {"pokemon_rarity": rarity, "pokemon_gen_id": pokemon_gen_id, "pokemon_gen_name": pokemon_species["generation"]["name"]}
        elif depth == 1:
            log_function(MODULE_NAME, func_name, "Fetching pokemon species from api")
            pokemon_species = pb.pokemon_species(poke_id)
            log_function(MODULE_NAME, func_name, "Fetched pokemon species from api successful")
            rarity = PokemonRarity.NORMAL
            if pokemon_species.is_mythical:
                rarity = PokemonRarity.MYTHIC
            if pokemon_species.is_legendary:
                rarity = PokemonRarity.LEGENDARY
            pokemon_gen_id = pokemon_species.generation.url.split("/")[-2]
            return {"pokemon_rarity": rarity, "pokemon_gen_id": pokemon_gen_id, "pokemon_gen_name": pokemon_species.generation.__getattr__("name")}
    except KeyError as e:
        if depth == 0:
            log_function(MODULE_NAME, func_name, "Could not find pokemon species in cache. Will try api fetch next")
            return get_pokemon_rarity_and_generation_by_id(poke_id, depth + 1)
        else:
            log_function(MODULE_NAME, func_name, f"KeyError on depth != 0! Error: {e.__str__()}", "error")
            return {}
    except Exception as e:
        log_function(MODULE_NAME, func_name, f"Unresolfed error occured! Error: {e.__str__()}", "error")
        return {}


def get_pokemon_by_id(poke_id: int, depth = 0) -> dict:
    # declare func_name for logging
    func_name = "get_pokemon_by_id"
    
    poke_id = check_input(func_name, poke_id, "poke_id")
    depth = check_input(func_name, depth, "depth")
    
    # check if poke id and depth are positive integers (pokemon id must be 1 or above)
    if poke_id < 1 or depth < 0:
        return {}
    
    # check depth
    if depth > 1:
        log_function(MODULE_NAME, func_name, f"Could not load pokemon with id {poke_id}", "error")
        return {}
    
    # try to fetch pokemon from database
    try:
        if depth == 0:
            log_function(MODULE_NAME, func_name, f"Try loading from cache for pokemon id {poke_id}")
            poke_resource = pb.cache.load("pokemon", poke_id)
            log_function(MODULE_NAME, func_name, f"Successfully loaded from cache for pokemon id {poke_id}")
            
            poke_stats = []
            
            for stat in poke_resource["stats"]:
                poke_stats.append({"stat_name": stat["stat"]["name"], "stat_value": stat["base_stat"]})
            
            return {"pokemon_id": poke_resource["id"], "pokemon_name": poke_resource["name"], "pokemon_stats": poke_stats}
        # use api load function !!!
        elif depth == 1:
            log_function(MODULE_NAME, func_name, f"Try fetching from api for pokemon id {poke_id}")
            poke_resource = pb.pokemon(poke_id)
            log_function(MODULE_NAME, func_name, f"Successfully fetched from api for pokemon id {poke_id}")
            
            poke_stats = []
            
            for stat in poke_resource.stats:
                poke_stats.append({"stat_name": stat.stat.__getattr__("name"), "stat_value": stat.base_stat})
            
            return {"pokemon_id": poke_resource.id, "pokemon_name": poke_resource.name, "pokemon_stats": poke_stats}
    except KeyError as e:
        if depth == 0:
            log_function(MODULE_NAME, func_name, f"Could not find name list in cache. Will try api fetch next for pokemon id {poke_id}")
            return get_pokemon_by_id(poke_id, depth + 1)
        else:
            log_function(MODULE_NAME, func_name, f"KeyError on depth != 0! Error: {e.__str__()}", "error")
            return {}
    except Exception as e:
        log_function(MODULE_NAME, func_name, f"Unresolfed error occured for pokemon id {poke_id}! Error:{e.__str__()}", "error")
        return {}


def get_pokesprite_url_by_id(poke_id: int, depth = 0) -> str:
    # declare func_name for logging
    func_name = "get_pokesprite_url_by_id"
    
    poke_id = check_input(func_name, poke_id, "poke_id")
    depth = check_input(func_name, depth, "depth")
    
    # check if poke id and depth are positive integers (pokemon id must be 1 or above)
    if poke_id < 1 or depth < 0:
        return ""
    
    # cast to int
    poke_id = int(poke_id)
    depth = int(depth)
    
    # check depth
    if depth > 1:
        log_function(MODULE_NAME, func_name, f"Could not load sprite for pokemon with id {poke_id}", "error")
        return ""
    
    # try fetching pokesprite url
    try:
        sprite_path = ""
        if depth == 0:
            log_function(MODULE_NAME, func_name, f"Loading pokemon sprite from cache for pokemon id: {poke_id}")
            sprite_path = pb.cache.load_sprite("pokemon", poke_id)["path"].split("static")[1].replace("\\", "/")
            log_function(MODULE_NAME, func_name, f"Loaded pokemon sprite from cache successfuly for pokemon id: {poke_id}")
            return sprite_path
        if depth == 1:
            log_function(MODULE_NAME, func_name, f"Fetching pokemon sprite from api for pokemon id: {poke_id}")
            sprite_path = pb.SpriteResource('pokemon', poke_id).path.split("static")[1].replace("\\", "/")
            log_function(MODULE_NAME, func_name, f"Fetched pokemon sprite from api successfuly for pokemon id: {poke_id}")
        return sprite_path
    except FileNotFoundError as e:
        if depth == 0:
            log_function(MODULE_NAME, func_name, f"Loading pokemon sprite from cache failed. Sprite not found for pokemon id: {poke_id}")
            return get_pokesprite_url_by_id(poke_id, depth+1)
        else:
            log_function(MODULE_NAME, func_name, f"KeyError on depth != 0! Error: {e.__str__()}", "error")
            return ""
    except Exception as e:
        log_function(MODULE_NAME, func_name, f"Failed fetching sprite for pokemon id {poke_id}. Error: {e.__str__()}", "error")
        return ""