from api.modules.module_pokeapi import *
from api.modules.module_pokeapi import _check_generation_and_depth, _check_poke_rarity
import tempfile
import shutil
import pytest


# setup temporary cache for testing environment (has to include static for the function to work)
@pytest.fixture(autouse=True)
def manage_test_environment():
    # create TMP_DIR and setup caching
    TMP_DIR = tempfile.mkdtemp()
    TMP_CACHE = TMP_DIR + "/static/.cache/"
    pb.cache.set_cache(TMP_CACHE)
    FILE_CACHE_NAME = CACHE_DIR + "test_cache.json"

    # execute tests
    yield

    # cleanup
    shutil.rmtree(TMP_DIR)

def test_cached_name_id_list():
    # adding name and write test value to have test file (if not working second assert will fail -> tests add name function as well)
    add_name_id_to_cache("./test_cache.json", "ditto", 132)
    # try loading non existing cache file
    assert load_cached_name_id_list("nonexisting.txt") == {}
    # try loading succesfully (test add name id function as well)
    assert load_cached_name_id_list("./test_cache.json") == {"ditto": 132}
    # remove test file
    os.remove("./test_cache.json")

def test_check_pokemon_name():
    # pokename not str
    assert check_pokemon_name("test_func", 123) == -1
    # pokename is none
    assert check_pokemon_name("test_func", None) == -1
    # pokemonname empty
    assert check_pokemon_name("test_func", "") == -1
    # pokemonname contains digit
    assert check_pokemon_name("test_func", "ditto1") == -1
    # pokemonname has other char than letter
    assert check_pokemon_name("test_func", "ditto*") == -1
    # pokename is fine
    assert check_pokemon_name("test_func", "ditto") == 0

def test_check_input():
    func_name="test_check_input"
    value_name="test_value"
    assert check_input(func_name, "asdf", value_name) == -1
    assert check_input(func_name, "123", value_name) == 123
    assert check_input(func_name, 123, value_name) == 123
    assert check_input(func_name, -4, value_name) == -1
    assert check_input(func_name, "-2", value_name) == -1


def test_check_gen_and_depth():
    func_name="test_check_gen_and_depth"
    assert _check_generation_and_depth(func_name, -1, 1) == 1
    assert _check_generation_and_depth(func_name, 1, -1) == 1
    assert _check_generation_and_depth(func_name, 0, 1) == 2
    assert _check_generation_and_depth(func_name, 4, 1) == 2
    assert _check_generation_and_depth(func_name, 1, 2) == 3
    assert _check_generation_and_depth(func_name, 2, 1) == 0
    
    
def test_check_poke_rarity():
    # test for cached pokemon species
    cached_pokemon_species_mock = {"is_legendary": True, "is_mythical": False}
    assert _check_poke_rarity(cached_pokemon_species_mock) == PokemonRarity.LEGENDARY
    cached_pokemon_species_mock = {"is_legendary": False, "is_mythical": True}
    assert _check_poke_rarity(cached_pokemon_species_mock) == PokemonRarity.MYTHIC
    cached_pokemon_species_mock = {"is_legendary": False, "is_mythical": False}
    assert _check_poke_rarity(cached_pokemon_species_mock) == PokemonRarity.NORMAL
    
    class pokemon_species_mock():
        is_legendary = True
        is_mythical = False
    
    fetched_PSM = pokemon_species_mock()
    assert _check_poke_rarity(fetched_PSM, False) == PokemonRarity.LEGENDARY
    fetched_PSM.is_legendary = False
    assert _check_poke_rarity(fetched_PSM, False) == PokemonRarity.NORMAL
    fetched_PSM.is_mythical = True
    assert _check_poke_rarity(fetched_PSM, False) == PokemonRarity.MYTHIC
    

def test_get_pokemon_by_id_from_name():
    assert get_pokemon_id_from_name(123) == -1
    # should not exist yet
    assert get_pokemon_id_from_name("ditto") == 132
    # should exist now
    assert get_pokemon_id_from_name("ditto") == 132
    # non existing pokemon
    assert get_pokemon_id_from_name("doesnotexist") == -1

def test_get_pokesprite_url_by_id():
    test_id = 20
    expected_result = "/.cache/sprite/pokemon/20.png"
    
    # should success
    
    # url should be uncached -> should use api call
    suc_uncached_url = get_pokesprite_url_by_id(test_id)
    assert suc_uncached_url == expected_result
    # url should be cached by now -> should load from cache
    suc_cached_url = get_pokesprite_url_by_id(test_id, 0)
    assert suc_cached_url == expected_result
    # url should be cached but depth 1 forces api call -> should use api call
    suc_cached_depth_1 = get_pokesprite_url_by_id(test_id, 1)
    assert suc_cached_depth_1 == expected_result
    # using string input containing integer -> should work without problems
    suc_str_int_input = get_pokesprite_url_by_id(f"{test_id}", "1")
    assert suc_str_int_input == expected_result
    
    # should fail
    
    # use depth value higher than 2 -> should fail since depth value over 1 causes interrupt
    err_depth_fail = get_pokesprite_url_by_id(test_id, 2)
    assert err_depth_fail == ""
    # use non integer input inside of string for pokemon id
    err_value_error_poke_id = get_pokesprite_url_by_id("2.2", 0)
    assert err_value_error_poke_id == ""
    # use non integer input inside of string for depth value
    err_value_error_depth = get_pokesprite_url_by_id(f"{test_id}", "3.2")
    assert err_value_error_depth == ""
    # use negative value
    err_value_error_negative_pokemon = get_pokesprite_url_by_id(-2, 0)
    assert err_value_error_negative_pokemon == ""
    err_value_error_negative_depth = get_pokesprite_url_by_id(2, -2)
    assert err_value_error_negative_depth == ""
    # use pokemon id 0
    err_value_error_poke_id_zero = get_pokesprite_url_by_id(0, 0)
    assert err_value_error_poke_id_zero == ""


def test_get_pokemon_by_id():
    test_id = 30
    expected_result =   {
                        'pokemon_id': 30, 
                        'pokemon_name': 'nidorina',
                        'pokemon_stats': [
                            {'stat_name': 'hp', 'stat_value': 70}, 
                            {'stat_name': 'attack', 'stat_value': 62}, 
                            {'stat_name': 'defense', 'stat_value': 67}, 
                            {'stat_name': 'special-attack', 'stat_value': 55}, 
                            {'stat_name': 'special-defense', 'stat_value': 55}, 
                            {'stat_name': 'speed', 'stat_value': 56}]
                        }
    
    # should success
    
    # pokemon object should be uncached -> should use api call
    suc_uncached_pokemon = get_pokemon_by_id(test_id)
    assert suc_uncached_pokemon == expected_result
    # pokemon object should be cached -> should load from cache
    suc_cached_pokemon = get_pokemon_by_id(test_id)
    assert suc_cached_pokemon == expected_result
    # pokemon object should be cached but depth 1 forces api call -> should use api call
    suc_cached_depth_1 = get_pokemon_by_id(test_id, 1)
    assert suc_cached_depth_1 == expected_result
    # using string input containing integer -> should work without problems
    suc_str_int_input = get_pokemon_by_id(f"{test_id}", "1")
    assert suc_str_int_input == expected_result
    
    # should fail
    
    # use depth value higher than 2 -> should fail since depth value over 1 causes interrupt
    err_depth_fail = get_pokemon_by_id(test_id, 2)
    assert err_depth_fail == {}
    # use non integer input inside of string for pokemon id
    err_value_error_poke_id = get_pokemon_by_id("2.2", 0)
    assert err_value_error_poke_id == {}
    # use non integer input inside of string for depth value
    err_value_error_depth = get_pokemon_by_id(f"{test_id}", "3.2")
    assert err_value_error_depth == {}
    # use negative value
    err_value_error_negative_pokemon = get_pokemon_by_id(-2, 0)
    assert err_value_error_negative_pokemon == {}
    err_value_error_negative_depth = get_pokemon_by_id(2, -2)
    assert err_value_error_negative_depth == {}
    # use pokemon id 0
    err_value_error_poke_id_zero = get_pokemon_by_id(0, 0)
    assert err_value_error_poke_id_zero == {}


def test_get_pokemon_rarity_and_generation_by_id():
    test_id = 30
    expected_result = {"pokemon_rarity": PokemonRarity.NORMAL, "pokemon_gen_id": '1', "pokemon_gen_name": "generation-i"}
    
    # should success
    
    # pokemon rarity should be uncached -> should use api call
    suc_uncached_pokemon = get_pokemon_rarity_and_generation_by_id(test_id)
    assert suc_uncached_pokemon == expected_result
    # pokemon rarity should be cached -> should load from cache
    suc_cached_pokemon = get_pokemon_rarity_and_generation_by_id(test_id)
    assert suc_cached_pokemon == expected_result
    # pokemon rarity should be cached but depth 1 forces api call -> should use api call
    suc_cached_depth_1 = get_pokemon_rarity_and_generation_by_id(test_id, 1)
    assert suc_cached_depth_1 == expected_result
    # using string input containing integer -> should work without problems
    suc_str_int_input = get_pokemon_rarity_and_generation_by_id(f"{test_id}", "1")
    assert suc_str_int_input == expected_result
    
    # should fail
    
    # use depth value higher than 2 -> should fail since depth value over 1 causes interrupt
    err_depth_fail = get_pokemon_rarity_and_generation_by_id(test_id, 2)
    assert err_depth_fail == {}
    # use non integer input inside of string for pokemon id
    err_value_error_poke_id = get_pokemon_rarity_and_generation_by_id("2.2", 0)
    assert err_value_error_poke_id == {}
    # use non integer input inside of string for depth value
    err_value_error_depth = get_pokemon_rarity_and_generation_by_id(f"{test_id}", "3.2")
    assert err_value_error_depth == {}
    # use negative value
    err_value_error_negative_pokemon = get_pokemon_rarity_and_generation_by_id(-2, 0)
    assert err_value_error_negative_pokemon == {}
    err_value_error_negative_depth = get_pokemon_rarity_and_generation_by_id(2, -2)
    assert err_value_error_negative_depth == {}
    # use pokemon id 0
    err_value_error_poke_id_zero = get_pokemon_rarity_and_generation_by_id(0, 0)
    assert err_value_error_poke_id_zero == {}
    

def test_get_pokemon_id_names_by_generation():
    test_id = 1
    
    # should success
    
    # pokemon list should be uncached -> should use api call
    suc_uncached_pokemon = get_pokemon_id_names_by_generation(test_id)
    assert len(suc_uncached_pokemon) > 0
    # pokemon list should be cached -> should load from cache
    suc_cached_pokemon = get_pokemon_id_names_by_generation(test_id)
    assert len(suc_cached_pokemon) > 0
    # pokemon list should be cached but depth 1 forces api call -> should use api call
    suc_cached_depth_1 = get_pokemon_id_names_by_generation(test_id, 1)
    assert len(suc_cached_depth_1) > 0
    # using string input containing integer -> should work without problems
    suc_str_int_input = get_pokemon_id_names_by_generation(f"{test_id}", "1")
    assert len(suc_str_int_input) > 0
    
    # should fail
    
    # use depth value higher than 2 -> should fail since depth value over 1 causes interrupt
    err_depth_fail = get_pokemon_id_names_by_generation(test_id, 2)
    assert len(err_depth_fail) == 0
    # use non integer input inside of string for pokemon id
    err_value_error_gen_id = get_pokemon_id_names_by_generation("2.2", 0)
    assert len(err_value_error_gen_id) == 0
    # use non integer input inside of string for depth value
    err_value_error_depth = get_pokemon_id_names_by_generation(f"{test_id}", "3.2")
    assert len(err_value_error_depth) == 0
    # use negative value
    err_value_error_negative_gen = get_pokemon_id_names_by_generation(-2, 0)
    assert len(err_value_error_negative_gen) == 0
    err_value_error_negative_depth = get_pokemon_id_names_by_generation(2, -2)
    assert len(err_value_error_negative_depth) == 0
    # use generation id 0
    err_value_error_gen_id_zero = get_pokemon_id_names_by_generation(0, 0)
    assert len(err_value_error_gen_id_zero) == 0
    # use geneartion id 4+ since gen must be between 1-3
    err_value_error_gen_id_4_plus = get_pokemon_id_names_by_generation(4, 0)
    assert len(err_value_error_gen_id_4_plus) == 0