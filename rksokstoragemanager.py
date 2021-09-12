"""
This module allow you manage storage by RKSOKCommand and represent answer from storage to RKSOKcommand.
"""

from rksokprotocol import RKSOKCommand, RequestVerb, ResponseStatus
from rksokstorage import RKSOKPhoneStorage


class RKSOKStorageManager:
    """
    This class allow manage storages RKSOKPhoneStorage by RKSOKCommand
    """

    def __init__(self, storage: RKSOKPhoneStorage) -> None:
        """
        Init RKSOKStorageManager parameters.

        Parameters:
        storage (RKSOKPhoneStorage) - storage for data.
        """
        self._storage = storage
        self._methods_for_request = {
            RequestVerb.GET.value: self._response_for_get,
            RequestVerb.WRITE.value: self._response_for_write,
            RequestVerb.DELETE.value: self._response_for_delete,
        }

    async def get_response_for_request(self, request: RKSOKCommand) -> RKSOKCommand:
        """
        This function try make action with storage by RKSOKCommand.

        Parameters:
        request (RKSOKCommand) - RKSOKCommand for make action with storage.

        Returns:
        (RKSOKCommand) - RKSOK response, which depended from storage response.
        """
        method =  self._methods_for_request.get(request.command(), None)
        if method is None:
            return RKSOKCommand(ResponseStatus.INCORRECT_REQUEST.value)
       
        return await method(request)            

    async def _response_for_get(self, request: RKSOKCommand) -> RKSOKCommand:
        """
        This function try get data from storage and modify it to RKSOKCommand.

        Parameters:
        request (RKSOKCommand) - RKSOKCommand for make action with storage.

        Returns:
        (RKSOKCommand)
        """
        values_for_key = await self._storage.get_data(request.key())
        if not values_for_key:
            return RKSOKCommand(ResponseStatus.NOTFOUND.value)
        return RKSOKCommand(ResponseStatus.OK.value, value=values_for_key)

    async def _response_for_write(self, request):
        """
        This function try write data to storage.

        Parameters:
        request (RKSOKCommand) - RKSOKCommand for make action with storage.

        Returns:
        (RKSOKCommand)
        """
        result_write_operation =  await self._storage.set_data(request.key(), request.value())
        if not result_write_operation:
            return RKSOKCommand(ResponseStatus.INCORRECT_REQUEST.value)
        return RKSOKCommand(ResponseStatus.OK.value)

    async def _response_for_delete(self, request):
        """
        This function try delete data from storage.

        Parameters:
        request (RKSOKCommand) - RKSOKCommand for make action with storage.

        Returns:
        (RKSOKCommand)
        """
        result_delete_operation =  await self._storage.delete_data(request.key())
        if not result_delete_operation:
            return RKSOKCommand(ResponseStatus.NOTFOUND.value)
        return RKSOKCommand(ResponseStatus.OK.value)


if __name__ == '__main__':
    pass