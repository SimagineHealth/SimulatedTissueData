import lib3mf
from lib3mf_common import *
import sys

def add_red_to_triangles(input_file):
    # Load the 3MF file
    # Get a wrapper object
    wrapper = get_wrapper()

    # Check version always
    get_version(wrapper)

    model = wrapper.CreateModel()
    read_3mf_file_to_model(model, input_file)
    show_object_information(model)

    # # Iterate through all objects in the model
    # for obj in model.objects:
    #     if obj.mesh:
    #         # Add red color to all triangles
    #         red_color = lib3mf.Color(1.0, 0.0, 0.0, 1.0)  # RGBA for red
    #         for triangle in obj.mesh.triangles:
    #             triangle.color = red_color

    # # Save the modified 3MF file
    # with open(input_file, 'wb') as f:
    #     model.write(f)

## add volume data to mesh model 
def create_volumetric_cubes_in_mesh(model, mesh_object, voxel_resolution=8):
    """
    Create a series of colored cubes (voxels) that fill a mesh using 3MF volumetric extensions.
    Each cube gets a different color to represent volumetric data.
    """
    try:

        # Calculate bounding box of the mesh
        vertices = []
        for i in range(mesh_object.GetVertexCount()):
            vertex = mesh_object.GetVertex(i)
            vertices.append([vertex.Coordinates[0], vertex.Coordinates[1], vertex.Coordinates[2]])
        
        if not vertices:
            print("No vertices found in mesh")
            return
        
        # Find min/max coordinates
        min_coords = [min(v[0] for v in vertices), min(v[1] for v in vertices), min(v[2] for v in vertices)]
        max_coords = [max(v[0] for v in vertices), max(v[1] for v in vertices), max(v[2] for v in vertices)]
        
        # Calculate voxel size
        size_x = max_coords[0] - min_coords[0]
        size_y = max_coords[1] - min_coords[1]
        size_z = max_coords[2] - min_coords[2]
        
        voxel_size_x = size_x / voxel_resolution
        voxel_size_y = size_y / voxel_resolution
        voxel_size_z = size_z / voxel_resolution
        
        print(f"Creating {voxel_resolution}x{voxel_resolution}x{voxel_resolution} voxel grid")
        print(f"Voxel size: {voxel_size_x:.3f} x {voxel_size_y:.3f} x {voxel_size_z:.3f}")
        
        # Create individual cube objects for each voxel
        voxel_count = 0
        for x in range(voxel_resolution):
            for y in range(voxel_resolution):
                for z in range(voxel_resolution):
                    # Calculate voxel position
                    pos_x = min_coords[0] + x * voxel_size_x + voxel_size_x/2
                    pos_y = min_coords[1] + y * voxel_size_y + voxel_size_y/2
                    pos_z = min_coords[2] + z * voxel_size_z + voxel_size_z/2
                    
                    # Create a small cube mesh for this voxel
                    voxel_object = model.AddMeshObject()
                    voxel_object.SetName(f"voxel_{x}_{y}_{z}")                    
                    # Create cube vertices (8 vertices for a cube)
                    half_x, half_y, half_z = voxel_size_x/2, voxel_size_y/2, voxel_size_z/2
                    
                    # Add vertices
                    v0 = create_vertex_and_return_index(voxel_object, pos_x - half_x, pos_y - half_y, pos_z - half_z)
                    v1 = create_vertex_and_return_index(voxel_object, pos_x + half_x, pos_y - half_y, pos_z - half_z)
                    v2 = create_vertex_and_return_index(voxel_object, pos_x + half_x, pos_y + half_y, pos_z - half_z)
                    v3 = create_vertex_and_return_index(voxel_object, pos_x - half_x, pos_y + half_y, pos_z - half_z)
                    v4 = create_vertex_and_return_index(voxel_object, pos_x - half_x, pos_y - half_y, pos_z + half_z)
                    v5 = create_vertex_and_return_index(voxel_object, pos_x + half_x, pos_y - half_y, pos_z + half_z)
                    v6 = create_vertex_and_return_index(voxel_object, pos_x + half_x, pos_y + half_y, pos_z + half_z)
                    v7 = create_vertex_and_return_index(voxel_object, pos_x - half_x, pos_y + half_y, pos_z + half_z)

                    # Add triangles for cube faces (12 triangles total)
                    # Bottom face
                    add_triangle(voxel_object, v0, v1, v2)
                    add_triangle(voxel_object, v0, v2, v3)
                    # Top face
                    add_triangle(voxel_object, v4, v6, v5)
                    add_triangle(voxel_object, v4, v7, v6)
                    # Front face
                    add_triangle(voxel_object, v0, v4, v5)
                    add_triangle(voxel_object, v0, v5, v1)
                    # Back face
                    add_triangle(voxel_object, v2, v6, v7)
                    add_triangle(voxel_object, v2, v7, v3)
                    # Left face
                    add_triangle(voxel_object, v0, v3, v7)
                    add_triangle(voxel_object, v0, v7, v4)
                    # Right face
                    add_triangle(voxel_object, v1, v5, v6)
                    add_triangle(voxel_object, v1, v6, v2)

                    # Assign a unique color based on position
                    red = (x / voxel_resolution)
                    green = (y / voxel_resolution)
                    blue = (z / voxel_resolution)
                    
                    # Create color resource
                    color_group = model.AddColorGroup()
                    color_id = color_group.AddColor(lib3mf.Color(int(red * 255), int(green * 255), int(blue * 255), 255))
                    
                    # Apply color to all triangles using helper function
                    for tri_idx in range(voxel_object.GetTriangleCount()):
                        create_triangle_color(color_group, color_id, color_id, color_id)
                    
                    # Set object name
                    voxel_object.SetName(f"voxel_{x}_{y}_{z}")
                    
                    # Add metadata (commented out - MeshObject doesn't support SetMetaData)
                    # voxel_object.SetMetaData("voxel_position", f"{x},{y},{z}")
                    # voxel_object.SetMetaData("voxel_color", f"{red:.3f},{green:.3f},{blue:.3f}")
                    
                    voxel_count += 1
        
        print(f"Created {voxel_count} volumetric cubes")
        
        # Add metadata to original mesh about volumetric data (commented out - MeshObject doesn't support SetMetaData)
        # mesh_object.SetMetaData("has_volumetric_data", "true")
        # mesh_object.SetMetaData("voxel_resolution", str(voxel_resolution))
        # mesh_object.SetMetaData("voxel_count", str(voxel_count))
        
    except Exception as e:
        print(f"Error creating volumetric cubes: {e}")

# Get a wrapper object
wrapper = get_wrapper()

# Check version always
get_version(wrapper)

# Create a model
model = wrapper.CreateModel()
mesh_object = model.AddMeshObject()
mesh_object.SetName("volumetric_mesh")


# Define cube dimensions
cube_size = 10.0
half_size = cube_size / 2

# Add 8 vertices for a cube
v0 = create_vertex_and_return_index(mesh_object, -half_size, -half_size, -half_size)
v1 = create_vertex_and_return_index(mesh_object, half_size, -half_size, -half_size)
v2 = create_vertex_and_return_index(mesh_object, half_size, half_size, -half_size)
v3 = create_vertex_and_return_index(mesh_object, -half_size, half_size, -half_size)
v4 = create_vertex_and_return_index(mesh_object, -half_size, -half_size, half_size)
v5 = create_vertex_and_return_index(mesh_object, half_size, -half_size, half_size)
v6 = create_vertex_and_return_index(mesh_object, half_size, half_size, half_size)
v7 = create_vertex_and_return_index(mesh_object, -half_size, half_size, half_size)


# Add 12 triangles to form the cube faces
# Bottom face (z = -half_size)
add_triangle(mesh_object, v0, v2, v1)
add_triangle(mesh_object, v0, v3, v2)

# Top face (z = half_size)
add_triangle(mesh_object, v4, v5, v6)
add_triangle(mesh_object, v4, v6, v7)

# Front face (y = -half_size)
add_triangle(mesh_object, v0, v1, v5)
add_triangle(mesh_object, v0, v5, v4)

# Back face (y = half_size)
add_triangle(mesh_object, v2, v7, v6)
add_triangle(mesh_object, v2, v3, v7)

# Left face (x = -half_size)
add_triangle(mesh_object, v0, v4, v7)
add_triangle(mesh_object, v0, v7, v3)

# Right face (x = half_size)
add_triangle(mesh_object, v1, v2, v6)
add_triangle(mesh_object, v1, v6, v5)
mesh_object.SetGeometry(vertices, triangles)


print(f"Created cube mesh with {mesh_object.GetVertexCount()} vertices and {mesh_object.GetTriangleCount()} triangles")

if mesh_object:
    # Create volumetric cubes that fill the first mesh object

    create_volumetric_cubes_in_mesh(model, mesh_object, voxel_resolution=4)
    
    # Save the modified model
    output_file = "volumetric_model_with_voxels.3mf"
    writer = model.QueryWriter("3mf")
    writer.WriteToFile(output_file)
    print(f"Saved model with volumetric cubes to: {output_file}")

# # Example usage
# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage:")
#         print("Add red to 3MF file: python3 AddColor.py model.3mf")
#     else:
#         try:
#             result = add_red_to_triangles(sys.argv[1])
#             sys.exit(result)
#         except Exception as e:
#             print(str(e)+ "\nAn error occurred during conversion.")
#             print("Please ensure you have the correct file format and the lib3mf library is properly installed.")
#             sys.exit(1)
