from collections import OrderedDict
import json
from stemp_abw.forms import LayerGroupForm, ComponentGroupForm, AreaGroupForm,\
    ScenarioDropdownForm

from stemp_abw.app_settings import LAYER_AREAS_METADATA, LAYER_REGION_METADATA,\
    LAYER_DEFAULT_STYLES, ESYS_COMPONENTS_METADATA, ESYS_AREAS_METADATA, LABELS


def prepare_layer_data():

    def _config2layer(cat_name, layer_cfg_metadata):
        layer_data = {}

        # create layer list for AJAX data urls,
        # include show (initial showup) and title (for spinner)
        layer_list = {l: {'show': d['show'],
                          'model': d['model'],
                          'cat': cat_name}
                      for ls in layer_cfg_metadata.values()
                      for l, d in ls.items()}
        for l, v in layer_list.items():
            layer_list[l]['title'] = LABELS['layers'][l]['title']

        # create JSON for layer styles
        layer_style = {l: a['style']
                       for v in layer_cfg_metadata.values()
                       for l, a in v.items()}
        layer_style.update(LAYER_DEFAULT_STYLES)

        # create dict choropleth layers
        choropleth_data = {l: a['choropleth']
                           for v in layer_cfg_metadata.values()
                           for l, a in v.items() if 'choropleth' in a}

        # update layer and layer group labels using labels config
        layer_metadata = OrderedDict()
        for (grp, layers) in layer_cfg_metadata.items():
            layer_metadata.update({grp: {'layers': layers}})
            layer_metadata[grp]['title'] = LABELS['layer_groups'][grp]['title']
            layer_metadata[grp]['text'] = LABELS['layer_groups'][grp]['text']
            for l, v in layers.items():
                layer_metadata[grp]['layers'][l]['title'] = LABELS['layers'][l]['title']
                layer_metadata[grp]['layers'][l]['text'] = LABELS['layers'][l]['text']

        # create layer groups for layer menu using layers config
        layer_groups = layer_metadata.copy()
        for grp, layers in layer_metadata.items():
            layer_groups[grp]['layers'] = LayerGroupForm(layers=layers['layers'],
                                                         cat_name=cat_name)
        layer_data['layer_groups'] = layer_groups

        return layer_data, layer_list, layer_style, choropleth_data

    # categories are different lists of layers, e.g.
    # 'region' is for the info layers of the status quo (region panel)
    # 'areas' is for areas that put restrictions on use for e.g. wind turbines
    layer_categories = {'areas': LAYER_AREAS_METADATA,
                        'region': LAYER_REGION_METADATA}

    # init data dict
    layer_data = {'layer_list': {},
                  'layer_style': {},
                  'choropleth_data': {}
                  }

    # prepare and fill
    for cat, metadata in layer_categories.items():
        ld, ll, ls, cd = _config2layer(cat, metadata)
        layer_data.update({'layer_{cat}'.format(cat=cat): ld})
        layer_data['layer_list'].update(ll)
        layer_data['layer_style'].update(ls)
        layer_data['choropleth_data'].update(cd)

    # serialize style data
    layer_data['layer_style'] = json.dumps(layer_data['layer_style'])
    layer_data['choropleth_data'] = json.dumps(layer_data['choropleth_data'])

    return layer_data


def prepare_component_data():
    component_data = {}

    # update component/area and group labels using labels config
    comp_metadata = OrderedDict()
    area_metadata = OrderedDict()
    for (grp, comps) in ESYS_COMPONENTS_METADATA.items():
        comp_metadata.update({grp: {'comps': comps}})
        comp_metadata[grp]['title'] = LABELS['component_groups'][grp]['title']
        comp_metadata[grp]['text'] = LABELS['component_groups'][grp]['text']
        for l, v in comps.items():
            comp_metadata[grp]['comps'][l]['title'] = LABELS['components'][l]['title']
            comp_metadata[grp]['comps'][l]['text'] = LABELS['components'][l]['text']
            if LABELS['components'][l].get('text2') is not None:
                comp_metadata[grp]['comps'][l]['text2'] = LABELS['components'][l]['text2']

    for (grp, comps) in ESYS_AREAS_METADATA.items():
        area_metadata.update({grp: {'comps': comps}})
        area_metadata[grp]['title'] = LABELS['component_groups'][grp]['title']
        area_metadata[grp]['text'] = LABELS['component_groups'][grp]['text']
        for l, v in comps.items():
            area_metadata[grp]['comps'][l]['title'] = LABELS['components'][l]['title']
            area_metadata[grp]['comps'][l]['text'] = LABELS['components'][l]['text']

    # create component groups for esys panel using components config
    comp_groups = comp_metadata.copy()
    for grp, comps in comp_groups.items():
        comp_groups[grp]['comps'] = ComponentGroupForm(components=comps['comps'])
    component_data['comp_groups'] = comp_groups

    # create area groups for areas panel (variable areas) using components config
    area_groups = area_metadata.copy()
    for grp, comps in area_groups.items():
        area_groups[grp]['comps'] = AreaGroupForm(components=comps['comps'])
    component_data['area_groups'] = area_groups

    return component_data


def prepare_scenario_data():
    """create scenarios for scenario dropdown menu (tool initialization only)"""
    return {'scenarios': ScenarioDropdownForm()}

    
def prepare_label_data():
    return {'panels': LABELS['panels'],
            'tooltips': LABELS['tooltips']}
