from flask_classy import FlaskView, route
from flask import session, Response, request

from feed.logger import getLogger

logging = getLogger(__name__)


class SamplePages(FlaskView):


    @route('setExampleSource/<string:name>/<int:position>', methods=["POST"])
    def setExampleSource(self, name, position):
        if session is None:
            logging.info(f'{name} requested but not present in memory')
            return Response(f'feed: {name} not found.', status=404)
        source = request.get_data(as_text=True)
        # TODO search for cookes and remove
        session.setExampleSource(source, position)
        return Response('ok', status=200)


