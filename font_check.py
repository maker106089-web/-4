import warnings
warnings.filterwarnings('error')
import matplotlib
matplotlib.use('Agg')
from matplotlib import font_manager, pyplot as plt

preferred = [
    'Microsoft JhengHei',
    'PingFang TC',
    'Noto Sans CJK TC',
    'Noto Sans TC',
    'Source Han Sans TC',
    'WenQuanYi Zen Hei',
    'WenQuanYi Micro Hei',
    'Microsoft YaHei',
    'SimHei',
    'Arial Unicode MS',
    'sans-serif',
]
available = {f.name for f in font_manager.fontManager.ttflist}
selected = next((font for font in preferred if font in available), 'DejaVu Sans')
print('selected=', selected)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = preferred
plt.rcParams['axes.unicode_minus'] = False
plt.figure()
plt.title('台東農產品價格')
plt.xlabel('日期')
plt.ylabel('價格')
plt.plot(['一', '二', '三'], [10, 20, 15])
plt.savefig('font_check.png', dpi=120)
print('render_ok')
