# All the site widgets and shit go here, then they are invoked directly using
# inline script tags in each template. This lets us package everything into a
# single, cacheable asset, while still having flexibility between pages. (It
# relies on runtime projects typically being fairly small in scope and not
# having much functional variety between pages.)

window.Marquee = {}

Marquee.Social          = require './Components/Social.coffee'
Marquee.Share           = require './Components/Share/Share.coffee'
Marquee.EmbedBlock      = require './Components/Story/EmbedBlock.coffee'
Marquee.ImageBlock      = require './Components/Story/ImageBlock.coffee'
Marquee.Cover           = require './Components/Story/Cover.coffee'
Marquee.RelatedStories  = require './Components/Story/RelatedStories.coffee'


{ GaugesEvents } = require './utilities.coffee'
Marquee.gauges_events   = new GaugesEvents()

require 'elementQuery'
setTimeout(window.elementQuery,50)

window.jQuery = window.$ = require 'jquery' if params.DEBUG