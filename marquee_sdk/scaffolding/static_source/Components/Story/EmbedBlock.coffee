$   = require 'jquery'
URI = require 'URIjs'
_   = require 'underscore'


buildIframeEmbed = (url, attrs={}) ->
    attributes = []
    for k, v of attrs
        attributes.push("k='#{ v }'")
    attributes = attributes.join(' ')
    return "<div class='wrapper'><iframe src='#{ url }' frameborder='0' #{ attributes } webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe></div>"


class EmbedBlock
    constructor: (el) ->
        @el = el
        @$el = $(el)
        @_content_el = @$el.find('._Content')
        @_caption_el = @$el.find('._Caption')
        url = @$el.data('embed_url')
        console.log 'EmbedBlock', @_url

        if url
            @_url = URI(url)
            if not @_url.protocol()
                @_url = URI("http://#{ url }")
            if not @_url.hostname()
                @_url = null

        built_embed = false
        if @_url
            built_embed = @_buildEmbed()
            if built_embed
                @$el.addClass('-intrinsic_ratio')
            else if params.EMBEDLY_KEY
                built_embed = @_buildWithEmbedly()

        if not built_embed
            console.warn('Failed to build embed', @$el.attr('id'))

    _buildEmbed: ->
        embed_html = null

        # Strip www from hostname for checking against known hosts.
        hostname = @_url.hostname().split('.')
        if hostname[0] is 'www'
            hostname.shift()
        hostname = hostname.join('.')

        # Match against known hosts, building an iframe with the appropriate URL.
        switch hostname
            when 'youtube.com'
                embed_html = buildIframeEmbed("http://www.youtube.com/embed/#{ @_url.query(true).v }?modestbranding=1")
            when 'youtu.be'
                embed_html = buildIframeEmbed("http://www.youtube.com/embed/#{ @_url.path() }?modestbranding=1")
            when 'vimeo.com'
                embed_html = buildIframeEmbed("#{ @_url.protocol() }://player.vimeo.com/video#{ @_url.path() }")

        if embed_html
            @_renderEmbed(embed_html)
            _.defer(@_adjustCaptionPosition)
            return true

        return false

    _renderEmbed: (embed) ->
        @_content_el.prepend(embed)

    _adjustCaptionPosition: =>
            console.log 'Adjusting caption', @$el.height(), @_caption_el.height(), parseInt(@$el.css('margin-bottom'))
            @$el.css
                'margin-bottom': @_caption_el.height() + parseInt(@$el.css('margin-bottom')) + parseInt(@_caption_el.css('padding-bottom')) + parseInt(@_caption_el.css('padding-top'))
            @_caption_el.css
                position: 'relative'
                top: @$el.height()

    _buildWithEmbedly: ->
        # Fetch embed data from embedly
        $.ajax
            url: params.urls.embedly_endpoint
            data:
                key         : params.EMBEDLY_KEY
                url         : @_url.toString()
                format      : 'json'
                maxwidth    : @_content_el.width()
            success: (response) =>
                if response.html?
                    @_renderEmbed(response.html)
                    @_content_el.css('text-align', 'center')
                else if response.type is 'link'
                    @_renderEmbed(buildLinkEmbed(response))

                else
                    console.warn("No .html in response for #{ @_url }", response)
            error: =>
                console.error("Error loading embed for #{ @_url }")

        return true

    @activate: ->
        $('.EmbedBlock').each (i, el) ->
            new EmbedBlock(el)
            return

buildLinkEmbed = (data) ->
    { thumbnail_url, description, title, url } = data
    return """
        <a class="EmbeddedStory" href="#{ url }">
            <img class="_Cover" src="#{ thumbnail_url }">
            <h2 class="_Title">#{ title }</h2>
            <p class="_Summary">#{ description }</p>
        </a>
    """


module.exports = EmbedBlock