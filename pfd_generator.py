from graphviz import Digraph
from equipment_symbols import get_equipment_color, get_equipment_shape

def analyze_process_flow(process_data):
    """Analyze process flow to identify recycling and optimize layout"""
    streams = process_data['streams']
    
    # Find equipment that are part of recycling loops
    recycles = set()
    for stream in streams:
        for other_stream in streams:
            if stream['to'] == other_stream['from'] and stream['from'] == other_stream['to']:
                # Create a consistent tuple (smaller ID first to avoid duplicates)
                pair = tuple(sorted([stream['from'], stream['to']]))
                recycles.add(pair)
    
    # Find equipment with multiple incoming streams (mixing points)
    incoming_counts = {}
    for stream in streams:
        incoming_counts[stream['to']] = incoming_counts.get(stream['to'], 0) + 1
    
    mixing_points = [eq for eq, count in incoming_counts.items() if count > 1]
    
    # Find equipment with multiple outgoing streams (splitting points)
    outgoing_counts = {}
    for stream in streams:
        outgoing_counts[stream['from']] = outgoing_counts.get(stream['from'], 0) + 1
    
    splitting_points = [eq for eq, count in outgoing_counts.items() if count > 1]
    
    # Find the main process flow path
    all_from = set([s['from'] for s in streams])
    all_to = set([s['to'] for s in streams])
    start_equips = list(all_from - all_to)  # Equipment with no incoming streams
    end_equips = list(all_to - all_from)    # Equipment with no outgoing streams
    
    if not start_equips:
        start_equips = [process_data['equipment'][0]['id']] if process_data['equipment'] else []
    
    return {
        'recycles': recycles,
        'mixing_points': mixing_points,
        'splitting_points': splitting_points,
        'incoming_counts': incoming_counts,
        'outgoing_counts': outgoing_counts,
        'start_equips': start_equips,
        'end_equips': end_equips
    }

def create_pfd_graphviz(process_data):
    """Create PFD using graphviz with detailed equipment labels and optimal layout"""
    # Analyze process flow
    flow_analysis = analyze_process_flow(process_data)
    
    # Create a directed graph with optimized settings
    dot = Digraph(comment='Process Flow Diagram', format='png')
    
    # Optimized graph attributes for better layout and quality
    dot.attr(
        rankdir='LR',           # Left to right layout
        size='18,12',           # Good size for layout
        dpi='300',              # High DPI for quality
        ratio='fill',           # Fill the specified size
        ranksep='1.5',          # Good space between ranks
        nodesep='1.2',          # Good space between nodes
        concentrate='true',     # Concentrate edges
        splines='ortho',        # Orthogonal splines for cleaner layout
        overlap='scale',        # Handle overlaps by scaling
        pack='true',            # Pack subgraphs
        packmode='node',        # Pack by nodes
        margin='0.5',           # Add margin around the diagram
        pad='0.3'               # Add padding around elements
    )
    
    dot.attr('node', 
             fontname='Arial', 
             fontsize='10',     # Good font size for detailed labels
             fixedsize='false') # Allow variable size for detailed labels
    
    dot.attr('edge', 
             fontname='Arial', 
             fontsize='9',      # Good font size for stream labels
             arrowsize='1.0',   # Larger arrows for better visibility
             labelfloat='false') # Keep labels attached to edges

    # Create subgraphs to group related equipment and prevent scattering
    # Group equipment by process flow hierarchy
    if flow_analysis['start_equips']:
        with dot.subgraph(name='cluster_main_flow') as c:
            c.attr(style='filled', color='lightgrey', fillcolor='lightgrey', label='Main Process Flow')
    
    # Add equipment nodes with detailed labels and proper text wrapping
    for equip in process_data['equipment']:
        equip_id = equip['id']
        equip_type = equip['type']
        equip_spec = equip.get('spec', '')
        
        # Create detailed label with equipment info and parameters
        # Limit text length to prevent breaking
        label_parts = [equip_id]
        
        # Add equipment type (limit length)
        equip_type_short = equip_type.replace('_', ' ').title()
        if len(equip_type_short) > 15:  # Limit type length
            equip_type_short = equip_type_short[:15] + "..."
        label_parts.append(equip_type_short)
        
        # Add specification if available (limit length)
        if equip_spec:
            spec_short = equip_spec[:20] + "..." if len(equip_spec) > 20 else equip_spec
            label_parts.append(spec_short)
        
        # Add any additional parameters that might be in the equipment data
        params = []
        
        # Add temperature if mentioned (limit length)
        temp_fields = ['temperature', 'temp', 'operating_temp', 'design_temp']
        for field in temp_fields:
            if field in equip and equip[field]:
                temp_str = f"T: {equip[field]}°C"
                if len(temp_str) <= 12:  # Reasonable length
                    params.append(temp_str)
                break
        
        # Add pressure if mentioned (limit length)
        pressure_fields = ['pressure', 'pres', 'operating_pres', 'design_pres']
        for field in pressure_fields:
            if field in equip and equip[field]:
                pres_str = f"P: {equip[field]} bar"
                if len(pres_str) <= 12:
                    params.append(pres_str)
                break
        
        # Add flow rate if mentioned (limit length)
        flow_fields = ['flow', 'flow_rate', 'capacity', 'design_flow']
        for field in flow_fields:
            if field in equip and equip[field]:
                flow_str = f"Flow: {equip[field]} kg/hr"
                if len(flow_str) <= 15:
                    params.append(flow_str)
                break
        
        # Add duty if mentioned (for heat exchangers, etc.)
        duty_fields = ['duty', 'heat_duty', 'cooling_duty', 'power']
        for field in duty_fields:
            if field in equip and equip[field]:
                duty_str = f"Duty: {equip[field]} kW"
                if len(duty_str) <= 15:
                    params.append(duty_str)
                break
        
        # Add efficiency if mentioned (for pumps, compressors)
        eff_fields = ['efficiency', 'eff', 'design_eff']
        for field in eff_fields:
            if field in equip and equip[field]:
                eff_str = f"Eff: {equip[field]}%"
                if len(eff_str) <= 12:
                    params.append(eff_str)
                break
        
        # Add stages if mentioned (for columns)
        stage_fields = ['stages', 'trays', 'number_of_trays']
        for field in stage_fields:
            if field in equip and equip[field]:
                stage_str = f"Stages: {equip[field]}"
                if len(stage_str) <= 12:
                    params.append(stage_str)
                break
        
        # Add all parameters to the label (limit total params to prevent overcrowding)
        if params:
            # Take only first 3 parameters to prevent text breaking
            selected_params = params[:3]
            param_str = " | ".join(selected_params)
            label_parts.append(param_str)
        
        # Combine all parts with proper formatting
        detailed_label = "\\n".join(label_parts)
        
        # Set color and shape based on equipment type
        fillcolor = get_equipment_color(equip_type)
        shape = get_equipment_shape(equip_type)
        
        # Highlight mixing and splitting points with larger nodes
        if equip_id in flow_analysis['mixing_points']:
            # Bold border for mixing points
            dot.node(equip_id, detailed_label,
                    fillcolor=fillcolor, 
                    style='filled,bold', 
                    shape=shape,
                    penwidth='3.0',
                    fontsize='10',
                    width='1.8',      # Larger width for detailed labels
                    height='1.2')     # Larger height for detailed labels
        elif equip_id in flow_analysis['splitting_points']:
            # Dashed border for splitting points
            dot.node(equip_id, detailed_label,
                    fillcolor=fillcolor, 
                    style='filled,dashed', 
                    shape=shape,
                    penwidth='2.5',
                    fontsize='10',
                    width='1.8',
                    height='1.2')
        else:
            dot.node(equip_id, detailed_label,
                    fillcolor=fillcolor, 
                    style='filled', 
                    shape=shape,
                    fontsize='10',
                    width='1.6',      # Larger width for detailed labels
                    height='1.0')     # Larger height for detailed labels

    # Add stream edges with detailed labels and text wrapping
    for stream in process_data['streams']:
        # Create detailed stream label with limited text
        stream_label_parts = [stream['id']]
        
        # Add any stream parameters (limit length)
        temp_fields = ['temperature', 'temp', 'stream_temp']
        for field in temp_fields:
            if field in stream and stream[field]:
                temp_str = f"T: {stream[field]}°C"
                if len(temp_str) <= 12:
                    stream_label_parts.append(temp_str)
                break
        
        pressure_fields = ['pressure', 'pres', 'stream_pres']
        for field in pressure_fields:
            if field in stream and stream[field]:
                pres_str = f"P: {stream[field]} bar"
                if len(pres_str) <= 12:
                    stream_label_parts.append(pres_str)
                break
        
        flow_fields = ['flow', 'flow_rate', 'stream_flow']
        for field in flow_fields:
            if field in stream and stream[field]:
                flow_str = f"Flow: {stream[field]} kg/hr"
                if len(flow_str) <= 15:
                    stream_label_parts.append(flow_str)
                break
        
        comp_fields = ['comp', 'composition', 'stream_comp']
        for field in comp_fields:
            if field in stream and stream[field]:
                comp = stream[field][:20] + "..." if len(str(stream[field])) > 20 else str(stream[field])
                comp_str = f"Comp: {comp}"
                if len(comp_str) <= 20:
                    stream_label_parts.append(comp_str)
                break
        
        # Limit to first 3 parameters to prevent text breaking
        detailed_stream_label = "\\n".join(stream_label_parts[:4])  # ID + up to 3 params
        
        # Check if this is a recycling stream
        stream_pair = tuple(sorted([stream['from'], stream['to']]))
        is_recycle = stream_pair in flow_analysis['recycles']
        
        if is_recycle:
            # Styling for recycling streams - dashed with special properties
            dot.edge(stream['from'], stream['to'], 
                    label=detailed_stream_label,
                    style='dashed',
                    color='red',
                    penwidth='2.5',
                    fontcolor='red',
                    fontsize='9',
                    constraint='false',  # Allow edge to bypass normal layout constraints
                    dir='back')  # Arrow points back for recycling
        else:
            # Regular stream
            dot.edge(stream['from'], stream['to'], 
                    label=detailed_stream_label,
                    constraint='true',   # Follow normal layout constraints
                    fontsize='9',
                    penwidth='2.0')

    return dot

def generate_pfd_image(process_data):
    """Generate PFD image as bytes with optimized quality"""
    pfd_graph = create_pfd_graphviz(process_data)
    # Render to PNG bytes with high quality
    png_data = pfd_graph.pipe(format='png')
    return png_data