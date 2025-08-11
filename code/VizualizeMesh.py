import streamlit as st
import numpy as np
import trimesh
from io import BytesIO
import tempfile
import os

import plotly.graph_objects as go

def load_3mf_file(uploaded_file):
    """Load a 3MF file and return the mesh"""
    try:
        # Create a temporary file to save the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.3mf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Load the mesh using trimesh
        mesh = trimesh.load(tmp_file_path, force='mesh')
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return mesh
    except Exception as e:
        st.error(f"Error loading 3MF file: {str(e)}")
        return None

def create_mesh_plot(mesh):
    """Create a 3D plot of the mesh using Plotly"""
    vertices = mesh.vertices
    faces = mesh.faces
    
    # Create the 3D mesh plot with z-axis gradient coloring
    fig = go.Figure(data=[
        go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1], 
            z=vertices[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            intensity=vertices[:, 2],  # Use z-coordinates for color intensity
            colorscale='Viridis',  # You can use other colorscales like 'Blues', 'Reds', 'Rainbow', etc.
            opacity=0.8,
            showscale=True
        )
    ])
    
    fig.update_layout(
        title="3MF Mesh Visualization",
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data'
        ),
        width=800,
        height=600
    )
    
    return fig

def main():
    st.title("3MF Mesh Viewer")
    st.write("Upload a 3MF file to visualize the mesh")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a 3MF file", 
        type=['3mf'],
        help="Upload a 3MF mesh file to visualize"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.write(f"**File name:** {uploaded_file.name}")
        st.write(f"**File size:** {uploaded_file.size} bytes")
        
        # Load and process the mesh
        with st.spinner("Loading mesh..."):
            mesh = load_3mf_file(uploaded_file)
        
        if mesh is not None:
            # Display mesh information
            st.subheader("Mesh Information")
            col1, col2, col3 = st.columns(3)

            #testing info
            print(type(mesh))
            print(dir(mesh))

            # Assuming you have access to a list of meshes inside the scene
            # for obj in mesh.objects:
            #     if hasattr(obj, 'vertices'):
            #         print(len(obj.vertices))  # Check vertices length

            with col1:
                st.metric("Vertices", len(mesh.vertices))
            with col2:
                st.metric("Faces", len(mesh.faces))
            with col3:
                st.metric("Volume", f"{mesh.volume:.2f}")
            
            # Create and display the 3D plot
            st.subheader("3D Visualization")
            fig = create_mesh_plot(mesh)
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional mesh properties
            st.subheader("Mesh Properties")
            st.write(f"**Bounding box:** {mesh.bounds}")
            st.write(f"**Center of mass:** {mesh.center_mass}")
            st.write(f"**Is watertight:** {mesh.is_watertight}")

if __name__ == "__main__":
    main()