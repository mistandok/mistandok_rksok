import asyncpg

from abc import ABC, abstractmethod
from objectserializer import ObjectSerializer


class RKSOKPhoneStorage(ABC):
    """
    This abstract class describe methods for work with data in RKSOK phone storage
    """

    @abstractmethod
    async def get_data(self, key: str) -> str:
        """
        This function allow get data from storage.

        Parameters:
        key (str) - key value for search info on storage.

        Returns:
        data (str) - return data for key in str format
        """
        pass

    @abstractmethod
    async def set_data(self, key: str, value: str) -> bool:
        """
        This function allow set data in storage.

        Parameters:
        key (str) - key value for set data.
        value (str) - value for key.

        Returns:
        True - if set was finished saccess
        False - if set was finished with error
        """
        pass

    @abstractmethod
    async def delete_data(self, key: str) -> bool:
        """
        This function allow delete data from storage.

        Parameters:
        key (str) - key value for delete info from storage.

        Returns:
        True - if delete was finished saccess
        False - if delete was finished with error or info about key wasn't found
        """
        pass

    @staticmethod
    def get_cls_by_storage_type(storage_type: str) -> object:
        """
        This function allow get specific Class by storage type.

        Parameters:
        storage_type (str) - storage type for work with data

        Returns:
        Class RKSOKPhoneStorage
        """
        return _SERIALIZER.get_serializer(storage_type)


class DictRKSOKPhoneStorage(RKSOKPhoneStorage):
    def __init__(self) -> None:
        super().__init__()
        self.storage = {}

    async def get_data(self, key: str) -> str:
        print(f'get dict data {key}')

    async def set_data(self, key: str, value: str) -> None:
        print(f'set dict data {key}, {value}')

    async def delete_data(self, key: str):
        print(f'delete dict data {key}')


class PostgreSQLRKSOKPhoneStorage(RKSOKPhoneStorage):
    """
    This class is descendant for RKSOKPhoneStorage.
    He allow work with data in PostgreSQL database.
    """

    def __init__(self, user: str, password: str, database: str, host: str) -> None:
        """
        Init parameters for storage.

        Parameters:
        user (str) - user for connection to DB
        password (str) - password for user for connection to DB
        database (str) - database name for storage data
        host (str) - host which database listen
        """
        super().__init__()
        self._user = user
        self._password = password
        self._database = database
        self._host = host

    async def _select_data_by_key(self, conn: asyncpg.Connection, key: str) -> asyncpg.Record:
        return await conn.fetchrow('SELECT * FROM userphones WHERE username = $1', key)

    async def get_data(self, key: str) -> str:
        conn = await asyncpg.connect(user=self._user, password=self._password, database=self._database, host=self._host)
        values = await self._select_data_by_key(conn, key)

        if not values:
            await conn.close()
            return None

        await conn.close()
        return dict(values).get("phones")

    async def set_data(self, key: str, value: str) -> bool:
        conn = await asyncpg.connect(user=self._user, password=self._password, database=self._database, host=self._host)
        await conn.execute("UPDATE userphones SET phones = $1 WHERE username = $2", value, key)
        await conn.execute("INSERT INTO userphones (username, phones) SELECT $1, $2 WHERE NOT EXISTS (SELECT 1 FROM userphones WHERE username = $3)", key, value, key)
        await conn.close()
        return True

    async def delete_data(self, key: str) -> bool:
        conn = await asyncpg.connect(user=self._user, password=self._password, database=self._database, host=self._host)
        values = await self._select_data_by_key(conn, key)

        if not values:
            await conn.close()
            return False

        await conn.execute("DELETE FROM userphones WHERE username = $1", key)
        await conn.close()
        return True


class RKSOKPhoneStorageSerializer(ObjectSerializer):
    """
    Class factory for RKSOKPhoneStorage
    """
    def __init__(self):
        super().__init__()


_SERIALIZER = RKSOKPhoneStorageSerializer()
_SERIALIZER.register_format('Dict', DictRKSOKPhoneStorage)
_SERIALIZER.register_format('PostgreSQL', PostgreSQLRKSOKPhoneStorage)


if __name__ == "__main__":
    pass
