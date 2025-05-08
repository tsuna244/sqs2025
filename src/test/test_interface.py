from api.modules.interface import *

import pytest
import os
import testcontainers.compose

# start the docker containers, based on tests/mocks/docker-compose.yml file
container = testcontainers.compose.DockerCompose(os.path.abspath("tests/"))
if len(container.get_containers()) != 1:
    container.start()

host = f'{container.get_service_host("database", 5432)}'
test_table = "test_table"

def test_pokemonobj():
    test_result = {
        'pokemon_id': 1, 
        'pokemon_name': 'bulbasaur', 
        'pokemon_generation': 'generation-i', 
        'pokemon_rarity': 'normal',
        'pokemon_stats': [
            {'stat_name': 'hp', 'stat_value': 45}, 
            {'stat_name': 'attack', 'stat_value': 49}, 
            {'stat_name': 'defense', 'stat_value': 49}, 
            {'stat_name': 'special-attack', 'stat_value': 65}, 
            {'stat_name': 'special-defense', 'stat_value': 65}, 
            {'stat_name': 'speed', 'stat_value': 45}], 
        'pokemon_sprite_path': ''}
    
    test_obj = PokemonObj(1, False)
    assert test_obj == test_result
    
    test_result = {
        'pokemon_id': 1, 
        'pokemon_name': 'bulbasaur', 
        'pokemon_generation': 'generation-i', 
        'pokemon_rarity': 'normal',
        'pokemon_stats': [
            {'stat_name': 'hp', 'stat_value': 45}, 
            {'stat_name': 'attack', 'stat_value': 49}, 
            {'stat_name': 'defense', 'stat_value': 49}, 
            {'stat_name': 'special-attack', 'stat_value': 65}, 
            {'stat_name': 'special-defense', 'stat_value': 65}, 
            {'stat_name': 'speed', 'stat_value': 45}], 
        'pokemon_sprite_path': '/.cache/sprite/pokemon/1.png'}
    test_obj = PokemonObj(1)
    print(test_obj)
    assert test_obj == test_result
    
    with pytest.raises(ValueError) as e_info:
        PokemonObj(-1)
    
    with pytest.raises(ValueError) as e_info:
        PokemonObj(0)
    
    
    # check getters
    assert test_obj.get_id() == 1
    assert test_obj.get_name() == 'bulbasaur'
    assert test_obj.get_generation() == 'generation-i'
    assert test_obj.get_rarity() == PokemonRarity.NORMAL
    assert test_obj.get_stats() == [
            {'stat_name': 'hp', 'stat_value': 45}, 
            {'stat_name': 'attack', 'stat_value': 49}, 
            {'stat_name': 'defense', 'stat_value': 49}, 
            {'stat_name': 'special-attack', 'stat_value': 65}, 
            {'stat_name': 'special-defense', 'stat_value': 65}, 
            {'stat_name': 'speed', 'stat_value': 45}]
    assert test_obj.get_sprite_path() == '/.cache/sprite/pokemon/1.png'


def test_generationobj():
    with pytest.raises(ValueError) as e_info:
        GenerationObj(0)
    
    with pytest.raises(ValueError) as e_info:
        GenerationObj(-2)
    
    with pytest.raises(ValueError) as e_info:
        GenerationObj(4)
    
    # list should look like this
    test_obj = GenerationObj(2)
    result_obj = {'generation_id': 2, 'pokemon_list': [{'pokemon_id': 152, 'pokemon_name': 'chikorita'}, {'pokemon_id': 155, 'pokemon_name': 'cyndaquil'}, {'pokemon_id': 158, 'pokemon_name': 'totodile'}, {'pokemon_id': 161, 'pokemon_name': 'sentret'}, {'pokemon_id': 163, 'pokemon_name': 'hoothoot'}, {'pokemon_id': 165, 'pokemon_name': 'ledyba'}, {'pokemon_id': 167, 'pokemon_name': 'spinarak'}, {'pokemon_id': 170, 'pokemon_name': 'chinchou'}, {'pokemon_id': 172, 'pokemon_name': 'pichu'}, {'pokemon_id': 173, 'pokemon_name': 'cleffa'}, {'pokemon_id': 174, 'pokemon_name': 'igglybuff'}, {'pokemon_id': 175, 'pokemon_name': 'togepi'}, {'pokemon_id': 177, 'pokemon_name': 'natu'}, {'pokemon_id': 179, 'pokemon_name': 'mareep'}, {'pokemon_id': 187, 'pokemon_name': 'hoppip'}, {'pokemon_id': 190, 'pokemon_name': 'aipom'}, {'pokemon_id': 191, 'pokemon_name': 'sunkern'}, {'pokemon_id': 193, 'pokemon_name': 'yanma'}, {'pokemon_id': 194, 'pokemon_name': 'wooper'}, {'pokemon_id': 198, 'pokemon_name': 'murkrow'}, {'pokemon_id': 200, 'pokemon_name': 'misdreavus'}, {'pokemon_id': 201, 'pokemon_name': 'unown'}, {'pokemon_id': 203, 'pokemon_name': 'girafarig'}, {'pokemon_id': 204, 'pokemon_name': 'pineco'}, {'pokemon_id': 206, 'pokemon_name': 'dunsparce'}, {'pokemon_id': 207, 'pokemon_name': 'gligar'}, {'pokemon_id': 209, 'pokemon_name': 'snubbull'}, {'pokemon_id': 211, 'pokemon_name': 'qwilfish'}, {'pokemon_id': 213, 'pokemon_name': 'shuckle'}, {'pokemon_id': 214, 'pokemon_name': 'heracross'}, {'pokemon_id': 215, 'pokemon_name': 'sneasel'}, {'pokemon_id': 216, 'pokemon_name': 'teddiursa'}, {'pokemon_id': 218, 'pokemon_name': 'slugma'}, {'pokemon_id': 220, 'pokemon_name': 'swinub'}, {'pokemon_id': 222, 'pokemon_name': 'corsola'}, {'pokemon_id': 223, 'pokemon_name': 'remoraid'}, {'pokemon_id': 225, 'pokemon_name': 'delibird'}, {'pokemon_id': 154, 'pokemon_name': 'meganium'}, {'pokemon_id': 156, 'pokemon_name': 'quilava'}, {'pokemon_id': 157, 'pokemon_name': 'typhlosion'}, {'pokemon_id': 159, 'pokemon_name': 'croconaw'}, {'pokemon_id': 160, 'pokemon_name': 'feraligatr'}, {'pokemon_id': 162, 'pokemon_name': 'furret'}, {'pokemon_id': 164, 'pokemon_name': 'noctowl'}, {'pokemon_id': 166, 'pokemon_name': 'ledian'}, {'pokemon_id': 168, 'pokemon_name': 'ariados'}, {'pokemon_id': 169, 'pokemon_name': 'crobat'}, {'pokemon_id': 171, 'pokemon_name': 'lanturn'}, {'pokemon_id': 176, 'pokemon_name': 'togetic'}, {'pokemon_id': 178, 'pokemon_name': 'xatu'}, {'pokemon_id': 180, 'pokemon_name': 'flaaffy'}, {'pokemon_id': 181, 'pokemon_name': 'ampharos'}, {'pokemon_id': 182, 'pokemon_name': 'bellossom'}, {'pokemon_id': 183, 'pokemon_name': 'marill'}, {'pokemon_id': 184, 'pokemon_name': 'azumarill'}, {'pokemon_id': 185, 'pokemon_name': 'sudowoodo'}, {'pokemon_id': 186, 'pokemon_name': 'politoed'}, {'pokemon_id': 188, 'pokemon_name': 'skiploom'}, {'pokemon_id': 189, 'pokemon_name': 'jumpluff'}, {'pokemon_id': 192, 'pokemon_name': 'sunflora'}, {'pokemon_id': 195, 'pokemon_name': 'quagsire'}, {'pokemon_id': 196, 'pokemon_name': 'espeon'}, {'pokemon_id': 197, 'pokemon_name': 'umbreon'}, {'pokemon_id': 199, 'pokemon_name': 'slowking'}, {'pokemon_id': 202, 'pokemon_name': 'wobbuffet'}, {'pokemon_id': 205, 'pokemon_name': 'forretress'}, {'pokemon_id': 208, 'pokemon_name': 'steelix'}, {'pokemon_id': 210, 'pokemon_name': 'granbull'}, {'pokemon_id': 212, 'pokemon_name': 'scizor'}, {'pokemon_id': 217, 'pokemon_name': 'ursaring'}, {'pokemon_id': 219, 'pokemon_name': 'magcargo'}, {'pokemon_id': 221, 'pokemon_name': 'piloswine'}, {'pokemon_id': 224, 'pokemon_name': 'octillery'}, {'pokemon_id': 227, 'pokemon_name': 'skarmory'}, {'pokemon_id': 228, 'pokemon_name': 'houndour'}, {'pokemon_id': 231, 'pokemon_name': 'phanpy'}, {'pokemon_id': 234, 'pokemon_name': 'stantler'}, {'pokemon_id': 235, 'pokemon_name': 'smeargle'}, {'pokemon_id': 236, 'pokemon_name': 'tyrogue'}, {'pokemon_id': 238, 'pokemon_name': 'smoochum'}, {'pokemon_id': 239, 'pokemon_name': 'elekid'}, {'pokemon_id': 240, 'pokemon_name': 'magby'}, {'pokemon_id': 241, 'pokemon_name': 'miltank'}, {'pokemon_id': 243, 'pokemon_name': 'raikou'}, {'pokemon_id': 244, 'pokemon_name': 'entei'}, {'pokemon_id': 245, 'pokemon_name': 'suicune'}, {'pokemon_id': 246, 'pokemon_name': 'larvitar'}, {'pokemon_id': 249, 'pokemon_name': 'lugia'}, {'pokemon_id': 250, 'pokemon_name': 'ho-oh'}, {'pokemon_id': 251, 'pokemon_name': 'celebi'}, {'pokemon_id': 229, 'pokemon_name': 'houndoom'}, {'pokemon_id': 230, 'pokemon_name': 'kingdra'}, {'pokemon_id': 232, 'pokemon_name': 'donphan'}, {'pokemon_id': 233, 'pokemon_name': 'porygon2'}, {'pokemon_id': 237, 'pokemon_name': 'hitmontop'}, {'pokemon_id': 242, 'pokemon_name': 'blissey'}, {'pokemon_id': 247, 'pokemon_name': 'pupitar'}, {'pokemon_id': 248, 'pokemon_name': 'tyranitar'}, {'pokemon_id': 153, 'pokemon_name': 'bayleef'}, {'pokemon_id': 226, 'pokemon_name': 'mantine'}]}
    assert test_obj == result_obj

def test_database():
    db_settings = {
        'database'        : 'test_database',
        'user'            : 'postgres',
        'host'            : host,
        'password'        : 'test_passwd',
        'port'            : 5432
    }
    
    # wrong port should not work
    with pytest.raises(ConnectionError) as e_info:
        Database(db_settings={
            'database'        : 'test_database',
            'user'            : 'postgres',
            'host'            : host,
            'password'        : 'test_passwd',
            'port'            : 1234}
            )
    
    db_obj = Database(db_settings)
    assert db_obj.delete_table() == 0
    assert db_obj.create_table() == 0
    assert db_obj.add_user("test_user", "1234ABCD", []) == 0
    assert db_obj.get_user("test_user", "1234ABCD").__str__() == {"user_id": 1, "user_name": "test_user", "deck_ids": []}.__str__()
    assert db_obj.update_user("test_user", [2, 3, 4]) == 0
    assert db_obj.delete_user("test_user") == 0
    assert db_obj.clean_table() == 0

