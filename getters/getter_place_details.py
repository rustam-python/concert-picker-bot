import asyncio
import time
import typing

import aiohttp
import pydantic

from getters.errors import KudagoError
from getters.getter_events import _ProtoGetter


class PlaceDetails(pydantic.BaseModel):
    address: str
    id: int
    title: str


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# noinspection PyBroadException
class GetterPlaceDetails(_ProtoGetter):
    def __init__(self, places_ids: typing.List[int]):
        super().__init__()
        self.places_ids: typing.List[int] = places_ids
        self._ids_for_retry: typing.List[int] = []

    def get_data(self) -> typing.List[PlaceDetails]:
        self.logger.info('Get details for events places')
        results = self._get_places_data(self.places_ids)
        if self._ids_for_retry:
            count = 5
            while count > 0:
                results += self._get_places_data(self._ids_for_retry)
                count -= 1
        return [PlaceDetails(**result) for result in results if result is not None]

    def _get_places_data(self, places_ids: typing.List[int]):
        results = []
        chunks = [places_ids[x:x + 6] for x in range(0, len(places_ids), 6)]

        for chunk in chunks:  # We can make only 6 requests per second to KudaGo API.
            results += loop.run_until_complete(self._make_requests(places_ids=chunk))
            time.sleep(1)
        return results

    async def _make_requests(self, places_ids: typing.List[int]):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for place_id in places_ids:
                tasks.append(self._get_place_details(place_id=place_id, session=session))
            result = await asyncio.gather(*tasks)
        return result

    async def _get_place_details(self, place_id: int, session: aiohttp.ClientSession):
        result = None
        url = f'https://kudago.com/public-api/v1.4/places/{place_id}/?lang=&fields=id,title,address&location=msk'
        try:
            result = await self._send_request(url=url, session=session)
            if place_id in self._ids_for_retry:
                self._ids_for_retry.remove(place_id)
        except KudagoError:
            if place_id not in self._ids_for_retry:
                self._ids_for_retry.append(place_id)
        except Exception:
            self.logger.error(f'Failed to get KudaGo data from {url}')
            if place_id not in self._ids_for_retry:
                self._ids_for_retry.append(place_id)
        return result

    async def _send_request(self, url: str, session: aiohttp.ClientSession):
        response = await session.request(method="GET", url=url)
        if not response.status == 200:
            error = await response.json()
            self.logger.error(f'Failed to get KudaGo data from {url}: {error.get("detail")}')
            raise KudagoError
        return await response.json()
