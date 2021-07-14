import typing

import database
import getters
import logger
from getters.getter_events import Event
from getters.getter_place_details import PlaceDetails


# noinspection PyBroadException
class ParserApi:
    def __init__(self):
        self.logger = logger.Logger(name=self.__class__.__name__)

    def proc(self) -> bool:
        result = False
        try:
            self.logger.info('APIs parsing is started')
            self._exec_scan()
            result = True
            self.logger.success('APIs check is completed')
        except Exception as e:
            self.logger.critical(f'Error occurred during APIs parsing: {e}', stack_info=True)
        return result

    def _exec_scan(self):
        events: typing.List[Event] = getters.GetterEvents().get()
        places_ids = list({event.place.id for event in events})
        places: typing.List[PlaceDetails] = getters.GetterPlaceDetails(places_ids).get()

        self.logger.info('Filter events')
        for event in events:
            if not self._check_place_is_present(event=event, places=places):
                events.remove(event)

        self.logger.info('Add places to DB')
        for place in places:
            database.Place.add(place_id=place.id, address=place.address, title=place.title)

        self.logger.info('Add events to DB')
        for event in events:
            database.Events.add(
                event_id=event.id,
                title=event.title,
                slug=event.slug,
                place_id=event.place.id,
                price=event.price
            )
            for date in event.dates:
                database.EventDates.add(event_id=event.id, date_start=date.start, date_stop=date.end)

    @staticmethod
    def _check_place_is_present(event: Event, places: typing.List[PlaceDetails]) -> bool:
        is_present = False
        for place in places:
            if event.place:
                if event.place.id == place.id:
                    is_present = True
                if not event.place.id:
                    is_present = True
        return is_present
