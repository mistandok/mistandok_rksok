from rksokprotocol import RKSOKCommand, RequestVerb, ResponseStatus
from rksokstorage import RKSOKPhoneStorage


class RKSOKStorageManager:
    def __init__(self, storage: RKSOKPhoneStorage) -> None:
        self._storage = storage
        self._methods_for_request = {
            RequestVerb.GET.value: self._response_for_get,
            RequestVerb.WRITE.value: self._response_for_write,
            RequestVerb.DELETE.value: self._response_for_delete,
        }

    async def get_response_for_request(self, request: RKSOKCommand) -> RKSOKCommand:
        method =  self._methods_for_request.get(request.command(), None)
        if method is None:
            return RKSOKCommand(ResponseStatus.INCORRECT_REQUEST.value)
       
        return await method(request)            

    async def _response_for_get(self, request: RKSOKCommand) -> RKSOKCommand:
        values_for_key = await self._storage.get_data(request.key())
        if not values_for_key:
            return RKSOKCommand(ResponseStatus.NOTFOUND.value)
        return RKSOKCommand(ResponseStatus.OK.value, value=values_for_key)

    async def _response_for_write(self, request):
        result_write_operation =  await self._storage.set_data(request.key(), request.value())
        if not result_write_operation:
            return RKSOKCommand(ResponseStatus.INCORRECT_REQUEST.value)
        return RKSOKCommand(ResponseStatus.OK.value)

    async def _response_for_delete(self, request):
        result_delete_operation =  await self._storage.delete_data(request.key())
        if not result_delete_operation:
            return RKSOKCommand(ResponseStatus.NOTFOUND.value)
        return RKSOKCommand(ResponseStatus.OK.value)


if __name__ == '__main__':
    pass