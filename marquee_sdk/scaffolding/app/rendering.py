from content import Text, Image, Embed, Container
from cgi import escape

import urlparse
import json

default_base_class_names = {
    Text.type   : 'TextBlock',
    Image.type  : 'ImageBlock',
    Embed.type  : 'EmbedBlock',
}

def renderGallery(block_list):
    html = ''

    for block in block_list:
        if block.type == Image.type:
            caption = _getCaption(block, as_html=False)

            orig_info = block.get('original', {})
            content_640 = block.get('content', {}).get('640', {})
            content_1280 = block.get('content', {}).get('1280', {})
            aspect_ratio  = orig_info.get('width', 0) / float(orig_info.get('height', 1))
            if not aspect_ratio:
                aspect_ratio = content_640.get('width',0) / float(content_640.get('height', 1))
            if not aspect_ratio:
                aspect_ratio = content_1280.get('width',0) / float(content_1280.get('height', 1))

            data = {
                    'src_640'       : content_640.get('url'),
                    'src_1280'      : content_1280.get('url'),
                    'aspect_ratio'  : aspect_ratio,
                    'caption'       : caption,
                    'id'            : block.get('id'),
                }

            html += """<div class="GalleryImage" style="background-image: url('{url}')">
                <script type="text/json">{data}</script>
            </div>""".format(
                    url     = content_640.get('url'),
                    data    = escape(json.dumps(data), quote=True),
                )

    return html

# Override base_class_name to use different selectors
def renderBlock(block, classes=None, attrs=None, base_class_name=None, for_static_markup=False):
    # because classes=[] in the sig is bad
    if not classes:
        classes = []
    if not attrs:
        attrs = {}
    if not base_class_name:
        base_class_name = default_base_class_names.get(block.type)
        if not base_class_name:
            return ''

    attrs['id'] = block.id
    classes.append(base_class_name)

    for prop, val in block.get('layout', {}).items():
        if val:
            attrs["data-{0}".format(prop)] = val

    if block.get('role'):
        attrs['data-role'] = block.role

    attrs['data-type'] = block.type

    block_template = u"<{tag} class='{classes}' {attrs}>{content}</{tag}>"

    if block.type == Image.type:
        # TODO use alt text from content object eventually
        alt = block.get("alt_text", None)
        if not alt:
            alt = _getCaption(block, as_html=False)
        if block.get('link_to'):
            content_tag = 'a'
            content_attrs = "href='{0}'".format(escape(block.get('link_to')))
        else:
            content_tag = 'div'
            content_attrs = ''

        orig_info = block.get('original', {})
        content_640 = block.get('content', {}).get('640', {})
        content_1280 = block.get('content', {}).get('1280', {})
        attrs['data-aspect_ratio']  = orig_info.get('width', 0) / float(orig_info.get('height', 1))
        if not attrs['data-aspect_ratio']:
            attrs['data-aspect_ratio'] = content_640.get('width',0) / float(content_640.get('height', 1))
        if not attrs['data-aspect_ratio']:
            attrs['data-aspect_ratio'] = content_1280.get('width',0) / float(content_1280.get('height', 1))
        attrs['data-loaded']        = 'false'
        attrs['data-src_640']       = content_640.get('url','')
        attrs['data-src_1280']      = content_1280.get('url','')

        if for_static_markup:
            actual_src = "src='{}'".format(content_640.get('url',''))
        else:
            actual_src = ''

        content = u"<{0} class='_Content' {1}>".format(content_tag, content_attrs)
        content += u"<img class='_Image' alt='{alt}' {src}>".format(
                alt = alt.replace("'",'&#x27;'),
                src = actual_src,
            )
        _caption = _getCaption(block)
        if _caption:
            content += _caption
            attrs['data-has_caption'] = 'true'
        content += u"</{0}>".format(content_tag)
    elif block.type == Text.type:
        content = _renderBlockContent(block)
    elif block.type == Embed.type:
        content = u'<div class="_Content">'
        if block.content[0:7] == '<iframe':
            content += block.content
        else:
            attrs['data-embed_url'] = block.content
        _caption = _getCaption(block)
        if _caption:
            content += _caption
            attrs['data-has_caption'] = 'true'
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
                return u"<{tag} class='_Caption'>{content}</tag>".format(
                    tag=tag, content=escape(caption['content']))
            else:
                return escape(caption['content'])
    return u''