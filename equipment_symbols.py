EQUIPMENT_TEMPLATES = {
    "reactor": {"shape": "rectangle", "style": "filled", "fillcolor": "lightblue", "color": "black", "width": "1.5", "height": "1.0"},
    "distillation": {"shape": "cylinder", "style": "filled", "fillcolor": "lightgreen", "color": "black", "width": "1.2", "height": "2.0"},
    "column": {"shape": "cylinder", "style": "filled", "fillcolor": "lightgreen", "color": "black", "width": "1.2", "height": "2.0"},
    "exchanger": {"shape": "ellipse", "style": "filled", "fillcolor": "lightyellow", "color": "black", "width": "1.5", "height": "1.0"},
    "heat": {"shape": "ellipse", "style": "filled", "fillcolor": "lightyellow", "color": "black", "width": "1.5", "height": "1.0"},
    "compressor": {"shape": "triangle", "style": "filled", "fillcolor": "orange", "color": "black", "width": "1.2", "height": "1.2"},
    "pump": {"shape": "invtriangle", "style": "filled", "fillcolor": "pink", "color": "black", "width": "1.2", "height": "1.2"},
    "separator": {"shape": "cylinder", "style": "filled", "fillcolor": "lightgrey", "color": "black", "width": "1.5", "height": "1.0"},
    "vessel": {"shape": "cylinder", "style": "filled", "fillcolor": "lightgrey", "color": "black", "width": "1.5", "height": "1.0"},
    "tank": {"shape": "cylinder", "style": "filled", "fillcolor": "lightgrey", "color": "black", "width": "1.5", "height": "1.0"},
    "condenser": {"shape": "ellipse", "style": "filled", "fillcolor": "lightcyan", "color": "black", "width": "1.5", "height": "1.0"},
    "cooler": {"shape": "ellipse", "style": "filled", "fillcolor": "lightcyan", "color": "black", "width": "1.5", "height": "1.0"},
    "heater": {"shape": "ellipse", "style": "filled", "fillcolor": "lightcoral", "color": "black", "width": "1.5", "height": "1.0"},
    "mixer": {"shape": "circle", "style": "filled", "fillcolor": "lightgray", "color": "black", "width": "1.0", "height": "1.0"},
    "splitter": {"shape": "circle", "style": "filled", "fillcolor": "lightgray", "color": "black", "width": "1.0", "height": "1.0"},
    "default": {"shape": "box", "style": "filled", "fillcolor": "white", "color": "black", "width": "1.2", "height": "0.8"}
}
def get_equipment_color(equip_type):
    equip_type_lower = equip_type.lower()
    for key, style in EQUIPMENT_TEMPLATES.items():
        if key in equip_type_lower:
            return style.get("fillcolor", "#F5F5F5")
    # fallback color_map from your original second code here...
    # (copy your original fallback color_map here)
    return '#F5F5F5'  # default fallback color

def get_equipment_shape(equip_type):
    equip_type_lower = equip_type.lower()
    for key, style in EQUIPMENT_TEMPLATES.items():
        if key in equip_type_lower:
            return style.get("shape", "box")
    # fallback shape_map from your original second code here...
    return 'box'  # default fallback shape
