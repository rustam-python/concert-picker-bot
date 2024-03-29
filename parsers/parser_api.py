import datetime

import database as db
import getters
import logger
import schemas
import sentry
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
            events: list[schemas.Event] | None = getters.GetterEvents().get_data()
            if events:
                places_ids = list({event.place.id for event in events if event.place})
                places: list[PlaceDetails] = getters.GetterPlaceDetails(places_ids).get_data()

                self.logger.info('Filter events')
                for event in events:
                    if not self._check_place_is_present(event=event, places=places):
                        events.remove(event)

                self.logger.info('Add places to DB')
                for place in places:
                    db.Places.add(place_id=place.id, address=place.address, title=place.title)

                self.logger.info('Add events to DB')
                for event in events:
                    db.Events.add(
                        event_id=event.id,
                        title=event.title,
                        slug=event.slug,
                        place_id=event.place.id if event.place else None,
                        price=event.price
                    )
                    for date in event.dates:
                        db.EventDates.add(event_id=event.id, date_start=date.start, date_stop=date.end)
                result = True
        except Exception as e:
            sentry.capture_exception(e)
            self.logger.failure(f'Error occurred during APIs parsing: {e}', stack_info=True)
            db.Log.add(datetime.datetime.now(), f'Error occurred during APIs parsing: {e}', 'critical')
        return result

    @staticmethod
    def _check_place_is_present(event: schemas.Event, places: list[PlaceDetails]) -> bool:
        is_present = False
        for place in places:
            if event.place:
                if event.place.id == place.id:
                    is_present = True
                if not event.place.id:
                    is_present = True
        return is_present
