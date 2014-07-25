from flask              import render_template, abort, request

from .main              import app

import pytz
from datetime import datetime
from random import random, randint, sample, choice

from hyperdrive2.models import StorySet, CollectionSet, Story
from hyperdrive2.channels import Channel

from app import settings

from content import Container


from pyes import *

es_conn = ES(settings.ELASTIC_SEARCH_URL)

@app.route('/')
def home_view():
    main_stories = StorySet.all()
    collections = [p['content'] for p in Channel('collection')]
    sponsored_collection = [p['content'] for p in Channel('sponsor')]
    if len(sponsored_collection) > 0:
        sponsored_collection = sponsored_collection[0]
    return render_template('Home.html',
            main_stories            = main_stories,
            collections             = collections,
            sponsored_collection    = sponsored_collection,
        )

@app.route('/search/')
def search_view():
    
    q = request.args.get('q')
    if q:
        query = MultiMatchQuery([
            "title",
            "byline",
        ], q)
        resultset = es_conn.search(
            query   = query,
            indices = "zee",
            doc_types = ["story"],
        )
        results = list(resultset)
        results = map(lambda r: StorySet.get(r.slug), results)
    else:
         results = StorySet.all()
    return render_template('Search.html',
            results = results,
            q = q
        )

@app.route('/stories/<story_slug>/')
def story_view(story_slug=None, collection_slug=None):
    story = StorySet.get(story_slug)
    if not story:
        abort(404)
    return render_template('Story.html',
            story       = story,
        )

@app.route('/collections/<collection_slug>/')
def collection_view(collection_slug=None):
    collection = CollectionSet.get(collection_slug)
    if not collection:
        abort(404)
    return render_template('Collection.html',
            collection       = collection,
        )
