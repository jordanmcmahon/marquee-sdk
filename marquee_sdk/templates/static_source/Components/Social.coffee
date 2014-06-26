# This file loads the social scripts in a deferred way which avoids loading
# them on mobile, where they are not visible.

_ = require 'underscore'
$ = require 'jquery'

$window = null

SCRIPTS =
    'facebook-jssdk'        : "https://connect.facebook.net/en_US/all.js#xfbml=1&appId=#{ params.FACEBOOK_APP_ID }"
    'google-platform-js'    : 'https://apis.google.com/js/platform.js'
    'twitter-wjs'           : 'https://platform.twitter.com/widgets.js'

scripts_added = false

_addScripts = _.debounce ->
    if not scripts_added and $window.width() > 768
        $body = $('body')
        to_load = 3
        for id, src of SCRIPTS
            script_el = document.createElement('script')
            script_el.id = id
            script_el.src = src
            $body.append(script_el)
        $('[data-social_enabled="false"]').attr('data-social_enabled', true)
            
        scripts_added = true
        $window.off('resize', _addScripts)
, 100

module.exports =
    activate: ->
        $window = $(window)
        _addScripts()
        unless scripts_added
            $window.on('resize', _addScripts)