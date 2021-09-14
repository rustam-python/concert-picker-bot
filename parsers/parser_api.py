import typing

import database
import getters
import logger
import schemas
from getters.getter_place_details import PlaceDetails


# noinspection PyBroadException
class ParserApi:
    def __init__(self):
        self.logger = logger.Logger(name=self.__class__.__name__)

    def start(self) -> bool:
        self.logger.info('APIs parsing is started')
        result = self._exec_scan()
        if result:
            self.logger.success('APIs parsing is completed')
        return result

    def _exec_scan(self) -> bool:
        result = False
        try:
            events: typing.Optional[typing.List[schemas.Event]] = getters.GetterEvents().get_data()
            if events:
                places_ids = list({event.place.id for event in events if event.place})
                places: typing.List[PlaceDetails] = getters.GetterPlaceDetails(places_ids).get_data()

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
                        place_id=event.place.id if event.place else None,
                        price=event.price
                    )
                    for date in event.dates:
                        database.EventDates.add(event_id=event.id, date_start=date.start, date_stop=date.end)
                result = True
        except Exception as e:
            self.logger.critical(f'Error occurred during APIs parsing: {e}', stack_info=True)
        return result

    @staticmethod
    def _check_place_is_present(event: schemas.Event, places: typing.List[PlaceDetails]) -> bool:
        is_present = False
        for place in places:
            if event.place:
                if event.place.id == place.id:
                    is_present = True
                if not event.place.id:
                    is_present = True
        return is_present
