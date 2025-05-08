from .module_logger import LoggerClass
from .module_pokeapi import (
    get_pokemon_by_id, 
    get_pokemon_id_names_by_generation, 
    get_pokemon_rarity_and_generation_by_id, 
    get_pokesprite_url_by_id, 
    PokemonRarity
)
from .module_postgresql import (
    DB_SETTINGS,
    add_user_with_crypt_pass,
    close_connection,
    create_table,
    clean_table,
    delete_table,
    get_postgress_conn,
    get_user_from_db,
    update_user_from_db,
    delete_user_from_db,
    DatabaseError
)

import random as rand

# create logger object to log system
log = LoggerClass().get_logger()


class PokemonObj(object):
    """ 
        This class represents a Pokemon 

        Methods:
            get_id: returns pokemon id
            get_name: returns pokemon name
            get_generation: returns the generation the pokemon is from
            get_rarity: returns rarity of the pokemon
            get_stats: returns base stats of the pokemon
            get_sprite_path: returns the path to the pokemon sprite
            __dict__: returns the Pokemon Object as a dictionary
            __str__: returns a string containing the Pokemon Object as a dictionary
    """
    def __init__(self, poke_id: int, load_sprite = True):
        """ Initializes a pokemon object with the pokemon id: poke_id. Will contain information about the name, generation, rarity and base stats of a pokemon.
            Additionally it loads the pokemon sprite if wanted and gives the pokemon points to represent its values.

        Args:
            poke_id (int): Pokemon Id, must be 1 or higher
            load_sprite (bool, optional): Boolean to determin if the sprite should load or not. Defaults to True.

        Raises:
            ValueError: Pokemen Id must be an integer and at least 1
        """
        if poke_id < 1:
            log.error("Pokemon Id must be greater than 1")
            raise ValueError("Pokemon Id must be greater than 1")

        self._poke_id = poke_id

        self._load_stats()

        if load_sprite:
            self._load_sprite_path()
        else:
            self._sprite = ""

    def _load_sprite_path(self):
        self._sprite = get_pokesprite_url_by_id(self._poke_id)

    def _load_stats(self):
        
        self._name = ""
        self._generation = 0
        self._rarity = PokemonRarity.NONE
        self._points = 0
        self._stats = []
        
        pokemon = get_pokemon_by_id(self._poke_id)
        if pokemon != {}:
            self._name = pokemon["pokemon_name"]
            self._stats = pokemon["pokemon_stats"]
            
            _gen_and_rarity = get_pokemon_rarity_and_generation_by_id(self._poke_id)
            self._generation = _gen_and_rarity["pokemon_gen_name"]
            self._rarity = _gen_and_rarity["pokemon_rarity"]
            multiplier = 1
            if self._rarity == PokemonRarity.LEGENDARY:
                multiplier = 2
            elif self._rarity == PokemonRarity.MYTHIC:
                multiplier = 5
            self._points = self._stats[0]["stat_value"] * multiplier  # hp base stat times rarity multiplier
    
    def get_id(self):
        return self._poke_id
    
    def get_name(self):
        return self._name
    
    def get_generation(self):
        return self._generation
    
    def get_rarity(self):
        return self._rarity
    
    def get_stats(self):
        return self._stats

    def get_sprite_path(self):
        return self._sprite

    def __dict__(self):
        return {"pokemon_id": self.get_id(), "pokemon_name": self.get_name(), "pokemon_generation": self.get_generation(), 
                "pokemon_rarity": self.get_rarity().value, "pokemon_stats": self.get_stats(), "pokemon_sprite_path": self.get_sprite_path()}

    def __str__(self):
        return self.__dict__().__str__()
    
    def __eq__(self, value):
        return self.__str__() == value.__str__()

class GenerationObj(object):
    """ This class represents all Pokemon in a Generation

        Methods:
            get_pokemon_list: returns a list containing all pokemon in that generation. Contains only pokemon id and name
            get_pokemon_by_index (int): returns a pokemon object with the poke id of the pokemon at the given index of this generation
            get_random_pokemon: returns a random pokemon object from the pokemon list of this generation
    """
    def __init__(self, gen_id: int):
        """_summary_

        Args:
            gen_id (int): The id of the generation. Must be one 1, 2 or 3

        Raises:
            ValueError: Generation id must be an integer and between 1 to 3
        """
        if gen_id < 1 or gen_id > 3:
            log.error("Only Generation 1 - 3 are supported")
            raise ValueError("Only Generation 1 - 3 are supported")
        self._gen_id = gen_id
        self._load_pokemon()
    
    def _load_pokemon(self):
        self._pokemon_list = []
        _pokemon_list = get_pokemon_id_names_by_generation(self._gen_id)
        if len(_pokemon_list) > 0:
            self._pokemon_list = _pokemon_list
    
    def get_pokemon_list(self):
        return self._pokemon_list
    
    def get_pokemon_by_index(self, index: int):
        """Returns a pokemon object for the pokemon at the position <index> from the pokemon list of this generation.

        Args:
            index (int): Index for the pokemon that should be returned. This index is NOT the pokemon id. Index must be between 0 and length of pokemon list

        Raises:
            IndexError: Index must be between 0 and length of pokemon list
            IndexError: If list is empty it will also trigger IndexError

        Returns:
            PokemonObj: returns a pokemon object with containing all information for the pokemon that was selected from the list via index
        """
        if index < 0 or index > len(self._pokemon_list):
            log.error("Index out of bounds")
            raise IndexError("Index out of bounds")
        if len(self._pokemon_list) > 0:
            pokemon_json = self._pokemon_list[0]
            return PokemonObj(pokemon_json["pokemon_id"])
        else:
            log.error("Pokemon list is empty")
            raise IndexError("Pokemon List is empty")

    def get_random_pokemon(self):
        """Returns a random pokemon out of the pokemon list of this generation

        Raises:
            IndexError: The pokemon list for this generation is empty

        Returns:
            PokemonObj: Pokemon Object with a random pokemon_id
        """
        if len(self._pokemon_list) > 0:
            rand_index = rand.randint(0, len(self._pokemon_list)-1)
            poke_id = self._pokemon_list[rand_index]["pokemon_id"]
            return PokemonObj(poke_id)
        else:
            log.error("Pokemon list is empty")
            raise IndexError("Pokemon List is empty")

    def get_generation_id(self):
        return self._gen_id

    def __dict__(self):
        return {"generation_id": self.get_generation_id(), "pokemon_list": self.get_pokemon_list()}

    def __str__(self):
        return self.__dict__().__str__()

    def __eq__(self, value):
        return self.__str__() == value.__str__()
    
        
class Database(object):
    """This class represents the connection to the database

        Methods:
            close: closes the connection to db
            create_table: creates a new table inside the db if not exists
            clean_table: removes all entries inside the table
            delete_table: deletes the table inside the db if still exists
            get_user: returns a user from the table
            add_user: adds a user into the table
            update_user: updates the deck_ids of a user inside the table
            delete_user: deletes a user inside the table if still exists       
    """
    
    def __init__(self, db_settings = None):
        """ Creates a Database object that has all the information and functions to communicate with the database

        Args:
            db_settings (dict, optional): Dictionary containing all the information to connect to a database. Defaults to None.

        Raises:
            ConnectionError: Raises if connection to database failed
        """
        if db_settings is not None:
            self._conn = get_postgress_conn(db_settings)
        else:
            self._conn = get_postgress_conn(DB_SETTINGS)
        if self._conn is None:
            raise ConnectionError("Could not connect do Database")
    
    def close(self):
        """Closes the connection to the database

        Raises:
            ConnectionError: raises if the connection is already a none type object
            DatabaseError: raises if closing the connection failes

        Returns:
            int: returns an integer value of 0 if successfull
        """
        output = close_connection(self._conn)
        if output == 1:
            raise ConnectionError("Close connection function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not close connection")
        else:
            return output
    
    def create_table(self):
        """Creates a table with default name inside the db

        Raises:
            ConnectionError: raises if the connection is a none type object
            DatabaseError: raises if creating the table failes

        Returns:
            int: returns an integer value of 0 if successfull
        """
        output = create_table(self._conn)
        if output == 1:
            raise ConnectionError("Create table function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not create table")
        else:
            return output
    
    def clean_table(self):
        """Cleans a table with default name inside the db

        Raises:
            ConnectionError: raises if the connection is a none type object
            DatabaseError: raises if cleaning the table failes

        Returns:
            int: returns an integer value of 0 if successfull
        """
        output = clean_table(self._conn)
        if output == 1:
            raise ConnectionError("Create table function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not create table")
        else:
            return output
    
    def delete_table(self):
        """Deletes a table with default name inside the db

        Raises:
            ConnectionError: raises if the connection is a none type object
            DatabaseError: raises if deleting the table failes

        Returns:
            int: returns an integer value of 0 if successfull
        """
        output = delete_table(self._conn)
        if output == 1:
            raise ConnectionError("Delete table function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not delete table")
        else:
            return output
    
    def get_user(self, user_name: str, user_password: str):
        """Returns a user in dictionary format containing his id, name, and list of pokemon_ids inside his deck called deck_id

        Args:
            user_name (str): the user name of the user to get
            user_password (str): password of the user with username: user_name

        Returns:
            dict: A dictionary containing information about the user:
                  {} if user does not exists or password is wrong
                  {"user_id": int, "user_name": str, "deck_ids": list[int]} if user does exists and password was correct
        """
        return get_user_from_db(self._conn, user_name, user_password).__dict__()

    def add_user(self, user_name: str, passwd: str, pokemon_list = []):
        """Add a new user to the table

        Args:
            user_name (str): The name of the user
            passwd (str): The password of the user:
                          Must contain at least one digit, upper and must be at least 8 character long
            pokemon_list (list, optional): a list of pokemon ids representing the deck of the user. Defaults to [].

        Raises:
            ConnectionError: raises if the connection is a none type object
            DatabaseError: raises if adding the user failes

        Returns:
            int: returns an integer value of 0 if successfull
        """
        output = add_user_with_crypt_pass(self._conn, user_name, passwd, pokemon_list)
        if output == 1:
            raise ConnectionError("Add user function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not add new user")
        else:
            return output

    def update_user(self, user_name: str, pokemon_list = []):
        """Updates the deck of a user.

        Args:
            user_name (str): The user thats deck should be updated
            pokemon_list (list, optional): The new list of pokemon ids representing the new deck. Defaults to [].

        Raises:
            ConnectionError: raises if the connection is a none type object
            DatabaseError: raises if updating the user failes

        Returns:
            int: returns an integer value of 0 if successfull
        """
        output = update_user_from_db(self._conn, user_name, pokemon_list)
        if output == 1:
            raise ConnectionError("Update user function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not update user")
        else:
            return output

    def delete_user(self, user_name: str):
        """Deletes a user.

        Args:
            user_name (str): The user that should be deleted

        Raises:
            ConnectionError: raises if the connection is a none type object
            DatabaseError: raises if deleting the user failes

        Returns:
            int: returns an integer value of 0 if successfull
        """
        output = delete_user_from_db(self._conn, user_name)
        if output == 1:
            raise ConnectionError("Delete user function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not delete user")
        else:
            return output