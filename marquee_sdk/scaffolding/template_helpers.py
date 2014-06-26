from cgi        import escape as cgi_escape
from content    import Text
from content.models     import instanceFromRaw
from jinja2     import evalcontextfilter, Markup

import rendering
from .models    import modelFromRole

import settings

import re
import unicodedata



def staticURL(path):
    """
    Public: helper for including static media assets in templates.

    Example
        {% raw %}
        {{ staticURL('images/file.jpg') }}
        {% endraw %}

    path - a String path to the asset, relative to the root of the static folder

    Returns the absolute URL to the asset.
    """
    return u'{0}{1}'.format(settings.STATIC_URL, path)



def mediaURL(path):
    """
    Public: helper for including user-uploaded media in templates.

    Example
        {% raw %}
        {{ mediaURL('images/file.jpg') }}
        {% endraw %}

    path - a String path to the asset, relative to the root of the media folder

    Returns the absolute URL to the asset.
    """
    return u'{0}{1}'.format(settings.MEDIA_URL, path)



def toItemSize(count, floor=1, ceiling=5):
    """
    Public: filter that converts a count of items to the appropriate size for
    [Formwork](https://github.com/droptype/formwork)'s `.item-` variants.

    count       - the int count of items
    floor       - (optional: 1) the lowest number to use (for ensuring a
                    maximum size)
    ceiling     - (optional: 5) the highest number to use (for ensuring a
                    minimum size)
    Examples
        {%- raw -%}
        {% set stories=publication.stories().limit(4) %}
        {% for story in stories %}
            <div class="item-{{ stories|toItemSize }}">
                ...
            </div>
        {% endfor %}

        {% set stories=publication.stories().limit(8) %}
        {% for story in stories %}
            <div class="item-{{ stories|toItemSize(floor=2, ceiling=4) }}">
                ...
            </div>
        {% endfor %}
        {%- endraw -%}

    Returns the str size name.
    """

    if count < floor:
        count = floor
    elif count > ceiling:
        count = ceiling

    size_map = {
        1: 'full',
        2: 'half',
        3: 'third',
        4: 'fourth',
        5: 'fifth',
    }
    return size_map.get(count, 'full')



@evalcontextfilter
def renderBlock(eval_ctx, block):
    """
    Public: a filter that renders the given block.

    block - the Block to render

    Returns the str markup for the block.
    """
    result = rendering.renderBlock(block)
    if eval_ctx.autoescape:
        result = Markup(result)
    return result



@evalcontextfilter
def contentPreview(eval_ctx, story, char_limit=400, text_only=False, escape=True):
    """
    Public: a filter that generates a content preview for a Story. Uses the
            description of the Story, if it has one, or the text content.

    story         - the Story to preview
    char_limit    - (optional:400) the int number of characters to show
    text_only     - (optional:False) a Boolean flag indicating that the result
                    should not be wrapped in spans
    escape        - (optional:True) escape HTML entities in the text_only
                    content output

    Examples

        {%- raw -%}
        {{ story|content_preview }}

        {{ story|content_preview(char_limit=200) }}

        {{ story|content_preview(text_only=True) }}
        {%- endraw -%}

    Returns a str of HTML up to `char_limit` content characters long (count
    doesn't include markup).
    """
    # Default to an empty string since this is for a template.
    content_preview = u''
    generate_preview = True

    if hasattr(story, 'description'):
        if story.description == '' or story.description is None:
            generate_preview = True
        else:
            generate_preview = False
            content_preview = story.description[:char_limit]
            if len(story.description) > char_limit:
                if text_only:
                    content_preview += u'...'
                else:
                    content_preview += '&hellip;'

    if generate_preview:
        content_preview_text_length = 0

        for block in story.content:

            # Only include Text blocks that aren't pre-formatted.
            if block and block.type == Text.type and block.role != 'pre':
                content = block.content.lstrip().rstrip()
                if content:

                    # If this iteration of content will put the total over the
                    # limit, truncate it.
                    if content_preview_text_length + len(content) > char_limit:
                        content = content[:char_limit - content_preview_text_length]

                    # Keep track of the preview length.
                    content_preview_text_length += len(content)

                    if escape:
                        # Escape after, so character count doesn't include markup.
                        content = cgi_escape(content, quote=True)

                    # Wrap the iteration's snippet in a tag that indicates the
                    # role, to allow for styling.
                    if text_only:
                        content_preview += u"{0} ".format(content)
                    else:
                        content_preview += u" <span data-role='{0}'>{1}</span>".format(block.role, content)

                    # Add an ellipsis to the content to append if over the limit.
                    if content_preview_text_length >= char_limit:
                        if text_only and not escape:
                            content_preview += u'...'
                        else:
                            content_preview += '&hellip;'

                    if content_preview_text_length >= char_limit:
                        break

    if eval_ctx.autoescape:
        content_preview = Markup(content_preview)

    return content_preview



@evalcontextfilter
def renderCover(eval_ctx, obj):
    """
    Public: a filter that renders the cover content for a given content object
    The type of cover is determined by the `cover_content` property, and the
    correct template is loaded from the `templates/includes/` folder.

    eval_ctx - the template EvaluationContext (provided automatically)
    obj      - the ContentObject that has cover content (Story, Issue, or
                 Category)

    Examples

        {% raw %}{{ story|render_cover }}{% endraw %}

    Returns a unicode HTML fragment, or empty string.
    """
    from content import Image, Embed

    cover_type = None
    context = {}
    result = u''

    if obj and hasattr(obj, 'cover_content'):
        if isinstance(obj.cover_content, list):
            cover_type = 'gallery'
            context['cover_urls'] = [{
                '1280': img.get('content', {}).get('1280', {}).get('url'),
                '640': img.get('content', {}).get('640', {}).get('url'),
            } for img in obj.cover_content]
        else:
            # Only render the cover if it actually has content set.
            if getattr(obj.cover_content, 'type', None) == Image.type and obj.cover_content.get('content'):
                cover_type = 'image'
                context['cover_urls'] = {
                    '1280': obj.cover_content.get('content').get('1280', {}).get('url'),
                    '640': obj.cover_content.get('content').get('640', {}).get('url'),
                }
            elif hasattr(obj.cover_content, 'get'):
                context['cover_urls'] = {}
                context['embed_url'] = ''
                if obj.cover_content.get('embed'):
                    context['embed_url'] = obj.cover_content['embed'].get('content', '')
                if obj.cover_content.get('image'):
                    context['cover_urls'] = {
                        '1280': obj.cover_content['image'].get('content').get('1280', {}).get('url'),
                        '640': obj.cover_content['image'].get('content').get('640', {}).get('url'),
                    }
                if len(context) > 0:
                    cover_type = 'embed'

        if cover_type:
            template = app.jinja_env.get_template('includes/cover_{0}.html'.format(cover_type))
            result = template.render(context)
    if eval_ctx.autoescape:
        result = Markup(result)
    return result



@evalcontextfilter
def asModel(eval_ctx, obj_dict):
    """
    Public: a filter that converts a dict to one of the above models.

    obj_dict - the dict to convert

    Returns the Story, Issue, or Category version
    """
    content_object = instanceFromRaw(obj_dict)
    model = modelFromRole(content_object)
    return model

def slugify(value):
    """
    Public: a filter that performs a Django-like slugification of a string

    value - the string to slugify

    Returns a string
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return Markup(re.sub('[-\s]+', '-', value))
