"""Build a reusable theme from the Power BI skill's visual safeguards."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
base = root / '.agents/skills/powerbi-report-cli/references/design/assets/base.json'
theme = json.loads(base.read_text(encoding='utf-8'))
replacements = {
    '#252423': '#0B1B30', '#605E5C': '#5B6B80', '#E8E8E8': '#D5DDE7',
    '#F3F2F1': '#FDF6EC', '#F9F9F8': '#FDF6EC',
    'Segoe UI Variable, Segoe UI, sans-serif': 'Segoe UI',
}
def adapt(value):
    if isinstance(value, dict):
        return {key: adapt(item) for key, item in value.items()}
    if isinstance(value, list):
        return [adapt(item) for item in value]
    return replacements.get(value, value) if isinstance(value, str) else value
theme = adapt(theme)
theme.update({
    '$schema': 'https://raw.githubusercontent.com/microsoft/powerbi-desktop-samples/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.157.json',
    'name': 'Aubeco – läsbar analys',
    'dataColors': ['#0F3163', '#9B570B', '#4A6BCE', '#5B6B80'],
    'good': '#007956', 'neutral': '#946200', 'bad': '#B42318',
    'minimum': '#FDF6EC', 'center': '#FBD6A8', 'maximum': '#0F3163', 'null': '#5B6B80',
    'foreground': '#0B1B30', 'firstLevelElements': '#0B1B30',
    'secondLevelElements': '#5B6B80', 'thirdLevelElements': '#D5DDE7',
    'fourthLevelElements': '#5B6B80', 'background': '#FFFFFF',
    'secondaryBackground': '#FDF6EC', 'tableAccent': '#0F3163',
    'accent': '#F7BA6B',
})
theme['textClasses'] = {
    'callout': {'fontSize': 32, 'fontFace': 'Segoe UI Semibold', 'color': '#0F3163'},
    'title': {'fontSize': 20, 'fontFace': 'Segoe UI Semibold', 'color': '#0F3163'},
    'header': {'fontSize': 12, 'fontFace': 'Segoe UI Semibold', 'color': '#0B1B30'},
    'label': {'fontSize': 11, 'fontFace': 'Segoe UI', 'color': '#5B6B80'},
}
solid = lambda color: {'solid': {'color': color}}
general = theme['visualStyles']['*']['*']
general.update({
    'background': [{'show': True, 'color': solid('#FFFFFF'), 'transparency': 0}],
    'title': [{'show': True, 'fontFamily': 'Segoe UI Semibold', 'fontSize': 14, 'fontColor': solid('#0F3163')}],
    'visualHeader': [{'show': False}],
})
# Light rules belong to chart axes; the sand token belongs to page/table surfaces.
for key in ('categoryAxis', 'valueAxis'):
    general[key][0]['gridlineColor'] = solid('#D5DDE7')
theme['visualStyles']['page'] = {'*': {'background': [{'color': solid('#FDF6EC'), 'transparency': 0}]}}
theme['visualStyles']['cardVisual']['*']['value'][0].update({'fontSize': 32, 'fontFamily': 'Segoe UI Semibold', 'fontColor': solid('#0F3163')})
theme['visualStyles']['cardVisual']['*']['label'][0].update({'fontSize': 11, 'fontFamily': 'Segoe UI', 'fontColor': solid('#5B6B80')})
theme['visualStyles']['card'] = {'*': {
    'labels': [{'fontSize': 32, 'fontFamily': 'Segoe UI Semibold', 'color': solid('#0F3163')}],
    'categoryLabels': [{'show': True, 'fontSize': 11, 'fontFamily': 'Segoe UI', 'color': solid('#5B6B80')}],
    'title': [{'show': False}],
}}
for visual in ('barChart','clusteredBarChart','columnChart','clusteredColumnChart','lineChart'):
    config = theme['visualStyles'][visual]['*']
    for object_name in ('labels','categoryAxis','valueAxis','legend'):
        for entry in config.get(object_name, []):
            if 'fontSize' in entry:
                entry['fontSize'] = 11
    if visual == 'lineChart':
        # Do not invent smoothed paths between real observations.
        config['lineStyles'][0] = {'strokeWidth': 2.5, 'lineChartType': 'linear', 'areaShow': False}
        config['dataPoint'][0]['transparency'] = 0
for object_name in ('header','items','date'):
    for entry in theme['visualStyles']['slicer']['*'][object_name]:
        entry['textSize'] = 11
theme['visualStyles']['slicer']['*']['items'][0]['padding'] = 6
(root / 'themes/aubeco-powerbi.json').write_text(json.dumps(theme, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Built themes/aubeco-powerbi.json')
