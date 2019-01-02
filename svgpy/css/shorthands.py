# Copyright (C) 2018 Tetsuya Miura <miute.dev@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re
from abc import abstractmethod
from collections import OrderedDict

import tinycss2
from tinycss2.ast import IdentToken, NumberToken

from .props import css_color_keyword_set, css_property_descriptor_map, \
    css_wide_keyword_set

_RE_CSS_VERSION = re.compile(r'-css[0-9]$')


class Shorthand(object):

    def __init__(self, declarations):
        self._declarations = declarations  # {property: (value, priority)}

    def _shorthand(self, property_name):
        shorthand = _shorthand_property_class_map[property_name]
        return shorthand(self._declarations)

    def get_property_priority(self, property_name):
        declarations = self._declarations
        priorities = list()
        for longhand_name in Shorthand.longhands(property_name):
            if Shorthand.is_shorthand(longhand_name):
                priority = self.get_property_priority(longhand_name)
            else:
                if longhand_name not in declarations:
                    continue
                _, priority = declarations[longhand_name]
            priorities.append(priority)

        if (len(priorities) == 0
                or (len(priorities) > 1
                    and not all(priorities[0] == x for x in priorities[1:]))):
            return ''
        return priorities[0]

    def get_property_value(self, property_name):
        declarations = self._declarations
        property_map = OrderedDict()
        priorities = list()
        for longhand_name in Shorthand.longhands(property_name):
            if Shorthand.is_shorthand(longhand_name):
                value = self.get_property_value(longhand_name)
                priority = self.get_property_priority(longhand_name)
            else:
                desc = css_property_descriptor_map[longhand_name]
                if longhand_name not in declarations:
                    continue
                value, priority = declarations[longhand_name]
                if len(value) == 0 or not desc.supports(value):
                    return ''
            property_map[longhand_name] = value
            priorities.append(priority)

        if (len(priorities) == 0
                or (len(priorities) > 1
                    and not all(priorities[0] == x for x in priorities[1:]))):
            return ''

        shorthand = self._shorthand(property_name)
        value = shorthand.tostring(property_map)
        return value

    @staticmethod
    def is_shorthand(property_name):
        if property_name.startswith('--'):
            return False
        property_name = property_name.lower()
        return property_name in shorthand_property_map

    @staticmethod
    def longhands(property_name, remove_version=True):
        property_name = property_name.lower()
        longhand_names = shorthand_property_map.get(property_name, ())
        if not remove_version or len(longhand_names) == 0:
            return longhand_names
        return tuple(_RE_CSS_VERSION.sub('', x) for x in longhand_names)

    def remove_property(self, property_name):
        declarations = self._declarations
        removed = False
        for longhand_name in Shorthand.longhands(property_name):
            if Shorthand.is_shorthand(longhand_name):
                if self.remove_property(longhand_name):
                    removed = True
            else:
                if longhand_name not in declarations:
                    continue
                del declarations[longhand_name]
                removed = True

        return removed

    def set_css_declaration(self, property_name, components, priority):
        property_name = property_name.lower()
        if property_name not in shorthand_property_map:
            return False

        shorthand = self._shorthand(property_name)
        updated = shorthand.set_css_declaration(components, priority)
        return updated


class ShorthandProperty(object):

    def __init__(self, declarations):
        self._declarations = declarations

    @staticmethod
    def _parse_css_declaration(property_name, components,
                               set_initial_value=True):
        components = components.copy()
        components_map = OrderedDict()
        target_components = None
        previous_component = None
        css_wide_keywords = list()
        longhand_names = shorthand_property_map[property_name]
        for longhand_name in longhand_names:
            desc = css_property_descriptor_map[longhand_name]
            for component in list(components):
                if (component.type == 'whitespace'
                        or (component == ','
                            and ('#' in desc.syntax
                                 or ',' in desc.syntax))):
                    if target_components:
                        target_components.append(component)
                        components.remove(component)
                    continue
                if (property_name == 'font'
                        and previous_component is not None
                        and previous_component == '/'):
                    line_height = css_property_descriptor_map['line-height']
                    supported, _ = line_height.support(component)
                    if supported:
                        components_map['line-height'] = list([component])
                    target_components = None
                    components.remove(previous_component)
                    components.remove(component)
                elif (component.type == 'ident'
                      and component.lower_value in css_wide_keyword_set):
                    components.remove(component)
                    css_wide_keywords.append(component.lower_value)
                else:
                    supported, _ = desc.support(component)
                    if supported:
                        components.remove(component)
                        target = components_map.setdefault(
                            longhand_name,
                            list())
                        if (component.type == 'ident'
                                and component.lower_value
                                in css_color_keyword_set
                                | css_wide_keyword_set):
                            component = IdentToken(component.source_line,
                                                   component.source_column,
                                                   component.lower_value)
                        target.append(component)
                        target_components = target
                    else:
                        target_components = None
                previous_component = component

        if len(css_wide_keywords) > 1:
            components_map.clear()
        elif len(css_wide_keywords) == 1:
            for longhand_name in longhand_names:
                components_map[longhand_name] = [
                    IdentToken(0, 0, css_wide_keywords[0])
                ]
        elif set_initial_value:
            for longhand_name in longhand_names:
                if longhand_name not in components_map:
                    desc = css_property_descriptor_map[longhand_name]
                    initial_value = desc.initial_value
                    if initial_value.isdecimal():
                        component = NumberToken(0,
                                                0,
                                                float(initial_value),
                                                True,
                                                initial_value)
                    else:
                        component = IdentToken(0, 0, initial_value)
                    components_map[longhand_name] = [component]

        return components_map

    def _set_css_declarations(self, components_map, priority):
        declarations = self._declarations
        updated = False
        for property_name, components in components_map.items():
            needs_update = False
            value = tinycss2.serialize(components).strip()
            if property_name not in declarations:
                needs_update = True
            else:
                target_value, target_priority = declarations[property_name]
                if target_value != value or target_priority != priority:
                    needs_update = True
            if needs_update:
                updated = True
                declarations[property_name] = value, priority

        return updated

    @abstractmethod
    def set_css_declaration(self, components, priority):
        raise NotImplementedError

    @abstractmethod
    def tostring(self, property_map):
        raise NotImplementedError


class FontShorthand(ShorthandProperty):

    def set_css_declaration(self, components, priority):
        components_map = ShorthandProperty._parse_css_declaration(
            'font',
            components
        )

        font_variant_components = components_map.pop('font-variant-css2')
        shorthand = FontVariantShorthand(self._declarations)
        shorthand.set_css_declaration(font_variant_components, priority)

        font_stretch_components = components_map.pop('font-stretch-css3')
        components_map['font-stretch'] = font_stretch_components

        # desc = css_property_set['font-size-adjust']
        # components_map['font-size-adjust'] = [
        #     IdentToken(0, 0, desc.initial_value)
        # ]

        # desc = css_property_set['font-kerning']
        # components_map['font-kerning'] = [
        #     IdentToken(0, 0, desc.initial_value)
        # ]

        # desc = css_property_set['font-feature-settings']
        # components_map['font-feature-settings'] = [
        #     IdentToken(0, 0, desc.initial_value)
        # ]

        # desc = css_property_set['font-language-override']
        # components_map['font-language-override'] = [
        #     IdentToken(0, 0, desc.initial_value)
        # ]

        # desc = css_property_set['font-min-size']
        # components_map['font-min-size'] = [
        #     NumberToken(0,
        #                 0,
        #                 int(desc.initial_value),
        #                 True,
        #                 desc.initial_value)
        # ]

        # desc = css_property_set['font-max-size']
        # components_map['font-max-size'] = [
        #     IdentToken(0, 0, desc.initial_value)
        # ]

        # desc = css_property_set['font-optical-sizing']
        # components_map['font-optical-sizing'] = [
        #     IdentToken(0, 0, desc.initial_value)
        # ]

        # desc = css_property_set['font-variation-settings']
        # components_map['font-variation-settings'] = [
        #     IdentToken(0, 0, desc.initial_value)
        # ]

        # desc = css_property_set['font-palette']
        # components_map['font-palette'] = [
        #     IdentToken(0, 0, desc.initial_value)
        # ]

        updated = self._set_css_declarations(components_map, priority)
        return updated

    def tostring(self, property_map):
        _ = self
        font_style = property_map.get('font-style')
        font_variant = property_map.get('font-variant')
        font_weight = property_map.get('font-weight')
        font_stretch = property_map.get('font-stretch')
        font_size = property_map.get('font-size')
        line_height = property_map.get('line-height')
        font_family = property_map.get('font-family')
        values = (font_style,
                  font_variant,
                  font_weight,
                  font_stretch,
                  font_size,
                  line_height,
                  font_family)
        if any(x is None or len(x) == 0 for x in values):
            return ''
        elif any(x in css_wide_keyword_set for x in values):
            if all(x == font_style for x in values):
                return font_style
            else:
                return ''

        desc = css_property_descriptor_map['font-variant-css2']
        if not desc.supports(font_variant):
            return ''

        desc = css_property_descriptor_map['font-stretch-css3']
        if not desc.supports(font_stretch):
            return ''

        if line_height != 'normal':
            property_map = property_map.copy()
            property_map['font-size'] = '{}/{}'.format(font_size, line_height)
            del property_map['line-height']

        values = list()
        for property_name, value in property_map.items():
            desc = css_property_descriptor_map[property_name]
            if property_name == 'font-family' or value != desc.initial_value:
                values.append(value)

        s = ' '.join(values)
        return s


class FontSynthesisShorthand(ShorthandProperty):

    def set_css_declaration(self, components, priority):
        components_map = OrderedDict()
        values = [tinycss2.serialize([x]) for x in components
                  if x.type != 'whitespace']
        font_synthesis_weight = None
        font_synthesis_style = None
        if len(values) == 1:
            if values[0] == 'none':
                font_synthesis_weight = 'none'
                font_synthesis_style = 'none'
            elif values[0] == 'weight':
                font_synthesis_weight = 'auto'
                font_synthesis_style = 'none'
            elif values[0] == 'style':
                font_synthesis_weight = 'none'
                font_synthesis_style = 'auto'
            elif values[0] in css_wide_keyword_set:
                font_synthesis_weight = values[0]
                font_synthesis_style = values[0]
        elif len(values) == 2 and 'weight' in values and 'style' in values:
            font_synthesis_weight = 'auto'
            font_synthesis_style = 'auto'

        if font_synthesis_weight:
            components_map['font-synthesis-weight'] = [
                IdentToken(0, 0, font_synthesis_weight)
            ]
        if font_synthesis_style:
            components_map['font-synthesis-style'] = [
                IdentToken(0, 0, font_synthesis_style)
            ]

        updated = self._set_css_declarations(components_map, priority)
        return updated

    def tostring(self, property_map):
        _ = self
        font_synthesis_weight = property_map.get('font-synthesis-weight')
        font_synthesis_style = property_map.get('font-synthesis-style')
        if font_synthesis_weight is None or font_synthesis_style is None:
            return ''
        elif (font_synthesis_weight == 'none'
              and font_synthesis_style == 'none'):
            return 'none'
        elif (font_synthesis_weight == 'auto'
              and font_synthesis_style == 'none'):
            return 'weight'
        elif (font_synthesis_weight == 'none'
              and font_synthesis_style == 'auto'):
            return 'style'
        elif (font_synthesis_weight == 'auto'
              and font_synthesis_style == 'auto'):
            return 'weight style'
        elif (font_synthesis_weight == font_synthesis_style
              and font_synthesis_weight in css_wide_keyword_set):
            return font_synthesis_weight
        return ''


class FontVariantShorthand(ShorthandProperty):

    def set_css_declaration(self, components, priority):
        value = tinycss2.serialize(components).strip()
        if value in ('normal', 'none'):
            components_map = OrderedDict()
            for longhand_name in shorthand_property_map['font-variant']:
                if (longhand_name == 'font-variant-ligatures'
                        and value == 'none'):
                    initial_value = 'none'
                else:
                    desc = css_property_descriptor_map[longhand_name]
                    initial_value = desc.initial_value
                components_map[longhand_name] = [
                    IdentToken(0, 0, initial_value)
                ]
        else:
            components_map = ShorthandProperty._parse_css_declaration(
                'font-variant',
                components
            )

        updated = self._set_css_declarations(components_map, priority)
        return updated

    def tostring(self, property_map):
        _ = self
        font_variant_ligatures = property_map.get('font-variant-ligatures')
        font_variant_caps = property_map.get('font-variant-caps')
        font_variant_alternates = property_map.get('font-variant-alternates')
        font_variant_numeric = property_map.get('font-variant-numeric')
        font_variant_east_asian = property_map.get('font-variant-east-asian')
        font_variant_position = property_map.get('font-variant-position')
        values = (font_variant_ligatures, font_variant_caps,
                  font_variant_alternates, font_variant_numeric,
                  font_variant_east_asian, font_variant_position)
        if any(x is None for x in values):
            return ''
        elif all(x == 'normal' for x in values):
            return 'normal'
        elif font_variant_ligatures == 'none':
            if all(x == 'normal' for x in (font_variant_caps,
                                           font_variant_alternates,
                                           font_variant_numeric,
                                           font_variant_east_asian,
                                           font_variant_position)):
                return 'none'
            else:
                return ''
        elif any(x in css_wide_keyword_set for x in values):
            if all(x == font_variant_ligatures for x in values):
                return font_variant_ligatures
            else:
                return ''

        s = ' '.join(x for x in values if x != 'normal')
        return s


class OverflowShorthand(ShorthandProperty):

    def set_css_declaration(self, components, priority):
        components_map = ShorthandProperty._parse_css_declaration(
            'overflow',
            components,
            set_initial_value=False
        )

        if ('overflow-x' in components_map
                and 'overflow-y' not in components_map):
            temp = [x for x in components_map['overflow-x']
                    if x.type != 'whitespace']
            components_map['overflow-x'] = [temp[0]]
            components_map['overflow-y'] = [temp[0] if len(temp) == 1
                                            else temp[1]]

        updated = self._set_css_declarations(components_map, priority)
        return updated

    def tostring(self, property_map):
        _ = self
        overflow_x = property_map.get('overflow-x')
        if overflow_x is None:
            return ''

        overflow_y = property_map.get('overflow-y')
        if overflow_y is None:
            return ''
        elif overflow_x == overflow_y:
            return overflow_x
        elif (overflow_x in css_wide_keyword_set
              or overflow_y in css_wide_keyword_set):
            return ''

        s = ' '.join([overflow_x, overflow_y])
        return s


class TextDecorationShorthand(ShorthandProperty):

    def set_css_declaration(self, components, priority):
        components_map = ShorthandProperty._parse_css_declaration(
            'text-decoration',
            components,
            set_initial_value=False,
        )

        for property_name in shorthand_property_map['text-decoration']:
            if property_name not in components_map:
                components_map[property_name] = [IdentToken(0, 0, 'initial')]

        updated = self._set_css_declarations(components_map, priority)
        return updated

    def tostring(self, property_map):
        _ = self
        text_decoration_line = property_map.get('text-decoration-line')
        if text_decoration_line is None:
            return ''

        text_decoration_style = property_map.get('text-decoration-style')
        if text_decoration_style is None:
            return ''

        text_decoration_color = property_map.get('text-decoration-color')
        if text_decoration_color is None:
            return ''

        values = (text_decoration_line, text_decoration_style,
                  text_decoration_color)
        if all(x in css_wide_keyword_set for x in values):
            if (text_decoration_line == text_decoration_style
                    == text_decoration_color):
                return text_decoration_line
            else:
                return ''
        elif any(x in css_wide_keyword_set - {'initial'} for x in values):
            return ''

        s = ' '.join(x for x in values if x != 'initial')
        return s


class WhiteSpaceShorthand(ShorthandProperty):

    def set_css_declaration(self, components, priority):
        components_map = OrderedDict()
        values = [tinycss2.serialize([x]) for x in components
                  if x.type != 'whitespace']
        if len(values) != 1:
            return False
        elif values[0] == 'normal':
            text_space_collapse = 'collapse'
            text_wrap = 'wrap'
            text_space_trim = 'none'
        elif values[0] == 'pre':
            text_space_collapse = 'preserve'
            text_wrap = 'nowrap'
            text_space_trim = 'none'
        elif values[0] == 'nowrap':
            text_space_collapse = 'collapse'
            text_wrap = 'nowrap'
            text_space_trim = 'none'
        elif values[0] == 'pre-wrap':
            text_space_collapse = 'preserve'
            text_wrap = 'wrap'
            text_space_trim = 'none'
        elif values[0] == 'pre-line':
            text_space_collapse = 'preserve-breaks'
            text_wrap = 'wrap'
            text_space_trim = 'none'
        elif values[0] in css_wide_keyword_set:
            text_space_collapse = values[0]
            text_wrap = values[0]
            text_space_trim = values[0]
        else:
            return False

        components_map['text-space-collapse'] = [
            IdentToken(0, 0, text_space_collapse)
        ]
        components_map['text-wrap'] = [
            IdentToken(0, 0, text_wrap)
        ]
        components_map['text-space-trim'] = [
            IdentToken(0, 0, text_space_trim)
        ]

        updated = self._set_css_declarations(components_map, priority)
        return updated

    def tostring(self, property_map):
        _ = self
        text_space_collapse = property_map.get('text-space-collapse')
        text_wrap = property_map.get('text-wrap')
        text_space_trim = property_map.get('text-space-trim')
        values = text_space_collapse, text_wrap, text_space_trim
        if all(x is None for x in values):
            return ''
        elif (text_space_collapse == 'collapse'
              and text_wrap == 'wrap'
              and text_space_trim == 'none'):
            return 'normal'
        elif (text_space_collapse == 'preserve'
              and text_wrap == 'nowrap'
              and text_space_trim == 'none'):
            return 'pre'
        elif (text_space_collapse == 'collapse'
              and text_wrap == 'nowrap'
              and text_space_trim == 'none'):
            return 'nowrap'
        elif (text_space_collapse == 'preserve'
              and text_wrap == 'wrap'
              and text_space_trim == 'none'):
            return 'pre-wrap'
        elif (text_space_collapse == 'preserve-breaks'
              and text_wrap == 'wrap'
              and text_space_trim == 'none'):
            return 'pre-line'
        elif (any(x in css_wide_keyword_set for x in values)
              and all(x == text_space_collapse for x in values)):
            return text_space_collapse
        return ''


_shorthand_property_class_map = {
    'font': FontShorthand,
    'font-synthesis': FontSynthesisShorthand,
    'font-variant': FontVariantShorthand,
    'overflow': OverflowShorthand,
    'text-decoration': TextDecorationShorthand,
    'white-space': WhiteSpaceShorthand,
}

shorthand_property_map = {
    'font': (
        'font-style',
        'font-variant-css2',
        'font-weight',
        'font-stretch-css3',
        'font-size',
        'line-height',
        'font-family',
    ),
    'font-synthesis': (
        'font-synthesis-weight',
        'font-synthesis-style',
    ),
    'font-variant': (
        'font-variant-ligatures',
        'font-variant-caps',
        'font-variant-alternates',
        'font-variant-numeric',
        'font-variant-east-asian',
        'font-variant-position',
    ),
    'overflow': (
        'overflow-x',
        'overflow-y',
    ),
    'text-decoration': (
        'text-decoration-line',
        'text-decoration-style',
        'text-decoration-color',
    ),
    'white-space': (
        'text-space-collapse',
        'text-wrap',
        'text-space-trim',
    ),
}
