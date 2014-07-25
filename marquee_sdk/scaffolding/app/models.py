from content        import Container
from .data_loader   import content_objects

from datetime import datetime
import pytz
LIPSUM = """Donec id elit non mi porta gravida at eget metus. Donec id elit non mi porta gravida at eget metus. Vivamus sagittis lacus vel augue laoreet rutrum faucibus dolor auctor. Nullam quis risus eget urna mollis ornare vel eu leo. Integer posuere erat a ante venenatis dapibus posuere velit aliquet. Nullam id dolor id nibh ultricies vehicula ut id elit. Duis mollis, est non commodo luctus, nisi erat porttitor ligula, eget lacinia odio sem nec elit"""
LIPSUM_WORDS = LIPSUM.replace('.','').replace(',','').lower().split(' ')
class DummyStory(object):
    byline = 'First Last'
    published_date = datetime(2014,7,21,13,12,3,tzinfo=pytz.utc)
    cover_url = None
    def __init__(self):
        self.title = u' '.join(sample(LIPSUM_WORDS, randint(1,8))).title()
        self.summary = choice(LIPSUM_WORDS).title() + u' '.join(sample(LIPSUM_WORDS, randint(10,len(LIPSUM_WORDS)))) + '.'
        self.link = "/stories/{}/".format('-'.join(self.title.lower().split(' ')))
        if random() > 0.3:
            self.cover_url = "http://sample.marquee-cdn.net/images/{}-512.jpg".format(randint(1,57))
    def cover(self, *args,**kwargs):
        return self.cover_url