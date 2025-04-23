from .module_logger import LoggerClass
from .module_pokeapi import *

# create logger object to log system
log = LoggerClass.get_logger()


class PokemonObj(object):
    
    def __init__(self, poke_name: str, load_sprite = True):

        self.poke_name = poke_name

        self._load_stats()

        if load_sprite:
            self.spirte = self._load_sprite_path()
        else:
            self.spirte = ""

    def _load_sprite_path(self):
        self.sprite = ""

    def _load_stats(self):
        self.name = ""
        self.generation = 0
        self.stats = {}
    
    def get_name(self):
        return self.name
    
    def get_generation(self):
        return self.generation
    
    def get_stats(self):
        return self.stats

    def get_sprite_path(self):
        return self.spirte


class GenerationObj(object):
    def __init__(self, gen_id: int):
        self.gen_id = gen_id
        #self.pokemon = pokemon
        #self.pokemon_count = len(pokemon)
    
    def _load_pokemon(self):
        self.pokemon_list = []
    
    def get_pokemon(self):
        return self.pokemon_list


class Database(object):
    
    def __init__(self):
        raise NotImplementedError("Database Object has not implemented yet")