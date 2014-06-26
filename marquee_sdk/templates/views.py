from flask              import render_template, abort, request
from flask.ext.classy   import FlaskView, route

from .utils             import loadPublication, getParam, jsonResponse

class PublicationView(FlaskView):

    def index(self):
        publication = loadPublication()
        stories = publication.stories()
        return render_template('Home.html', stories=stories)

    @route('/api/stories/')
    def stories(self):
        publication = loadPublication()
        offset  = getParam(request, '_offset', 0, int)
        limit   = getParam(request, '_limit', 20, int)
        query   = {}

        category = getParam(request, 'category', '', str)
        if category:
            query['category'] = category

        stories = publication.stories(**query).sort('-first_published_date').offset(offset).limit(limit)
        return jsonResponse([s.toJSONSafe(link_root=request.host_url[:-1]) for s in stories])

