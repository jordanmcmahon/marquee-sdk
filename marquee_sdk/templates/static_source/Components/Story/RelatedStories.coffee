

$ = require 'jquery'
_ = require 'underscore'


class RelatedStory
    constructor: (@_story) ->
        @$el = $('<div class="RelatedStory" data-visible="false" data-size="small"></div>')
        @el = @$el[0]

    render: (item_only=false) ->
        html = """
            <a class="StoryCard" href="/#{ @_story.week_slug }/#{ @_story.slug }/" title="#{ _.escape(@_story.description.replace(/\n/g,' ')) }">
                <div class="_Media" style="background-image: url(#{ @_story.cover_url_640 })">
                </div>
                <div class="_Title">#{ _.escape(@_story.title) }</div>
            </a>
        """
        unless item_only
            html = """
                <div class="_Content">
                    <span class="RelatedStory_Label">Related Story</span>
                    #{ html }
                </div>
            """

        @$el.html(html)
        _.defer(@_adjustTitle)
        return this

    _adjustTitle: =>
        $story_item = @$el.find('.StoryItem')
        $title = $story_item.find('._Title')
        spacing = ($story_item.height() - $title.height()) / 2
        spacing = 0 if spacing < 0
        $title.css
            'margin-top': spacing

    setPosition: (position) ->
        @$el.attr('data-position', position)

    reveal: ->
        @$el.attr('data-visible', true)

# Lay out stories first to avoid jumping, then fill out content and fade in
# Identify gaps of 1000 pixels between images
# Prefer being injected next to blocks that are 3+ lines in height, or ones that
# have dropcaps (likely beginning of a section)

class RelatedStories
    constructor: (config) ->
        @_story_ids = config.story_ids # List of story IDs
        @_threshold             = config.threshold or 0 # Percentage of story to start at
        @_top_threshold         = config.top_threshold or 400 # Percentage of story to start at
        @_link_height           = config.link_height or 400 # pixel height of space the related links need
        @_segment_offset        = config.segment_offset or 0
        @_visualize_segments    = config.visualize_segments or false

        if @_story_ids
            @$window = $(window)
            @$story_content = $('.Story_Content')
            @$content = $('.ViewContent')
            @$window.on('scroll', @_checkScrollDepth)

        if @_visualize_segments
            @$window.on('resize', _.debounce(@_visualizeSegments, 500))
            @_visualizeSegments()

    _visualizeSegments: =>
        $('.RelatedStoriesVisualizer').remove()
        @$visualizer = $('<div class="RelatedStoriesVisualizer"></div>')
        @$visualizer.css
            position            : 'absolute'
            top                 : 0
            left                : 0
            right               : 0
            bottom              : 0
            'pointer-events'    : 'none'
        @$story_content.css(position: 'relative').append(@$visualizer)
        _.each @_segment_index, (segment) =>
            $vis_box = $('<div></div>')
            $vis_box.css
                position        : 'absolute'
                left            : 20
                right           : 20
                top             : segment.blocks[0].$el.position().top + 2
                height          : segment.height - 4
                background      : 'rgba(0,255,0,0.1)'
                'border-bottom' : '2px solid orange'
                'border-top'    : '2px solid blue'
            @$visualizer.append($vis_box)


    # Wait until the user has scrolled to where threshold * window_height is visible
    _checkScrollDepth: =>
        window_height = @$window.height()
        if @$window.scrollTop() + window_height > window_height * @_threshold
            @$window.off('scroll', @_checkScrollDepth)
            @_loadStoryInfo()


    _loadStoryInfo: ->
        console.log 'RelatedStories::_loadStoryInfo', @_story_ids.length, 'stories'
        $.ajax
            type: 'GET'
            url: params.urls.search
            data:
                ids: @_story_ids
            success: (response) =>
                @_stories = _.map response.results, (story) -> new RelatedStory(story)
                setTimeout(@_layoutStories, 500) if @_stories

    _calculateHeights: ->
        content_blocks  = @$story_content.children()
        blocks_index    = []
        segment_index   = []
        current_segment = null

        _resetSegment = ->
            if @_visualize_segments
                console.log 'RESET SEGMENT'
            if current_segment?
                current_segment.id = segment_index.length
                segment_index.push(current_segment)
            current_segment =
                blocks: []
                height: 0

        need_to_clear = 0
        _.each content_blocks, (block_el, i) =>
            $block = $(block_el)
            need_to_clear = 0 if _.isNaN(need_to_clear)
            if $block.data('role') isnt 'paragraph'
                _resetSegment()
                unless $block.data('position') is 'center' or $block.data('size') is 'large'
                    # Keep the injected link away from floated blocks. 
                    need_to_clear += $block.find('.Block_Content').height() + $block.find('.Caption').height() + parseInt($block.find('.Block_Content').css('margin-bottom'))
                    current_segment.cleared_on = $block.data('position')
                else
                    # Still keep the injected link away from centered or large
                    # objects.
                    need_to_clear += @_link_height
            else if $block.data('role') is 'paragraph'
                # If there is not a segment, the block has dropcaps, or the
                # block doesn't have any alphanumeric characters (ie it looks
                # something like '* * *'), or the block has centered text,
                # then reset the segment.
                if not current_segment? or $block.data('effect') is 'dropcaps' or $block.text().search(/\w/) is -1 or $block.data('align') is 'center'
                    _resetSegment()
                block_height = $block.height() + parseInt($block.css('margin-bottom'))
                if need_to_clear > 0 or $block.data('align') is 'center'
                    need_to_clear -= block_height
                else
                    block_index =
                        $el     : $block
                        height  : block_height
                    current_segment.blocks.push(block_index)
                    current_segment.height += block_height
            if @_visualize_segments
                console.log $block.data('type'), need_to_clear, $block.find('.Block_Content')?.height()
                console.log block_el
            if i is content_blocks.length - 1
                _resetSegment()

        return segment_index

    _insertStory: (story, segment) ->
        if segment.cleared_on is 'right'
            story.setPosition('left')
        else
            story.setPosition('right')
        block_i = 0
        # If the segment had to clear a block or is at the beginning, do a
        # look-ahead to see if there is room for the related story link
        # farther down. This ensures there will be a pleasing amount of space
        # between the link and the cleared block.
        if segment.blocks.length > 2 and segment.blocks[0].height < @_link_height and segment.height - (segment.blocks[0].height + segment.blocks[1]?.height) > @_link_height
            block_i = 2
        else if segment.cleared_on and segment.height - segment.blocks[0].height > @_link_height or segment.id is 0
            block_i = 1

        # Inject the story link.
        segment.blocks[block_i].$el.before(story.render().el)
        

    _layoutStories: =>
        segment_index = @_calculateHeights()
        @_segment_index = _.filter segment_index, (s) =>
            # console.log 's.blocks', s.blocks[0]?.$el.position().top, s.blocks[0]?.$el[0], s.blocks[0]?.$el.offset().top
            return s.height >= @_link_height and (s.blocks[0].$el.position().top > @_top_threshold or s.height >= @_link_height / 2 + @_top_threshold)

        # TODO: if segment index has more than there are related stories, remove the smallest of the _.rest

        interval = Math.floor(@_segment_index.length / @_stories.length)
        if interval < 1
            interval = 1
        remaining_stories = []
        _.each @_stories, (story, i) =>
            segment = @_segment_index[i * interval + @_segment_offset]
            if segment
                @_insertStory(story, segment)
            else
                remaining_stories.push(story)

        @_visualizeSegments() if @_visualize_segments
        if remaining_stories.length > 0
            @_addStoriesToEnd(remaining_stories)

    _addStoriesToEnd: (stories) ->
        label_text = if stories.length is 1 then 'Related Story' else 'Related Stories'
        $remaining_stories = $("""
                <div class="AdditionalRelated">
                    <span class="_Label">#{ label_text }</span>
                    <div class="_Items"></div>
                </div>
            """)
        $story_list = $remaining_stories.find('._Items')
        if stories.length % 2 is 0
            $story_list.addClass('-num_items--even')
        else
            $story_list.addClass('-num_items--odd')
        _.each stories, (story) =>
            $story_list.append(story.render(true).el)
        @$story_content.after($remaining_stories)



module.exports = RelatedStories