from .module_logger import LoggerClass
from .module_pokeapi import (
    get_pokemon_by_id, 
    get_pokemon_id_from_name,
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
    get_all_users_from_db,
    authenticate_user_from_db,
    update_user_from_db,
    update_user_from_db_points,
    delete_user_from_db,
    DatabaseError
)

import random as rand

# create logger object to log system
log = LoggerClass().get_logger()


class PokemonObj(object):
    """This class represents a Pokemon
    :class: `api.interface.PokemonObj`
    
    :param poke_id: Pokemon Id, must be 1 or higher
    :type poke_id: int

    :param load_sprite: Boolean to determin if the sprite should load or not, defaults to True.
    :type load_sprite: bool, optional
    
    :raises ValueError: Pokemen Id must be an integer and at least 1
    """
    
    def __init__(self, poke_id: int, load_sprite = True):
        """constructor method

        :param poke_id: Pokemon Id, must be 1 or higher
        :type poke_id: int
        :param load_sprite: Boolean to determin if the sprite should load or not. Defaults to True., defaults to True
        :type load_sprite: bool, optional
        
        :raises ValueError: Pokemen Id must be an integer and at least 1
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
        """Loads the sprite path for the pokemon with its id
        """
        self._sprite = get_pokesprite_url_by_id(self._poke_id)

    def _load_stats(self):
        """Loads the stats for the pokemon with its id
        """
        
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
    
    @classmethod
    def from_pokemon_name(cls, pokemon_name: str, load_sprite=True):
        """Returns pokemon object from pokemon name istead of id

        :param pokemon_name: name of pokemon
        :type pokemon_name: str
        :param load_sprite: tells if pokemon sprite should be loaded or not, defaults to True
        :type load_sprite: bool, optional
        :return: a Pokemon object with this name
        :rtype: PokemonObj
        """
        pokemon_id = get_pokemon_id_from_name(pokemon_name)
        if pokemon_id == -1:
            return {"details": "Pokemon with this Name not found"}
        return cls(pokemon_id, load_sprite)
    
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

    def get_points(self):
        return self._points

    def get_sprite_path(self):
        return self._sprite

    def __dict__(self):
        return {"pokemon_id": self.get_id(), "pokemon_name": self.get_name(), "pokemon_generation": self.get_generation(), 
                "pokemon_rarity": self.get_rarity().value, "pokemon_points": self.get_points(), "pokemon_stats": self.get_stats(), "pokemon_sprite_path": self.get_sprite_path()}

    def __str__(self):
        return self.__dict__().__str__()
    
    def __eq__(self, value):
        return self.__str__() == value.__str__()

class GenerationObj(object):
    """This class represents all Pokemon in a Generation

    :param gen_id: The id of the generation. Must be 1, 2 or 3
    :type gen_id: int
    
    :raises ValueError: Generation id must be an integer and between 1 to 3
    """
    
    def __init__(self, gen_id: int):
        """constructor method

        :param gen_id: The id of the generation. Must be one 1, 2 or 3
        :type gen_id: int
    
        :raises ValueError: Generation id must be an integer and between 1 to 3
        """
        
        if gen_id < 1 or gen_id > 3:
            log.error("Only Generation 1 - 3 are supported")
            raise ValueError("Only Generation 1 - 3 are supported")
        self._gen_id = gen_id
        self._load_pokemon()
    
    def _load_pokemon(self):
        """try to load list with pokemon in this generation
        """
        
        self._pokemon_list = []
        _pokemon_list = get_pokemon_id_names_by_generation(self._gen_id)
        if len(_pokemon_list) > 0:
            self._pokemon_list = _pokemon_list
    
    def get_pokemon_list(self):
        return self._pokemon_list
    
    def get_pokemon_by_index(self, index: int):
        """Returns a pokemon object for the pokemon at the position <index> from the pokemon list of this generation.

        :param index: Index for the pokemon that should be returned. This index is NOT the pokemon id. Index must be between 0 and length of pokemon list
        :type index: int
        :raises IndexError: Index must be between 0 and length of pokemon list
        :raises IndexError: If list is empty it will also trigger IndexError
        :return: returns a pokemon object with containing all information for the pokemon that was selected from the list via index
        :rtype: PokemonObj
        """
        
        if index < 0 or index > len(self._pokemon_list):
            log.error("Index out of bounds")
            raise IndexError("Index out of bounds")
        if len(self._pokemon_list) > 0:
            pokemon_json = self._pokemon_list[index]
            return PokemonObj(pokemon_json["pokemon_id"])
        else:
            log.error("Pokemon list is empty")
            raise IndexError("Pokemon List is empty")

    def get_random_pokemon(self):
        """Returns a random pokemon out of the pokemon list of this generation

        :raises IndexError: The pokemon list for this generation is empty
        :return: Pokemon Object with a random pokemon_id
        :rtype: PokemonObj
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
    """This class represents the connection to the database and offers methods for functionallity

    :param db_settings: Dictionary containing all the information to connect to a database, defaults to None
    :type db_settings: dict | None
    
    :raises ConnectionError: Raises if connection to database failed
    """
    
    def __init__(self, db_settings = None):
        """constructor method

        :param db_settings: Dictionary containing all the information to connect to a database, if none environment variables will be used, defaults to None
        :type db_settings: dict | None
        
        :raises ConnectionError: Raises if connection to database failed
        """
        
        if db_settings is not None:
            self._conn = get_postgress_conn(db_settings)
        else:
            self._conn = get_postgress_conn(DB_SETTINGS)
        if self._conn is None:
            raise ConnectionError("Could not connect do Database")
    
    def close(self) -> int:
        """Closes the connection to the database

        :raises ConnectionError: raises if the connection is already a none type object
        :raises DatabaseError: raises if closing the connection failes
        :return: `0` if successfull, `1` if ConnectionError, `2` if DatabaseError
        :rtype: int
        """
        
        output = close_connection(self._conn)
        if output == 1:
            raise ConnectionError("Close connection function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not close connection")
        else:
            return output
    
    def create_table(self) -> int:
        """Creates a table with default name inside the db

        :raises ConnectionError: raises if the connection is a none type object
        :raises DatabaseError: raises if creating the table failes
        :return: `0` if successfull, `1` if ConnectionError, `2` if DatabaseError
        :rtype: int
        """
        
        output = create_table(self._conn)
        if output == 1:
            raise ConnectionError("Create table function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not create table")
        else:
            return output
    
    def clean_table(self) -> int:
        """Cleans a table with default name inside the db

        :raises ConnectionError: raises if the connection is a none type object
        :raises DatabaseError: raises if cleaning the table failes
        :return: `0` if successfull, `1` if ConnectionError, `2` if DatabaseError
        :rtype: int
        """

        output = clean_table(self._conn)
        if output == 1:
            raise ConnectionError("Create table function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not create table")
        else:
            return output
    
    def delete_table(self) -> int:
        """Deletes a table with default name inside the db

        :raises ConnectionError: raises if the connection is a none type object
        :raises DatabaseError: raises if deleting the table failes
        :return: `0` if successfull, `1` if ConnectionError, `2` if DatabaseError
        :rtype: int
        """
        
        output = delete_table(self._conn)
        if output == 1:
            raise ConnectionError("Delete table function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not delete table")
        else:
            return output
    
    def get_user(self, user_name: str) -> dict:
        """Returns a user in dictionary format containing his id, name, and list of pokemon_ids inside his deck called deck_id

        :param user_name: the user name of the user to get
        :type user_name: str
        :return: A dictionary containing information about the user:
                  `{"user_id": -1, "user_name": "", "deck_ids": []}` if user does not exists
                  `{"user_id": int, "user_name": str, "deck_ids": list[int]}` if user does exists
        :rtype: dict
        """
        
        return get_user_from_db(self._conn, user_name).__dict__()

    def get_users(self):
        """Returns a dictionary containing a list of all users in the table

        :return: A dictionary containing information about all the users:
                  `{"users": [{"user_id": int, "user_name": str, "deck_ids": list[int]}, ...]}` if table is not empty
                  `{"users": []}` if table is empty
                  `{}` if fetch failed
        :rtype: dict
        """
        
        return get_all_users_from_db(self._conn)

    def authenticate_user(self, user_name: str, user_password: str) -> dict:
        """Authenticates the user and if the authentication is successfully it returns the user

        :param user_name: the user name of the user to get
        :type user_name: str
        :param user_password: password of the user
        :type user_password: str
        :return: A dictionary containing information about the user:
                  `{"user_id": -1, "user_name": "", "deck_ids": []}` if user does not exists or password is wrong
                  `{"user_id": int, "user_name": str, "deck_ids": list[int]}` if user does exists and password was correct
        :rtype: dict
        """
        
        return authenticate_user_from_db(self._conn, user_name, user_password).__dict__()

    def add_user(self, user_name: str, passwd: str, pokemon_list = []) -> int:
        """Add a new user to the table

        :param user_name: The name of the user
        :type user_name: str
        :param passwd: The password of the user: Must contain at least one digit, upper and must be at least 8 character long
        :type passwd: str
        :param pokemon_list: a list of pokemon ids representing the deck of the user, defaults to []
        :type pokemon_list: list, optional
        :raises ConnectionError: raises if the connection is a none type object
        :raises DatabaseError: raises if adding the user failes
        :return: `0` if successfull, `1` if ConnectionError, `2` if DatabaseError
        :rtype: int
        """
        
        output = add_user_with_crypt_pass(self._conn, user_name, passwd, pokemon_list)
        if output == 1:
            raise ConnectionError("Add user function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not add new user")
        else:
            return output

    def add_elem_to_user_deck(self, user_name: str, new_elem):
        """Add an element to a users deck

        :param user_name: The name of the user
        :type user_name: str
        :param new_elem: the element that should be added to the user of form `{"_id": int, "_name": str}`
        :type new_elem: dict

        :return: `0` if successfull
        :rtype: int | void
        """
        user = get_user_from_db(self._conn, user_name)
        if not user.__empty__() and new_elem not in user.deck_ids:
            user.deck_ids.append(new_elem)
            print(user.deck_ids)
            return self.update_user(user_name, user.deck_ids)
        
    def update_user(self, user_name: str, pokemon_list = []) -> int:
        """Updates the deck of a user.

        :param user_name: The user thats deck should be updated
        :type user_name: str
        :param pokemon_list: The new list of pokemon ids representing the new deck, defaults to []
        :type pokemon_list: list, optional
        :raises ConnectionError: raises if the connection is a none type object
        :raises DatabaseError: raises if updating the user failes
        :return: `0` if successfull, `1` if ConnectionError, `2` if DatabaseError
        :rtype: int
        """
        
        output = update_user_from_db(self._conn, user_name, pokemon_list)
        if output == 1:
            raise ConnectionError("Update user function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not update user")
        else:
            return output

    def update_user_points(self, user_name: str, points: int) -> int:
        """Updates the points of a user.

        :param user_name: The user thats deck should be updated
        :type user_name: str
        :param points: The new points of a user, defaults to 0
        :type points: int
        :raises ConnectionError: raises if the connection is a none type object
        :raises DatabaseError: raises if updating the user failes
        :return: `0` if successfull, `1` if ConnectionError, `2` if DatabaseError
        :rtype: int
        """
        
        output = update_user_from_db_points(self._conn, user_name, points)
        if output == 1:
            raise ConnectionError("Update user function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not update user")
        else:
            return output

    def delete_user(self, user_name: str) -> int:
        """Deletes a user

        :param user_name: The user that should be deleted
        :type user_name: str
        :raises ConnectionError: raises if the connection is a none type object
        :raises DatabaseError:  raises if deleting the user failes
        :return: `0` if successfull, `1` if ConnectionError, `2` if DatabaseError
        :rtype: int
        """
        
        output = delete_user_from_db(self._conn, user_name)
        if output == 1:
            raise ConnectionError("Delete user function received none type object for connection")
        elif output == 2:
            raise DatabaseError("Unresolved error occured, could not delete user")
        else:
            return output