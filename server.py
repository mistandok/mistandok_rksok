import asyncio
import time

from typing import Tuple

from collections import namedtuple
from decouple import config
from rksokprotocol import RequestVerb, ResponseStatus, RKSOKCommand
from rksokstoragemanager import RKSOKStorageManager
from rksokstorage import RKSOKPhoneStorage

ENCODING = "UTF-8"
SEPARATOR = "\r\n"
ENDING = "\r\n\r\n"

SERVER_HOST = config("SERVER_HOST")
SERVER_PORT = int(config("SERVER_PORT"))

VALIDATE_SERVER_HOST = config("VALIDATE_SERVER_HOST")
VALIDATE_SERVER_PORT = int(config("VALIDATE_SERVER_PORT"))

STORAGE_TYPE = config("STORAGE_TYPE")

if STORAGE_TYPE == 'PostgreSQL':
    STORAGE_PARM = {
        'user': config("DB_USER"),
        'password': config("DB_USER_PASSWORD"),
        'database': config("DB_NAME"),
        'host': config("DB_HOST")
    }
else:
    STORAGE_PARM = {}


ServerParameters = namedtuple("ServerParameters", ["host", "port"])


class RKSOKPhoneBookServer:
    """
    Server for communication with RKSOK clients.
    He allow get data from clients, validate requests on "Server for validation" and send responses for clients.
    """

    def __init__(self, server_parameters: ServerParameters, storage: RKSOKPhoneStorage, validate_server_parameters: ServerParameters = None) -> None:
        """
        Init server parameters

        Parameters:
        server_parameters (Tuple[str, int]) - host and port for start server
        storage (RKSOKPhoneStorage) - storage for work with data
        validate_server_parameters (Tuple[str, int]=(None, None)) - host and port for "Server for validation"
        """
        self._host, self._port = server_parameters
        self._validate_server_host, self._validate_server_port = validate_server_parameters        
        self._storage_manager = RKSOKStorageManager(storage)

    async def run_server(self):
        """
        Start server without limit by time.
        """
        server = await asyncio.start_server(
            self._handle_request,
            self._host,
            self._port)

        async with server:
            await server.serve_forever()

    async def _get_all_data_from_reader(self, reader: asyncio.StreamReader) -> str:
        """
        Receives data from reader

        Parameters:
        reader (asyncio.StreamReader) - someone who sends data to the server

        Returns:
        (str) - decode message from reader
        """
        request = b""
        limit_time = 6
        start_time = time.time()
        while True:
            request += await reader.read(1024)
            if request.endswith(ENDING.encode(ENCODING)):
                break
            if time.time() - start_time >= limit_time:
                return ''
        return request.decode(ENCODING)

    async def _get_validation_response_for_request(self, request: RKSOKCommand) -> Tuple[bool, RKSOKCommand]:
        """
        This function send response to setup Server for validation.

        Parameters:
        request (RKSOKCommand) - rksok response to validation server

        Returns:
        Tuple[True, RKSOKCommand] - If everything is OK or if "Server for validation" does not setup.
        Tuple[False, RKSOKCommand] - If something is WRONG
        """
        try:
            if not all((self._validate_server_host, self._validate_server_port)):
                return True, RKSOKCommand(ResponseStatus.APPROVED.value)

            reader, writer = await asyncio.open_connection(self._validate_server_host, self._validate_server_port)
            writer.write(str(request).encode(ENCODING))
            response = await self._get_all_data_from_reader(reader)
            writer.close()
            rksok_response = RKSOKCommand.rksokcommand_from_str(response)
            if rksok_response.command() == ResponseStatus.APPROVED.value:
                return True, rksok_response
            else:
                return False, rksok_response
        except ConnectionRefusedError:
            return True, RKSOKCommand(ResponseStatus.APPROVED.value)
    
    async def _handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        This function handle requests from clients and send responses for them.

        Parameters:
        reader (asyncio.StreamReader) - someone who sends data to the server
        writer (asyncio.StreamWriter) - someone who will get response from server

        Returns:
        None
        """
        request = await self._get_all_data_from_reader(reader)    
        print(request)
        if not self._client_request_is_correct_RKSOK(request):
            response = RKSOKCommand(ResponseStatus.INCORRECT_REQUEST.value)
        else:
            valid, validation_server_response = await self._get_validation_response_for_request(RKSOKCommand(RequestVerb.CAN.value, value=request))
            
            if not valid:
                response = validation_server_response
            else:       
                response = await self._get_response_for_request(RKSOKCommand.rksokcommand_from_str(request))         
        
        await self._send_response_to_writer(writer, response)

    def _client_request_is_correct_RKSOK(self, request: str) -> bool:
        """The function checks the compliance of the request with the protocol RKSOK"""
        rksok_request = RKSOKCommand.rksokcommand_from_str(request)
        if rksok_request.command() == ResponseStatus.INCORRECT_REQUEST.value:
            return False
        return True

    async def _get_response_for_request(self, request: RKSOKCommand) -> RKSOKCommand:
        """
        This function get response from storage manager if request is correct.

        Parameters:
        request (RKSOKCommand) - request for storage

        Returns:
        (RKSOKCommand) - response from storage
        (RKSOKCommand) - incorrect_value response
        """
        return await self._storage_manager.get_response_for_request(request)
    
    async def _send_response_to_writer(self, writer: asyncio.StreamWriter, response: RKSOKCommand) -> None:
        """
        This function send response for writer.

        Parameters:
        writer (asyncio.StreamWriter) - someone who will get response from server
        response (RKSOKCommand) - response from Server

        Returns:
        None
        """
        writer.write(str(response).encode(ENCODING))
        await writer.drain()
        writer.close()


if __name__ == '__main__':
    storage = RKSOKPhoneStorage.get_cls_by_storage_type(STORAGE_TYPE)(**STORAGE_PARM)
    server = RKSOKPhoneBookServer(
        server_parameters=ServerParameters(SERVER_HOST, SERVER_PORT),
        storage=storage,
        validate_server_parameters=ServerParameters(VALIDATE_SERVER_HOST, VALIDATE_SERVER_PORT)
        )
    asyncio.run(server.run_server())