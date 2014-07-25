
$ = require 'jquery'
_ = require 'underscore'

{ GaugesEvents, AGENT_IS_MOBILE } = require '../../utilities.coffee'

SERVICE_PROPER_NAMES =
    facebook    : 'Facebook'
    twitter     : 'Twitter'
    googleplus  : 'Google+'
    pinterest   : 'Pinterest'
    appdotnet   : 'App.net'


class Share
    constructor: (services...) ->
        unless AGENT_IS_MOBILE
            @_events_tracker = new GaugesEvents('Share')
            @_story = params.story
            @$el = $('<div class="Share"></div>')
            @_addServices(services)

            @$window = $(window)
            @$upper = $('.Story_CoverImage')
            @$lower = $('.CollectionItems')

            @$window.on('scroll', @_adjustVisibility)
            @_adjustVisibility()

            $('body').append(@$el)


    _addServices: (services) ->
        _.each services, (service_name) =>
            share_link = @_buildShareLink(service_name)
            if share_link
                $share_link = $("<a target='_blank' class='Share_Trigger -#{ service_name }' href='#{ share_link }' data-service_name='#{ service_name }' title='Share to #{ SERVICE_PROPER_NAMES[service_name] }'></a>")
                $share_link.on 'click', (e) =>
                    @_openShareBox(e, share_link)
                @$el.append($share_link)

    _buildShareLink: (service) ->
        { title, summary, link, cover } = @_story
        link = window.location.origin + window.location.pathname
        switch service
            when 'facebook'
                share_link = "http://www.facebook.com/sharer/sharer.php?s=100&p[url]=#{link}&p[images][0]=#{cover}&p[title]=#{title}&p[summary]=#{summary}"
            when 'twitter'
                share_link = "http://twitter.com/home?status=#{title}%20%E2%80%93%20#{link}"
            when 'googleplus'
                share_link = "https://plus.google.com/share?url=#{link}"
            when 'pinterest'
                share_link = "http://www.pinterest.com/pin/create/button/?url=#{link}&media=#{cover}&description=#{title}"
            when 'appdotnet'
                share_link = "https://alpha.app.net/intent/post/?text=#{title}&url=#{link}"
            else
                share_link = null
        return share_link

    _openShareBox: (e, share_link) =>
        @_events_tracker.track("#{ $(e.currentTarget).data('service_name') }=#{ params.story.link }")
        e.preventDefault()
        options =
            scrollbars  : 'yes'
            resizable   : 'yes'
            toolbar     : 'no'
            location    : 'yes'
            width       : 550
            height      : 420
        window_options = []
        for k,v of options
            window_options.push("#{ k }=#{ v }")
        window_options = window_options.join(',')
        window.open(share_link, 'intent', window_options)

    _adjustVisibility: =>
        window_top = @$window.scrollTop()
        window_bottom = window_top + @$window.height()
        @$el.attr('data-visible', window_top > @$upper.offset().top + @$upper.height())
        lower_top = @$lower.offset()?.top
        if lower_top and window_bottom > lower_top
            @$el.attr('data-fixed', false)
            @$el.css
                position: 'absolute'
                top: @$el.offset().top
        else
            @$el.attr('data-fixed', true)
            @$el.css
                position: ''
                top: ''

module.exports = Share