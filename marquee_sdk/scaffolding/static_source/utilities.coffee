_ = require 'underscore'


module.exports.AGENT_IS_MOBILE = /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent)


class Evented
    on: (ev_name, fn) =>
        @_callbacks ?= {}
        @_callbacks[ev_name] ?= []
        @_callbacks[ev_name].push(fn)

    trigger: (ev_name, args...) =>
        _.each @_callbacks[ev_name], (fn) => fn(args...)

module.exports.Evented = Evented


# A stripped down version of https://github.com/EtienneLem/gauges-events/
# Removed the in-markup event tracking. Added a prefix to allow for segmenting
# events with different trackers.
class GaugesEvents

    constructor: (prefix='') ->
        @_prefix = prefix
        @_iframe = @createIframe()

    createIframe: ->
        iframe = document.createElement('iframe')
        iframe.id = 'gauges-events-tracker'
        iframe.style.cssText = 'width:0;height:0;border:0'
        document.body.appendChild(iframe)
        return iframe

    track: (event) ->
        console.log params.urls.gauges_events, "tracking #{ @_prefix }:#{ event }"
        if params.urls.gauges_events
            event = encodeURIComponent(event)
            @_iframe.src = "#{ params.urls.gauges_events }?event=#{ @_prefix }:#{ event }"

module.exports.GaugesEvents = GaugesEvents


module.exports.QueryString =
    parse: (q_string) ->
        query = {}
        if q_string
            if q_string[0] is '?'
                q_string = q_string.slice(1)
            query_parts = q_string.split('&')
            for param in query_parts
                [k, v...] = param.split('=')
                if v
                    query[k] = decodeURIComponent(v.join('='))
        return query

    assemble: (query={}) ->
        query_parts = []
        for k, v of query
            query_parts.push("#{ k }=#{ encodeURIComponent(v) }") if v
        return "?#{ query_parts.join('&') }"
