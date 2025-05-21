import pokebase as pb
from enum import Enum
import re
import json
import os

# set chache folder for pokebase
STATIC_FOLDER = "api/static/"

CACHE_DIR = STATIC_FOLDER + ".cache/"

pb.cache.set_cache(CACHE_DIR)

FILE_CACHE_NAME = CACHE_DIR + "cache_ids.json"

from .module_logger import log_function

MODULE_NAME="module_pokeapi"

class PokemonRarity(Enum):
    """This Enum class represents the 3 types of pokemon rarity, None type is only a placeholder in case a pokemon could not be fetched from the api
    """
    NONE = "none"
    NORMAL = "normal"
    LEGENDARY = "legendary"
    MYTHIC = "mythical"


def load_cached_name_id_list(file_path):
    if os.path.exists(file_path):
        with open(file_path) as file:
            return json.load(file)#
    else:
        return {}

def add_name_id_to_cache(file_path, poke_name: str, poke_id: int):
    current_cache = load_cached_name_id_list(file_path)
    current_cache[poke_name] = poke_id
    with open(file_path, "w") as file:
        json.dump(current_cache, file)

# utility function: check function for integer values (poke_id and depth)
def check_input(function_name: str, input: int, val_name: str) -> int:
    """Checks if the input value is a postive integer. Returns -1 if not

    :param function_name: The name of the function that calls the check (used for logging)
    :type function_name: str
    :param input: the input that will be checked
    :type input: int
    :param val_name: the name of the input that is beeing checked (used for logging)
    :type val_name: str
    :return: `-1` if the input is not an integer or negative, `input` value as integer otherwise
    :rtype: int
    """
    
    try:
        val = int(input)
        if val < 0:
            return -1
        return val
    except ValueError:
        log_function(MODULE_NAME, function_name, f"{val_name} must be an integer or a string containing an integer!!! {val_name} = {input}", "error")
        return -1


def check_pokemon_name(function_name: str, pokemon_name: str):
    """Checks if the pokemon name is correct. returns -1 if not

    :param function_name: The name of the function that calls the check (used for logging)
    :type function_name: str
    :param pokemon_name: the pokemon name to check
    :type pokemon_name: str
    :return: `-1` if the pokemon name is wrong, '0' otherwise
    :rtype: int
    """
    if pokemon_name is None:
        log_function(MODULE_NAME, function_name, f"Pokemon name must not be None!!! Pokemon_name = {pokemon_name}", "error")
        return -1

    if not isinstance(pokemon_name, str):
        log_function(MODULE_NAME, function_name, "Pokemon name must be of type str", "error")
        return -1

    regex = re.compile('[^a-zA-Z]+')
    if pokemon_name == "":
        log_function(MODULE_NAME, function_name, f"Pokemon name must not be emtpy!!! Pokemon_name = {pokemon_name}", "error")
        return -1
    if any(char.isdigit() for char in pokemon_name):
        log_function(MODULE_NAME, function_name, f"Pokemon name must not contain digits!!! Pokemon_name = {pokemon_name}", "error")
        return -1
    if regex.search(pokemon_name):
        log_function(MODULE_NAME, function_name, f"Pokemon name must not contain special characters!!! Pokemon_name = {pokemon_name}", "error")
        return -1
    log_function(MODULE_NAME, function_name, f"Pokemon name checked successfully!!! Pokemon_name = {pokemon_name}")
    return 0


def _check_generation_and_depth(func_name: str, generation: int, depth: int):
    """Checks if the generation input and the depth input are correct

    :param func_name: The name of the function that calls the check (used for logging)
    :type func_name: str
    :param generation: the pokemon generation value
    :type generation: int
    :param depth: the depth value of the function
    :type depth: int
    :return: `0` if successful, `1` if one of both integer are less then 0, `2` if the generation is not between 1 and 3, `3` if depth is greater than 1
    :rtype: int
    """
    
    if generation < 0 or depth < 0:
        log_function(MODULE_NAME, func_name, "Generation must be between 1 and 3", "error")
        return 1
    if generation < 1 or generation > 3:
        log_function(MODULE_NAME, func_name, "Generation must be between 1 and 3", "error")
        return 2
    if depth > 1:
        log_function(MODULE_NAME, func_name, f"Could not fetch pokemon name list by generation id {generation}", "error")
        return 3
    return 0


def _check_poke_rarity(pokemon_species, is_cache=True):
    """Checks the rarity of a pokemon

    :param pokemon_species: the pokemon_species object of the pokebase api fetch
    :type pokemon_species: dict | pokebase.APIResource
    :param is_cache: tells if the pokemon_species object is from the cache or directly from the pokebase api, defaults to True
    :type is_cache: bool, optional
    :return: returns the rarity of the pokemon
    :rtype: PokemonRarity
    """
    
    if is_cache:
        if pokemon_species["is_mythical"]:
            return PokemonRarity.MYTHIC
        elif pokemon_species["is_legendary"]:
            return PokemonRarity.LEGENDARY
        else:
            return PokemonRarity.NORMAL
    else:
        if pokemon_species.is_mythical:
            return PokemonRarity.MYTHIC
        elif pokemon_species.is_legendary:
            return PokemonRarity.LEGENDARY
        else:
            return PokemonRarity.NORMAL

def get_pokemon_id_names_by_generation(generation: int, depth=0) -> list:
    """Returns a list with all the pokemon for the given generation containing their pokemon id and name

    :param generation: the pokemon generation (only between 1 and 3)
    :type generation: int
    :param depth: `0` => load from cache, `1` => fetch from pokebase api, `otherwise` => fetch failed, defaults to 0
    :type depth: int, optional
    :return:  returns a list with the pokemon for the given generation. `[]` if any check fails
    :rtype: list
    """
    
    # declare func_name for logging
    func_name = "get_pokemon_id_names_by_generation"
    
    # check input
    generation = check_input(func_name, generation, "generation")
    depth = check_input(func_name, depth, "depth")
    
    # check if generation id and depth are positive integers (pokemon id must be 1 or above)
    if _check_generation_and_depth(func_name, generation, depth) != 0:
        return []

    try:
        # use cache load function !!!
        if depth == 0:
            log_function(MODULE_NAME, func_name, "Try loading from cache")
            gen_resource = pb.cache.load("generation", generation)
            log_function(MODULE_NAME, func_name, "Successfully loaded from cache")
            pokemon_list = []
            # for each pokemon in the list of pokemon
            for pokemon_source in gen_resource["pokemon_species"]:
                # fetch id out of url and append to list
                poke_id = int(pokemon_source["url"].split("/")[-2])
                pokemon_list.append({"pokemon_id": poke_id, "pokemon_name": pokemon_source["name"]})
            return pokemon_list
        # use api load function !!!
        elif depth == 1:
            log_function(MODULE_NAME, func_name, "Try fetching from api")
            gen_resource = pb.generation(generation)
            log_function(MODULE_NAME, func_name, "Successfully fetched from api")
            pokemon_list = []
            for pokemon_source in gen_resource.pokemon_species:
                pokemon_list.append({"pokemon_id": pokemon_source.id_, "pokemon_name": pokemon_source.name})
            return pokemon_list
    # key error occurs if load function cant find a fetch for the generation value hence try api call first
    except KeyError as e:
        # if depth was 0 -> not found in cache
        if depth == 0:
            log_function(MODULE_NAME, func_name, "Could not find name list in cache. Will try api fetch next")
            return get_pokemon_id_names_by_generation(generation, depth + 1)
        else: # this occurs it it was a KeyError for the api fetch
            log_function(MODULE_NAME, func_name, f"KeyError on depth != 0! Error: {e.__str__()}", "error")
            return []
    except Exception as e:
        log_function(MODULE_NAME, func_name, f"Unresolfed error occured! Error:{e.__str__()}", "error")
        return []


def get_pokemon_id_from_name(pokemon_name: str) -> int:
    func_name = "get_pokemon_id_from_name"
    
    if check_pokemon_name(func_name, pokemon_name) == -1:
        return -1
    
    try:
        log_function(MODULE_NAME, func_name, "Loading pokemon id from cache")
        cached_name_id_list = load_cached_name_id_list(FILE_CACHE_NAME)
        if pokemon_name in cached_name_id_list:
            log_function(MODULE_NAME, func_name, "Loaded pokemon id from cache successful")
            return cached_name_id_list[pokemon_name]
        else:
            # fetch from api if loading from cache failed
            log_function(MODULE_NAME, func_name, "Fetching pokemon id from api")
            pokemon_species = pb.pokemon_species(pokemon_name)
            log_function(MODULE_NAME, func_name, "Fetched pokemon id from api successful")
            add_name_id_to_cache(FILE_CACHE_NAME, pokemon_name, pokemon_species.id)
            return pokemon_species.id
    except KeyError as e:
        # otherwise its a keyerror from api -> error return {}
        log_function(MODULE_NAME, func_name, f"KeyError! Could not get pokemon id for name {pokemon_name} Error: {e.__str__()}", "error")
        return -1
    except Exception as e:
        log_function(MODULE_NAME, func_name, f"Unresolfed error occured! Error: {e.__str__()}", "error")
        return -1

def get_pokemon_rarity_and_generation_by_id(poke_id: int, depth = 0) -> dict:
    """Returns the rarity and generation of a pokemon given its id

    :param poke_id: id of the pokemon
    :type poke_id: int
    :param depth: `0` => load from cache, `1` => fetch from pokebase api, `otherwise` => fetch failed, defaults to 0
    :type depth: int, optional
    :return: `{}` if fetch fails. `{"pokemon_rarity": <rarity>, "pokemon_gen_id": <generation_id>, "pokemon_gen_name": <generation>}` if successfull
    :rtype: dict
    """
    
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
        # try loading from cache
        if depth == 0:
            log_function(MODULE_NAME, func_name, "Loading pokemon species from cache")
            pokemon_species = pb.cache.load("pokemon-species", poke_id)
            log_function(MODULE_NAME, func_name, "Loaded pokemon species from cache successful")
            # check the rarity of pokemon and get id from generations url
            rarity = _check_poke_rarity(pokemon_species)
            pokemon_gen_id = pokemon_species["generation"]["url"].split("/")[-2]
            return {"pokemon_rarity": rarity, "pokemon_gen_id": pokemon_gen_id, "pokemon_gen_name": pokemon_species["generation"]["name"]}
        elif depth == 1:
            # fetch from api if loading from cache failed
            log_function(MODULE_NAME, func_name, "Fetching pokemon species from api")
            pokemon_species = pb.pokemon_species(poke_id)
            log_function(MODULE_NAME, func_name, "Fetched pokemon species from api successful")
            rarity = _check_poke_rarity(pokemon_species, False)
            pokemon_gen_id = pokemon_species.generation.url.split("/")[-2]
            return {"pokemon_rarity": rarity, "pokemon_gen_id": pokemon_gen_id, "pokemon_gen_name": pokemon_species.generation.__getattr__("name")}
    except KeyError as e:
        # keyerror for cache -> retry fetching from api
        if depth == 0:
            log_function(MODULE_NAME, func_name, "Could not find pokemon species in cache. Will try api fetch next")
            return get_pokemon_rarity_and_generation_by_id(poke_id, depth + 1)
        else:
            # otherwise its a keyerror from api -> error return {}
            log_function(MODULE_NAME, func_name, f"KeyError on depth != 0! Error: {e.__str__()}", "error")
            return {}
    except Exception as e:
        log_function(MODULE_NAME, func_name, f"Unresolfed error occured! Error: {e.__str__()}", "error")
        return {}


def get_pokemon_by_id(poke_id: int, depth = 0) -> dict:
    """Returns information of a pokemon with the given poke_id

    :param poke_id: id of the pokemon
    :type poke_id: int
    :param depth: `0` => load from cache, `1` => fetch from pokebase api, `otherwise` => fetch failed, defaults to 0
    :type depth: int, optional
    :return: `{}` if fetch fails, `{"pokemon_id": <pokemon_id>, "pokemon_name": <pokemon_name>, "pokemon_stats": <poke_stats>}` if successfull
    :rtype: dict
    """
    
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
        # load from cache
        if depth == 0:
            log_function(MODULE_NAME, func_name, f"Try loading from cache for pokemon id {poke_id}")
            poke_resource = pb.cache.load("pokemon", poke_id)
            log_function(MODULE_NAME, func_name, f"Successfully loaded from cache for pokemon id {poke_id}")
            
            poke_stats = []
            
            for stat in poke_resource["stats"]:
                poke_stats.append({"stat_name": stat["stat"]["name"], "stat_value": stat["base_stat"]})
            
            return {"pokemon_id": poke_resource["id"], "pokemon_name": poke_resource["name"], "pokemon_stats": poke_stats}
        elif depth == 1: # fetch from api
            log_function(MODULE_NAME, func_name, f"Try fetching from api for pokemon id {poke_id}")
            poke_resource = pb.pokemon(poke_id)
            log_function(MODULE_NAME, func_name, f"Successfully fetched from api for pokemon id {poke_id}")
            
            poke_stats = []
            
            for stat in poke_resource.stats:
                poke_stats.append({"stat_name": stat.stat.__getattr__("name"), "stat_value": stat.base_stat})
            
            return {"pokemon_id": poke_resource.id, "pokemon_name": poke_resource.name, "pokemon_stats": poke_stats}
    except KeyError as e:
        # load from cache failed -> retry with api fetch
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
    """Returns an url to the sprite of the pokemon with poke_id

    :param poke_id: id of the pokemon
    :type poke_id: int
    :param depth: `0` => load from cache, `1` => fetch from pokebase api, `otherwise` => fetch failed, defaults to 0
    :type depth: int, optional
    :return: Returns empty string if fetch fails. Returns a string containing the path to the sprite of the pokemon if successfull
    :rtype: str
    """
    
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
        # load from cache
        if depth == 0:
            log_function(MODULE_NAME, func_name, f"Loading pokemon sprite from cache for pokemon id: {poke_id}")
            sprite_path = pb.cache.load_sprite("pokemon", poke_id)["path"].split("static")[1].replace("\\", "/")
            log_function(MODULE_NAME, func_name, f"Loaded pokemon sprite from cache successfuly for pokemon id: {poke_id}")
            return sprite_path
        if depth == 1:
            # fetch from api
            log_function(MODULE_NAME, func_name, f"Fetching pokemon sprite from api for pokemon id: {poke_id}")
            sprite_path = pb.SpriteResource('pokemon', poke_id).path.split("static")[1].replace("\\", "/")
            log_function(MODULE_NAME, func_name, f"Fetched pokemon sprite from api successfuly for pokemon id: {poke_id}")
        return sprite_path
    except FileNotFoundError as e:
        # load from cache failed -> try fetching from api
        if depth == 0:
            log_function(MODULE_NAME, func_name, f"Loading pokemon sprite from cache failed. Sprite not found for pokemon id: {poke_id}")
            return get_pokesprite_url_by_id(poke_id, depth+1)
        else:
            log_function(MODULE_NAME, func_name, f"KeyError on depth != 0! Error: {e.__str__()}", "error")
            return ""
    except Exception as e:
        log_function(MODULE_NAME, func_name, f"Failed fetching sprite for pokemon id {poke_id}. Error: {e.__str__()}", "error")
        return ""