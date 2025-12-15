from nanohublib.ui.numvalue import Number
import ipywidgets as widgets

try:
    n = Number(name='E1', value='138 GPa', min='0 GPa', max='500 GPa', units='GPa')
    print("Successfully created Number widget with unit strings.")
    print(f"Value: {n.value}, Min: {n.min}, Max: {n.max}")
except Exception as e:
    print(f"Failed to create Number widget: {e}")
