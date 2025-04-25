from .module_logger import LoggerClass
from .module_pokeapi import get_pokemon_by_id, get_pokemon_id_names_by_generation, get_pokemon_rarity_by_id, get_pokesprite_url_by_id, PokemonRarity
import random as rand

# create logger object to log system
log = LoggerClass().get_logger()


class PokemonObj(object):
    
    def __init__(self, poke_id: int, load_sprite = True):

        self.poke_id = poke_id

        self._load_stats()

        if load_sprite:
            self._load_sprite_path()
        else:
            self.sprite = ""

    def _load_sprite_path(self):
        self.sprite = get_pokesprite_url_by_id(self.poke_id)

    def _load_stats(self):
        
        self.name = ""
        self.generation = 0
        self.rarity = ""
        self.points = 0
        self.stats = []
        
        pokemon = get_pokemon_by_id(self.poke_id)
        if pokemon is not None:
            self.name = pokemon["pokemon_name"]
            self.stats = pokemon["pokemon_stats"]
            self.rarity = get_pokemon_rarity_by_id(self.poke_id)
            multiplier = 1
            if self.rarity == PokemonRarity.LEGENDARY:
                multiplier = 2
            elif self.rarity == PokemonRarity.MYTHIC:
                multiplier = 5
            self.points = self.stats[0]["stat_value"] * multiplier  # hp base stat mal rarity multiplier
    
    def get_id(self):
        return self.poke_id
    
    def get_name(self):
        return self.name
    
    def get_generation(self):
        return self.generation
    
    def get_rarity(self):
        return self.rarity.value
    
    def get_stats(self):
        return self.stats

    def get_sprite_path(self):
        return self.sprite

    def __dict__(self):
        return {"pokmone_id": self.get_id(), "pokemon_name": self.get_name(), "pokemon_generation": self.get_generation(), 
                "pokemon_rarity": self.get_rarity(), "pokemon_stats": self.get_stats(), "pokemon_sprite_path": self.get_sprite_path()}

    def __str__(self):
        return f"{self.__dict__()}"

class GenerationObj(object):
    def __init__(self, gen_id: int):
        if gen_id < 1 or gen_id > 3:
            log.error("Only Generation 1 - 3 are supported")
            raise ValueError("Only Generation 1 - 3 are supported")
        self.gen_id = gen_id
        self._load_pokemon()
    
    def _load_pokemon(self):
        self.pokemon_list = []
        _pokemon_list = get_pokemon_id_names_by_generation(self.gen_id)
        if len(_pokemon_list) > 0:
            self.pokemon_list = _pokemon_list
    
    def get_pokemon_list(self):
        #_pokemon_list = [{k: v for k, v in d.items() if k != 'rarity'} for d in self.pokemon_list]
        return self.pokemon_list
    
    def get_pokemon_by_index(self, index: int):
        if index < 0 or index > len(self.pokemon_list):
            log.error("Index out of bounds")
            raise IndexError("Index out of bounds")
        if len(self.pokemon_list) > 0:
            pokemon_json = self.pokemon_list[0]
            if "rarity" in pokemon_json:
                return PokemonObj(pokemon_json["pokemon_id"], pokemon_json["rarity"])
            else:
                return PokemonObj(pokemon_json["pokemon_id"])
        else:
            log.error("Pokemon list is empty")
            raise IndexError("Pokemon List is empty")

    def get_random_pokemon(self):
        if len(self.pokemon_list) > 0:
            rand_index = rand.randint(0, len(self.pokemon_list)-1)
            poke_id = self.pokemon_list[rand_index]["pokemon_id"]
            return PokemonObj(poke_id)
        else:
            log.error("Pokemon list is empty")
            raise IndexError("Pokemon List is empty")

class Database(object):
    
    def __init__(self):
        raise NotImplementedError("Database Object has not implemented yet")