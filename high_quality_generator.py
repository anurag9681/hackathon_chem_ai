from graphviz import Digraph
from equipment_symbols import get_equipment_color, get_equipment_shape

def create_high_quality_pfd_graphviz(process_data):
    """Create PFD using graphviz with maximum quality settings"""
    # Analyze process flow
    streams = process_data['streams']
    
    # Find equipment that are part of recycling loops
    recycles = set()
    for stream in streams:
        for other_stream in streams:
            if stream['to'] == other_stream['from'] and stream['from'] == other_stream['to']:
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
    
    # Create a directed graph with maximum quality settings
    dot = Digraph(comment='Process Flow Diagram', format='png')
    
    # Maximum quality graph attributes
    dot.attr(
        rankdir='LR',           # Left to right layout
        size='24,16',           # Larger size for maximum quality
        dpi='600',              # Very high DPI for crisp quality
        ratio='fill',           # Fill the specified size
        ranksep='1.8',          # Good space between ranks
        nodesep='1.5',          # Good space between nodes
        concentrate='true',     # Concentrate edges
        splines='ortho',        # Orthogonal splines for cleaner layout
        overlap='scale',        # Handle overlaps by scaling
        pack='true',            # Pack subgraphs
        packmode='node',        # Pack by nodes
        margin='0.5',           # Add margin around the diagram
        pad='0.3',              # Add padding around elements
        bgcolor='white',        # White background
        fontname='Arial',       # Consistent font
        fontsize='12'           # Larger font for better readability
    )
    
    dot.attr('node', 
             fontname='Arial', 
             fontsize='12',     # Larger font for better readability
             fixedsize='false',
             style='filled',
             penwidth='2')
    
    dot.attr('edge', 
             fontname='Arial', 
             fontsize='10',     # Larger edge font
             arrowsize='1.2',   # Larger arrows
             labelfloat='false',
             penwidth='2')

    # Add equipment nodes with detailed labels
    for equip in process_data['equipment']:
        equip_id = equip['id']
        equip_type = equip['type']
        equip_spec = equip.get('spec', '')
        
        # Create detailed label with equipment info and parameters
        # Limit text length to prevent breaking
        label_parts = [f"<B>{equip_id}</B>"]  # Bold ID
        
        # Add equipment type (limit length)
        equip_type_short = equip_type.replace('_', ' ').title()
        if len(equip_type_short) > 15:  # Limit type length
            equip_type_short = equip_type_short[:15] + "..."
        label_parts.append(f"<I>{equip_type_short}</I>")  # Italic type
        
        # Add specification if available (limit length)
        if equip_spec:
            spec_short = equip_spec[:20] + "..." if len(equip_spec) > 20 else equip_spec
            label_parts.append(f"<FONT POINT-SIZE='10'>{spec_short}</FONT>")
        
        # Add parameters
        params = []
        
        # Add temperature if mentioned
        temp_fields = ['temperature', 'temp', 'operating_temp', 'design_temp']
        for field in temp_fields:
            if field in equip and equip[field]:
                temp_str = f"T: {equip[field]}°C"
                if len(temp_str) <= 12:
                    params.append(temp_str)
                break
        
        # Add pressure if mentioned
        pressure_fields = ['pressure', 'pres', 'operating_pres', 'design_pres']
        for field in pressure_fields:
            if field in equip and equip[field]:
                pres_str = f"P: {equip[field]} bar"
                if len(pres_str) <= 12:
                    params.append(pres_str)
                break
        
        # Add flow rate if mentioned
        flow_fields = ['flow', 'flow_rate', 'capacity', 'design_flow']
        for field in flow_fields:
            if field in equip and equip[field]:
                flow_str = f"Flow: {equip[field]} kg/hr"
                if len(flow_str) <= 15:
                    params.append(flow_str)
                break
        
        # Add duty if mentioned
        duty_fields = ['duty', 'heat_duty', 'cooling_duty', 'power']
        for field in duty_fields:
            if field in equip and equip[field]:
                duty_str = f"Duty: {equip[field]} kW"
                if len(duty_str) <= 15:
                    params.append(duty_str)
                break
        
        # Add efficiency if mentioned
        eff_fields = ['efficiency', 'eff', 'design_eff']
        for field in eff_fields:
            if field in equip and equip[field]:
                eff_str = f"Eff: {equip[field]}%"
                if len(eff_str) <= 12:
                    params.append(eff_str)
                break
        
        # Add stages if mentioned
        stage_fields = ['stages', 'trays', 'number_of_trays']
        for field in stage_fields:
            if field in equip and equip[field]:
                stage_str = f"Stages: {equip[field]}"
                if len(stage_str) <= 12:
                    params.append(stage_str)
                break
        
        # Add parameters to label
        if params:
            selected_params = params[:3]  # Limit to 3 parameters
            param_str = " | ".join(selected_params)
            label_parts.append(f"<FONT POINT-SIZE='9'>{param_str}</FONT>")
        # Add temperature and pressure to the equipment label if available
        temp_fields = ['temperature', 'temp', 'operating_temp', 'design_temp']
        for field in temp_fields:
            if field in equip and equip[field]:
                temp_str = f"T: {equip[field]}°C"
                label_parts.append(temp_str)
                break

        pressure_fields = ['pressure', 'pres', 'operating_pres', 'design_pres']
        for field in pressure_fields:
            if field in equip and equip[field]:
                pres_str = f"P: {equip[field]} bar"
                label_parts.append(pres_str)
                break
        # Combine all parts with HTML formatting for better alignment
        detailed_label = f"<{'<BR ALIGN=\"LEFT\"/>' .join(label_parts)}>"
        
        # Set color and shape based on equipment type
        fillcolor = get_equipment_color(equip_type)
        shape = get_equipment_shape(equip_type)
        
        # Highlight mixing and splitting points
        if equip_id in mixing_points:
            dot.node(equip_id, detailed_label,
                    fillcolor=fillcolor, 
                    style='filled,bold', 
                    shape=shape,
                    penwidth='3.5',
                    fontsize='12',
                    width='2.0',
                    height='1.4')
        elif equip_id in splitting_points:
            dot.node(equip_id, detailed_label,
                    fillcolor=fillcolor, 
                    style='filled,dashed', 
                    shape=shape,
                    penwidth='3.0',
                    fontsize='12',
                    width='2.0',
                    height='1.4')
        else:
            dot.node(equip_id, detailed_label,
                    fillcolor=fillcolor, 
                    style='filled', 
                    shape=shape,
                    fontsize='12',
                    width='1.8',
                    height='1.2')

    # Add stream edges with detailed labels
    for stream in process_data['streams']:
        # Create detailed stream label
        stream_label_parts = [f"<B>{stream['id']}</B>"]  # Bold ID
        
        # Add parameters
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
        
        # Limit to first 3 parameters
        detailed_stream_label = f"<{'<BR ALIGN=\"LEFT\"/>' .join(stream_label_parts[:4])}>"
        
        # Check if this is a recycling stream
        stream_pair = tuple(sorted([stream['from'], stream['to']]))
        is_recycle = stream_pair in recycles
        
        if is_recycle:
            dot.edge(stream['from'], stream['to'], 
                    label=detailed_stream_label,
                    style='dashed',
                    color='red',
                    penwidth='3.0',
                    fontcolor='red',
                    fontsize='10',
                    constraint='false',
                    dir='back')
        else:
            dot.edge(stream['from'], stream['to'], 
                    label=detailed_stream_label,
                    constraint='true',
                    fontsize='10',
                    penwidth='2.5')

    return dot

def generate_high_quality_pfd_image(process_data):
    """Generate high-quality PFD image as bytes"""
    pfd_graph = create_high_quality_pfd_graphviz(process_data)
    # Render to PNG bytes with maximum quality
    png_data = pfd_graph.pipe(format='png')
    return png_data