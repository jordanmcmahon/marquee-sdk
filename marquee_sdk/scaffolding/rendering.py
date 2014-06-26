from content import Text, Image, Embed, Container
from cgi import escape

import urlparse

default_base_class_names = {
    Text.type   : 'TextBlock',
    Image.type  : 'ImageBlock',
    Embed.type  : 'EmbedBlock',
}

# Override base_class_name to use different selectors
def renderBlock(block, classes=None, attrs=None, base_class_name=None):
    # because classes=[] in the sig is bad
    if not classes:
        classes = []
    if not attrs:
        attrs = {}
    if not base_class_name:
        base_class_name = default_base_class_names[block.type]

    attrs['id'] = block.id
    classes.append(base_class_name)

    for prop, val in block.get('layout', {}).items():
        if val:
            classes.append(u"-{0}--{1}".format(prop, val))

    if block.get('role'):
        classes.append(u"-role--{0}".format(block.role))

    block_template = u"<{tag} class='{classes}' {attrs}>{content}</{tag}>"

    if block.type == Image.type:
        src = _pickImageSrc(block)
        # TODO use alt text from content object eventually
        alt = block.get("alt_text", None)
        if not alt:
            alt = _getCaption(block, as_html=False)
        if alt == '' and src is not None:
            alt = urlparse.urlsplit(src).path.split('/')[-1]
        if block.get('link_to'):
            content_tag = 'a'
            content_attrs = "href='{0}'".format(escape(block.get('link_to')))
        else:
            content_tag = 'div'
            content_attrs = ''
        content = u"<{0} class='Block_Content' {1}>".format(content_tag, content_attrs)
        content += u"<img class='ImageBlock_Image' src='{0}' alt='{1}'>".format(src, alt)
        _caption = _getCaption(block)
        if _caption:
            content += _caption
            classes.append('-has_caption')
        content += u"</{0}>".format(content_tag)
    elif block.type == Text.type:
        content = _renderBlockContent(block)
    elif block.type == Embed.type:
        content = u'<div class="Block_Content">'
        if block.content[0:7] == '<iframe':
            content += block.content
        else:
            attrs['data-embed_url'] = block.content
        _caption = _getCaption(block)
        if _caption:
            content += _caption
            classes.append('-has_caption')
        content += '</div>'

    attrs = ["{0}='{1}'".format(k,v) for k, v in attrs.items()]
    markup = block_template.format(
            tag         = _pickTag(block),
            classes     = escape(u' '.join(classes)),
            attrs       = escape(u' '.join(attrs)),
            content     = content
        )
    return markup




def _pickImageSrc(block):
    if block.get('layout', {}).get('size') == 'large':
        return block.content.get('1280', {}).get('url')
    return block.content.get('640', {}).get('url')



def _pickTag(block):
    if block.type == Text.type:
        TAGS = {
            'paragraph' : 'p',
            'pre'       : 'pre',
            'quote'     : 'blockquote',
            'heading'   : 'h',
        }
        tag = TAGS.get(block.role, 'p')
        if block.role == 'heading':
            tag += str(block.get('heading_level', 1) + 1)
        return tag
    elif block.type in [Image.type, Embed.type]:
        return 'figure'
    return 'div'



def _renderBlockContent(block):
    return block.toHTML()



def _getCaption(block, as_html=True, in_figure=True):
    annotations = block.get('annotations', [])
    if annotations:
        caption = filter(lambda a: 'caption' == a['type'], annotations)
        if caption:
            caption = caption[0]
            if as_html:
                if in_figure:
                    tag = 'figcaption'
                else:
                    tag = 'div'
                return u"<{tag} class='Caption'>{content}</tag>".format(
                    tag=tag, content=escape(caption['content']))
            else:
                return escape(caption['content'])
    return u''