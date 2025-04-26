from api.modules.module_pokeapi import *
import tempfile
import shutil
import os
import pytest

# setup temporary cache for testing environment (has to include static for the function to work)
@pytest.fixture(autouse=True)
def manage_test_environment():
    # create TMP_DIR and setup caching
    TMP_DIR = tempfile.mkdtemp()
    TMP_CACHE = TMP_DIR + "/static/.cache/"
    pb.cache.set_cache(TMP_CACHE)
    
    # execute tests
    yield

    # cleanup
    shutil.rmtree(TMP_DIR)

def test_get_pokesprite_url_by_id():
    test_id = 20
    expected_result = "/.cache/sprite/pokemon/20.png"
    
    # should success
    
    # url should be uncached -> should use api call
    suc_uncached_url = get_pokesprite_url_by_id(test_id, 0)
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
    
    # use depth value higher than 2 -> should fail since depth value over 2 causes interrupt
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
