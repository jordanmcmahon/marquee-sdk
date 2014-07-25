
$                   = require 'jquery'
_                   = require 'underscore'
{ AGENT_IS_MOBILE } = require '../../utilities.coffee'

# Sets the cover size to fill the remainder of the page, or the full size if
# the window width is below the threshold. If the window width is above the
# upper bound, resets to the original aspect ratio (assuming intrinsic ratio).

class Cover
    constructor: (target_selector, internal_selector, opts={}) ->
        @_threshold     = opts.threshold or 2560
        @_upper_bound   = opts.upper_bound or 1200
        @_full_height   = opts.full_height or 1
        @_target        = $(target_selector)
        @_internals     = @_target.find(internal_selector)
        @_image         = @_target.children()
        @_window        = $(window)
        @_body          = $('body')
        @_original_image_bg = @_image.css('background-image')

        @_url = @_target.data('embed_url') unless AGENT_IS_MOBILE

        if @_url
            @_renderEmbed()

        @_window.on('resize', _.debounce(@_adjustSize, 20))
        setTimeout(@_adjustSize, 1)

        @_original_width = @_image.width()
        @_original_height = @_image.height()
        @_body_remainder = @_body.height() - @_original_height

        @_setUpScrollIndicator()


    _setUpScrollIndicator: ->
        $scroll_indicator = $('<div class="Story_ScrollIndicator" title="Scroll down to read the story."></div>')
        @_image.append($scroll_indicator)
        setTimeout =>
            $scroll_indicator.attr('data-visible', true)
        , 1000
        @_window.on 'scroll', _.throttle =>
            $scroll_indicator.attr('data-visible', @_window.scrollTop() <= 0)
        , 1000
        $scroll_indicator.on 'click', =>
            $('html').animate(scrollTop: @_window.height(), 1000)

    _adjustSize: =>
        window_width = @_window.width()
        window_height = @_window.height()

        # Calculate what the sizes would have been if the image hadn't been sized before
        remainder = (@_body.height() - @_image.height())
        body_height = (@_original_height / @_original_width) * window_width + remainder

        if window_width < @_threshold
            @_setFull(window_height: window_height, window_width: window_width, body_height: body_height)
        else if body_height < window_height and window_width < @_upper_bound
            @_setFill(window_height: window_height, remainder: remainder, body_height: body_height)
        else
            @_reset()
        _.defer(@_centerInternals)
        return

    _setFull: ({ window_height, body_height }) ->
        @_hideEmbed() if @_url
        @_target.css
            'height'            : window_height * @_full_height - @_target.offset().top
            'padding-bottom'    : 0

    _setFill: ({ window_height, remainder }) ->
        @_showEmbed() if @_url
        new_height = window_height - remainder
        @_target.css
            'height'            : new_height
            'padding-bottom'    : 0

    _reset: ->
        @_showEmbed() if @_url
        padding = "#{ @_original_height / @_original_width * 100 }%"
        @_target.css
            'height': ''
            'padding-bottom': padding

    _centerInternals: =>
        outer_height = @_image.height()
        inner_height = @_internals.height()
        console.log outer_height, inner_height
        @_internals.css
            'margin-top': (outer_height - inner_height) / 2

    _showEmbed: ->
        @_frame.show()
        # Need to hide the image by setting the bg image so the title is still
        # visible on the cover.
        @_image.css('background-image': 'none')

    _hideEmbed: ->
        @_frame.hide()
        @_image.css('background-image': @_original_image_bg)

    _renderEmbed: ->
        if @_url.indexOf('vimeo.com') isnt -1
            video_id = @_url.split('/')
            video_id.pop() if video_id[video_id.length - 1] is '/'
            video_id = video_id.pop()
            # Note, some of these options may be overridden by the Vimeo
            # user's preferences (if they're Pro).
            video_url = "//player.vimeo.com/video/#{ video_id }?badge=0&amp;color=000000&amp;autoplay=1&amp;loop=1&amp;potrait=0&amp;title=0&amp;byline=0"
        else if @_url.indexOf('youtube.com') isnt -1
            video_id = @_url.split('v=').pop()
            video_id = video_id.split('&').shift()
            # Need to include the &playlist parameter for looping, but it can
            # just be the same as the video id.
            video_url = "//youtube.com/embed/#{ video_id }?autoplay=1&amp;controls=0&amp;modestbranding=1&amp;iv_load_policy=3&amp;showinfo=0&amp;autohide=1&amp;loop=1&amp;playlist=#{ video_id }"
        else
            @_url = null
            video_url = null
        if video_url
            video_frame = """<iframe src="#{ video_url }" width="150%" height="150%" style="margin-left:-25%;margin-top:-5%" frameborder="0"></iframe>"""
            @_frame = $(video_frame)
            @_target.append(@_frame)

module.exports = Cover