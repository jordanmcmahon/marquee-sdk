$ = require 'jquery'
_ = require 'underscore'

{ AGENT_IS_MOBILE, Evented } = require '../../utilities.coffee'

$window = null

TRANSITION_DURATION = 500

class Zoomer extends Evented
    constructor: (@parent) ->
        @$el = $('<div class="Zoomer"></div>')
        @$el.on('click', @hide)
        @$img = $('<img class="_Image">')
        @$el.append(@$img)
        @_is_loaded = false
        @_is_open = false
        $window.on 'resize', _.debounce =>
            @_reveal() if @_is_open
        , 50
        $window.on('scroll', @_onScroll)
        _.defer(@_onScroll)

    _onScroll: (e) =>
        if @_is_revealing
            e.preventDefault()
        if @_is_open and not @_is_revealing
            @hide()
        @_setInitialPosition()

    show: =>
        unless @_is_revealing or @_is_open
            @_is_open = true
            @_is_revealing = true
            $('body').append(@$el)
            @_setInitialPosition(false)
            unless @_is_loaded
                @$img.on 'load', =>
                    @_is_loaded = true
                    _.defer(@_reveal)
                @$img.attr(src: @parent.src_1280)
            else
                _.defer(@_reveal)
        return

    _reveal: =>
        # Do this here so it happens after the image is loaded.
        @trigger('show:pre')
        @$el.attr('data-open', true)
        w_width   = $window.width()
        w_height  = $window.height()
        if @parent.aspect_ratio > w_width / w_height
            height  = w_width / @parent.aspect_ratio
            width   = w_width
        else
            height  = w_height
            width   = w_height * @parent.aspect_ratio
        left = (w_width - width) / 2
        top  = (w_height - height) / 2
        @$img.css
            width   : width
            height  : height
            left    : left
            top     : top
        setTimeout =>
            @_is_revealing = false
            @trigger('show:post')
        , TRANSITION_DURATION

    hide: =>
        unless @_is_revealing
            @trigger('hide:pre')
            @_is_revealing = true
            @$el.attr('data-open', false)
            @_setInitialPosition()
            setTimeout =>
                @$el.detach()
                @_is_revealing = false
                @_is_open = false
                @trigger('hide:post')
            , TRANSITION_DURATION

    _setInitialPosition: (transition=true) ->
        @$img.attr('data-transition', transition)
        { left, top } = @parent.$img.offset()
        top -= $window.scrollTop()
        @$img.css
            width   : @parent.$img.width()
            height  : @parent.$img.height()
            left    : left
            top     : top
        @$img.attr('data-transition', true)


class ImageBlock
    constructor: (el) ->
        @el             = el
        @$el            = $(el)
        @$img           = @$el.find('._Image')
        @_src_is_set    = false
        @aspect_ratio   = @$el.data('aspect_ratio')
        @src_640        = @$el.data('src_640')
        @src_1280       = @$el.data('src_1280')
        @_bindEvents()
        @_checkPosition()
        _.defer(@_setSize)

    _bindEvents: ->
        $window.on('scroll', _.throttle(@_checkPosition, 50))
        $window.on('resize', _.throttle(@_setSize, 50))
        @$img.on 'load', =>
            @$el.attr('data-loaded', true)
            @_zoomer = new Zoomer(this)
            @_zoomer.on 'show:pre', =>
                @$el.attr('data-zoomed', true)
            @_zoomer.on 'hide:post', =>
                @$el.attr('data-zoomed', false)
        @$img.on('click', @_zoomImage)

    _checkPosition: (e) =>
        if $window.scrollTop() > (@$el.offset().top - 1.5 * $window.height())
            @_setSrc()
        return

    _setSize: =>
        new_width = @$img.width()
        if new_width isnt @_last_width
            @_last_width = new_width
            height = @_last_width / @aspect_ratio
            @$img.css
                height: height
            @_checkPosition()
            @$img.attr('data-zoomable', @$img.width() isnt $window.width())
        return

    _zoomImage: =>
        unless @$img.width() is $window.width()
            @_zoomer.show()

    _setSrc: ->
        is_retina = window.devicePixelRatio > 1
        @_src_is_set = true
        $window.off('scroll', @_checkPosition)
        width = @$img.width()
        if width > 640 or (width > 320 and is_retina)
            src = @src_1280
        else
            src = @src_640
        if @$el.data('effect') is 'pin' and not AGENT_IS_MOBILE
            @$img.css
                'background-image': "url(#{ src })"
                'background-attachment': 'fixed'
                'background-position': 'center center'
                'background-repeat': 'no-repeat'
                'background-size': 'cover'
            @$img.attr(alt: '')
            @$el.attr('data-loaded', true)
        else
            @$img.attr(src: src)

    @activate: ->
        $window = $(window)
        window.devicePixelRatio ?= 1
        $('.ImageBlock').each (i, el) ->
            new ImageBlock(el)

module.exports = ImageBlock
