# -*- coding: utf-8 -*-

import collections
import keyword
import numbers
import re
import six

from sidecar.element import Element, expr

_TAGS = """
a abbr address area article aside audio b base bdi bdo big blockquote body br button
canvas caption cite code col colgroup data datalist dd del details dfn dialog div dl dt
em embed fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 head header hgroup hr
html i iframe img input ins kbd keygen label legend li link main map mark menu menuitem
meta meter nav noscript object ol optgroup option output p param picture pre progress q
rp rt ruby s samp script section select small source span strong style sub summary sup
table tbody td textarea tfoot th thead time title tr track u ul var video wbr
""".split()

_VOID_TAGS = """
area base br col embed hr img input keygen link menuitem meta param source track wbr
""".split()

_ATTRIBUTES = """
accept acceptCharset accessKey action allowFullScreen allowTransparency alt async
autoComplete autoFocus autoPlay capture cellPadding cellSpacing challenge charSet
checked classID className colSpan cols content contentEditable contextMenu controls
coords crossOrigin data dateTime default defer dir disabled download draggable encType
form formAction formEncType formMethod formNoValidate formTarget frameBorder headers
height hidden high href hrefLang htmlFor httpEquiv icon id inputMode integrity is
keyParams keyType kind label lang list loop low manifest marginHeight marginWidth max
maxLength media mediaGroup method min minLength multiple muted name noValidate nonce
open optimum pattern placeholder poster preload radioGroup readOnly rel required
reversed role rowSpan rows sandbox scope scoped scrolling seamless selected shape size
sizes span spellCheck src srcDoc srcLang srcSet start step style summary tabIndex target
title type useMap value width wmode wrap
""".split()

_STYLES = """
alignContent alignItems alignSelf animation animationDelay animationDirection
animationDuration animationFillMode animationIterationCount animationName
animationTimingFunction animationPlayState background backgroundAttachment
backgroundColor backgroundImage backgroundPosition backgroundRepeat backgroundClip
backgroundOrigin backgroundSize backfaceVisibility border borderBottom borderBottomColor
borderBottomLeftRadius borderBottomRightRadius borderBottomStyle borderBottomWidth
borderCollapse borderColor borderImage borderImageOutset borderImageRepeat
borderImageSlice borderImageSource borderImageWidth borderLeft borderLeftColor
borderLeftStyle borderLeftWidth borderRadius borderRight borderRightColor
borderRightStyle borderRightWidth borderSpacing borderStyle borderTop borderTopColor
borderTopLeftRadius borderTopRightRadius borderTopStyle borderTopWidth borderWidth
bottom boxDecorationBreak boxShadow boxSizing captionSide clear clip color columnCount
columnFill columnGap columnRule columnRuleColor columnRuleStyle columnRuleWidth columns
columnSpan columnWidth content counterIncrement counterReset cursor direction display
emptyCells filter flex flexBasis flexDirection flexFlow flexGrow flexShrink flexWrap
cssFloat font fontFamily fontSize fontStyle fontVariant fontWeight fontSizeAdjust
fontStretch hangingPunctuation height hyphens icon imageOrientation justifyContent
left letterSpacing lineHeight listStyle listStyleImage listStylePosition listStyleType
margin marginBottom marginLeft marginRight marginTop maxHeight maxWidth minHeight
minWidth navDown navIndex navLeft navRight navUp opacity order orphans outline
outlineColor outlineOffset outlineStyle outlineWidth overflow overflowX overflowY
padding paddingBottom paddingLeft paddingRight paddingTop pageBreakAfter pageBreakBefore
pageBreakInside perspective perspectiveOrigin position quotes resize right tableLayout
tabSize textAlign textAlignLast textDecoration textDecorationColor textDecorationLine
textDecorationStyle textIndent textJustify textOverflow textShadow textTransform top
transform transformOrigin transformStyle transition transitionProperty transitionDuration
transitionTimingFunction transitionDelay unicodeBidi verticalAlign visibility whiteSpace
width wordBreak wordSpacing wordWrap widows zIndex
""".split()


def _register_html_tags():
    elements = {}

    def clsdict(name):
        def __init__(self, **props):
            super(elements[name], self).__init__(name, props=props)

        def _convert_props(self, **props):
            props, props_items = {}, props.items()
            for k, v in props_items:
                # convert snakecase to camelcase for all props
                k = re.sub(r'_([a-z])', lambda s: s.group(1).upper(), k)
                # allow trailing underscore if a prop is a Python keyword
                if k and k.endswith('_') and keyword.iskeyword(k[:-1]):
                    k = k[:-1]
                if k not in _ATTRIBUTES:
                    raise RuntimeError('unknown attribute: {}'.format(k))
                # style attribute must be a dict
                if k == 'style':
                    if not isinstance(v, collections.Mapping):
                        raise RuntimeError('invalid style: {}'.format(v))
                    v, v_items = {}, v.items()
                    for sk, sv in v_items:
                        # convert snakecase (dashes allowed) to camelcase
                        sk = re.sub(r'[\-_]([a-z])', lambda s: s.group(1).upper(), sk)
                        if sk not in _STYLES:
                            raise RuntimeError('unknown style: {}'.format(sk))
                        # only allow strings, integers and expressions for styles
                        if not isinstance(sv, (six.string_types, numbers.Real, expr)):
                            raise RuntimeError('invalid style: {}={}'.format(sk, sv))
                        v[sk] = sv
                else:
                    # only allow strings or expressions for non-style attributes
                    if not isinstance(v, (six.string_types, expr)):
                        raise RuntimeError('invalid attribute: {}={}'.format(k, v))
                props[k] = v
            return props

        return {
            '__init__': __init__,
            '__doc__': '<{}> HTML tag.'.format(name),
            '_convert_props': _convert_props,
            'allow_children': name not in _VOID_TAGS
        }

    for tag in _TAGS:
        elements[tag] = type(tag, (Element,), clsdict(tag))
        # register tag in the global namespace, append underscore if it's a Python keyword
        globals()[tag + '_' * keyword.iskeyword(tag)] = elements[tag]

_register_html_tags()
