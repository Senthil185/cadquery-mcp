# cadquery_fastmcp.py
from mcp.server.fastmcp import FastMCP, Context, Image
import os
import sys
import tempfile
import json
import base64
from typing import Optional, Dict, List, Any, Union
# At the top of your cadquery_fastmcp.py file, import the bridge
from cq_editor_bridge import CQEditorBridge, integrate_with_mcp_server



# Try to import CadQuery
try:
    import cadquery as cq
    from cadquery import exporters
    CADQUERY_AVAILABLE = True
except ImportError:
    CADQUERY_AVAILABLE = False
    print("CadQuery not found. Running in mock mode.")

# Create a temp directory for models
temp_dir = tempfile.mkdtemp(prefix="cadquery_mcp_")

# Create the MCP server
mcp = FastMCP("CadQuery", 
             dependencies=["cadquery", "numpy"])

# Store for CadQuery workspaces and objects
workspaces = {}
current_workspace_id = "default"

# Initialize default workspace
if CADQUERY_AVAILABLE:
    workspaces[current_workspace_id] = {
        "objects": {},
        "assembly": cq.Assembly(),
        "current_object": None
    }
else:
    # Mock workspace when CadQuery is not available
    workspaces[current_workspace_id] = {
        "objects": {},
        "assembly": None,
        "current_object": None
    }

def get_current_workspace():
    """Helper to get the current workspace"""
    return workspaces[current_workspace_id]

# Move bridge integration here, after the function is defined

bridge = integrate_with_mcp_server(mcp, get_current_workspace)

@mcp.resource("workspace://current")
def get_current_workspace_info() -> str:
    """Get information about the current workspace"""
    workspace = get_current_workspace()
    
    info = {
        "workspace_id": current_workspace_id,
        "object_count": len(workspace["objects"]),
        "objects": list(workspace["objects"].keys()),
        "current_object": workspace["current_object"]
    }
    
    return json.dumps(info, indent=2)

@mcp.tool()
def create_workspace(name: str) -> dict:
    """Create a new workspace
    
    Args:
        name: Name of the new workspace
    """
    global current_workspace_id
    
    if name in workspaces:
        return {
            "status": "error",
            "message": f"Workspace '{name}' already exists"
        }
    
    if CADQUERY_AVAILABLE:
        workspaces[name] = {
            "objects": {},
            "assembly": cq.Assembly(),
            "current_object": None
        }
    else:
        workspaces[name] = {
            "objects": {},
            "assembly": None,
            "current_object": None
        }
    
    current_workspace_id = name
    
    return {
        "status": "success",
        "message": f"Created workspace: {name}",
        "workspace_id": name
    }

@mcp.tool()
def switch_workspace(name: str) -> dict:
    """Switch to an existing workspace
    
    Args:
        name: Name of the workspace to switch to
    """
    global current_workspace_id
    
    if name not in workspaces:
        return {
            "status": "error",
            "message": f"Workspace '{name}' does not exist"
        }
    
    current_workspace_id = name
    
    return {
        "status": "success",
        "message": f"Switched to workspace: {name}",
        "workspace_id": name
    }

@mcp.tool()
def get_workspace_info() -> dict:
    """Get detailed information about the current design workspace"""
    workspace = get_current_workspace()
    
    return {
        "workspace_id": current_workspace_id,
        "object_count": len(workspace["objects"]),
        "objects": list(workspace["objects"].keys()),
        "current_object": workspace["current_object"],
        "temp_directory": temp_dir
    }

@mcp.tool()
def create_box(width: float = 1.0, length: float = 1.0, height: float = 1.0, 
               centered: bool = True, name: str = None) -> dict:
    """Create a box with given dimensions
    
    Args:
        width: Width of the box
        length: Length of the box
        height: Height of the box
        centered: Whether the box is centered at origin
        name: Name for the box object (optional)
    """
    workspace = get_current_workspace()
    
    if name is None:
        name = f'box_{len(workspace["objects"])}'
    
    if CADQUERY_AVAILABLE:
        # Create real CadQuery box
        box = cq.Workplane("XY")
        if centered:
            box = box.box(width, length, height)
        else:
            box = box.box(width, length, height, centered=False)
        
        # Store in workspace
        workspace["objects"][name] = {
            'type': 'box',
            'width': width,
            'length': length,
            'height': height,
            'centered': centered,
            'workplane': box
        }
        
        # Set as current object
        workspace["current_object"] = name
        
        # Export to STL
        stl_path = os.path.join(temp_dir, f"{name}.stl")
        exporters.export(box, stl_path)
    else:
        # Mock implementation
        workspace["objects"][name] = {
            'type': 'box',
            'width': width,
            'length': length,
            'height': height,
            'centered': centered
        }
        
        workspace["current_object"] = name
        
        # Create a mock file path
        stl_path = os.path.join(temp_dir, f"{name}.stl")
        with open(stl_path, 'w') as f:
            f.write("Mock STL file content")
    
    return {
        "status": "success",
        "message": f"Created box: {name}",
        "object_id": name,
        "dimensions": {
            "width": width,
            "length": length,
            "height": height
        },
        "files": {
            "stl": stl_path
        }
    }

@mcp.tool()
def create_cylinder(radius: float = 1.0, height: float = 1.0, 
                    centered: bool = True, name: str = None) -> dict:
    """Create a cylinder with given radius and height
    
    Args:
        radius: Radius of the cylinder
        height: Height of the cylinder
        centered: Whether the cylinder is centered at origin
        name: Name for the cylinder object (optional)
    """
    workspace = get_current_workspace()
    
    if name is None:
        name = f'cylinder_{len(workspace["objects"])}'
    
    if CADQUERY_AVAILABLE:
        # Create real CadQuery cylinder
        cylinder = cq.Workplane("XY").cylinder(height, radius)
        
        # Store in workspace
        workspace["objects"][name] = {
            'type': 'cylinder',
            'radius': radius,
            'height': height,
            'centered': centered,
            'workplane': cylinder
        }
        
        # Set as current object
        workspace["current_object"] = name
        
        # Export to STL
        stl_path = os.path.join(temp_dir, f"{name}.stl")
        exporters.export(cylinder, stl_path)
    else:
        # Mock implementation
        workspace["objects"][name] = {
            'type': 'cylinder',
            'radius': radius,
            'height': height,
            'centered': centered
        }
        
        workspace["current_object"] = name
        
        # Create a mock file path
        stl_path = os.path.join(temp_dir, f"{name}.stl")
        with open(stl_path, 'w') as f:
            f.write("Mock STL file content")
    
    return {
        "status": "success",
        "message": f"Created cylinder: {name}",
        "object_id": name,
        "dimensions": {
            "radius": radius,
            "height": height
        },
        "files": {
            "stl": stl_path
        }
    }

@mcp.tool()
def boolean_operation(operation: str, target: str, tool: str, name: str = None) -> dict:
    """Perform boolean operation between two objects
    
    Args:
        operation: Type of boolean operation ('union', 'subtract', 'intersect')
        target: Name of the target object
        tool: Name of the tool object
        name: Name for the resulting object (optional)
    """
    workspace = get_current_workspace()
    
    if target not in workspace["objects"]:
        return {
            "status": "error",
            "message": f"Target object '{target}' not found"
        }
    
    if tool not in workspace["objects"]:
        return {
            "status": "error",
            "message": f"Tool object '{tool}' not found"
        }
    
    if name is None:
        name = f'boolean_{len(workspace["objects"])}'
    
    if CADQUERY_AVAILABLE:
        target_obj = workspace["objects"][target]["workplane"]
        tool_obj = workspace["objects"][tool]["workplane"]
        
        if operation == "union":
            result = target_obj.union(tool_obj)
        elif operation == "subtract":
            result = target_obj.cut(tool_obj)
        elif operation == "intersect":
            result = target_obj.intersect(tool_obj)
        else:
            return {
                "status": "error",
                "message": f"Unknown boolean operation: {operation}"
            }
        
        # Store result
        workspace["objects"][name] = {
            'type': 'boolean',
            'operation': operation,
            'target': target,
            'tool': tool,
            'workplane': result
        }
        
        # Set as current object
        workspace["current_object"] = name
        
        # Export to STL
        stl_path = os.path.join(temp_dir, f"{name}.stl")
        exporters.export(result, stl_path)
    else:
        # Mock implementation
        workspace["objects"][name] = {
            'type': 'boolean',
            'operation': operation,
            'target': target,
            'tool': tool
        }
        
        workspace["current_object"] = name
        
        # Create a mock file path
        stl_path = os.path.join(temp_dir, f"{name}.stl")
        with open(stl_path, 'w') as f:
            f.write(f"Mock STL file for {operation} of {target} and {tool}")
    
    return {
        "status": "success",
        "message": f"Created {operation} between {target} and {tool}",
        "object_id": name,
        "files": {
            "stl": stl_path
        }
    }

@mcp.tool()
def render_current_object(ctx: Context) -> dict:
    """Render the current object and return an image
    
    This function renders the current object and returns a base64-encoded image.
    """
    workspace = get_current_workspace()
    
    if workspace["current_object"] is None:
        return {
            "status": "error",
            "message": "No current object selected"
        }
    
    obj_name = workspace["current_object"]
    
    if CADQUERY_AVAILABLE:
        try:
            # In a real implementation, you would render the object here
            # For simplicity, we're returning a mock image
            ctx.info(f"Rendering {obj_name}...")
            
            # For actual rendering, you might use something like this:
            # from cadquery import exporters
            # png_path = os.path.join(temp_dir, f"{obj_name}.png")
            # exporters.export(workspace["objects"][obj_name]["workplane"], png_path)
            
            # Mock image for now
            mock_image_path = os.path.join(temp_dir, f"{obj_name}.png")
            with open(mock_image_path, "w") as f:
                f.write("Mock PNG content")
            
            return {
                "status": "success",
                "message": f"Rendered {obj_name}",
                "object_id": obj_name,
                "files": {
                    "png": mock_image_path
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error rendering object: {str(e)}"
            }
    else:
        # Mock implementation
        mock_image_path = os.path.join(temp_dir, f"{obj_name}.png")
        with open(mock_image_path, "w") as f:
            f.write("Mock PNG content")
        
        return {
            "status": "success",
            "message": f"Rendered {obj_name} (mock)",
            "object_id": obj_name,
            "files": {
                "png": mock_image_path
            }
        }

@mcp.tool()
def export_object(name: str, format: str = "stl", validate: bool = True) -> dict:
    """Export an object to the specified format
    
    Args:
        name: Name of the object to export
        format: Export format (stl, step, stp)
        validate: Whether to validate the exported file (optional)
    """
    workspace = get_current_workspace()
    
    if name not in workspace["objects"]:
        return {
            "status": "error",
            "message": f"Object '{name}' not found"
        }
    
    # Normalize the format
    format = format.lower()
    
    # Handle special case for STEP files (both .step and .stp extensions)
    is_step_format = format in ["step", "stp"]
    extension = format
    
    if CADQUERY_AVAILABLE:
        obj = workspace["objects"][name]
        
        # Get the workplane
        workplane = obj.get("workplane")
        
        # Export to the requested format
        output_path = os.path.join(temp_dir, f"{name}.{extension}")
        
        try:
            if format == "stl":
                exporters.export(workplane, output_path)
            elif is_step_format:
                # Support both .step and .stp extensions for STEP format
                # Make sure we're exporting a solid (not a workplane)
                if hasattr(workplane, "val") and workplane.val and hasattr(workplane, "findSolid"):
                    solid = workplane.findSolid()
                    exporters.export(
                        solid, 
                        output_path, 
                        exporters.ExportTypes.STEP,
                        tolerance=0.001,  # Higher precision
                        angularTolerance=0.1  # Angular tolerance in degrees
                    )
                else:
                    # Default case for workplanes
                    exporters.export(
                        workplane, 
                        output_path, 
                        exporters.ExportTypes.STEP,
                        tolerance=0.001,
                        angularTolerance=0.1
                    )
                
                # Validate the file if requested
                if validate and is_step_format:
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        # Check if file is readable by reopening it
                        try:
                            with open(output_path, 'r') as f:
                                first_line = f.readline()
                                if not first_line or "ISO-10303" not in first_line:
                                    return {
                                        "status": "error",
                                        "message": f"Exported file does not appear to be a valid STEP file"
                                    }
                        except Exception as file_error:
                            return {
                                "status": "error",
                                "message": f"Exported file validation failed: {str(file_error)}"
                            }
                    else:
                        return {
                            "status": "error",
                            "message": f"Exported file is empty or wasn't created properly"
                        }
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported export format: {format}. Supported formats: stl, step, stp"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Export failed: {str(e)}"
            }
    else:
        # Mock implementation
        output_path = os.path.join(temp_dir, f"{name}.{extension}")
        with open(output_path, 'w') as f:
            if is_step_format:
                f.write(f"Mock STEP file content for {name}")
            else:
                f.write(f"Mock {format.upper()} file content for {name}")
    
    return {
        "status": "success",
        "message": f"Exported {name} to {extension} format",
        "object_id": name,
        "files": {
            extension: output_path
        }
    }

@mcp.tool()
def export_step(name: str, filepath: str = None) -> dict:
    """Export an object as STEP file
    
    Args:
        name: Name of the object to export
        filepath: Optional custom filepath (if not specified, uses temp directory)
    """
    workspace = get_current_workspace()
    
    if name not in workspace["objects"]:
        return {
            "status": "error",
            "message": f"Object '{name}' not found"
        }
    
    # Determine output path
    if filepath:
        # Ensure the filepath ends with .step or .stp
        if not (filepath.lower().endswith('.step') or filepath.lower().endswith('.stp')):
            filepath += '.step'
        output_path = filepath
    else:
        output_path = os.path.join(temp_dir, f"{name}.step")
    
    if CADQUERY_AVAILABLE:
        try:
            obj = workspace["objects"][name]
            workplane = obj.get("workplane")
            
            # Export to STEP format with more options
            # Make sure we're exporting a solid (not a workplane)
            if hasattr(workplane, "val") and workplane.val and hasattr(workplane, "findSolid"):
                solid = workplane.findSolid()
                exporters.export(
                    solid, 
                    output_path, 
                    exporters.ExportTypes.STEP,
                    tolerance=0.001,  # Higher precision for STEP export
                    angularTolerance=0.1  # Angular tolerance in degrees
                )
            else:
                # Default case for workplanes
                exporters.export(
                    workplane, 
                    output_path, 
                    exporters.ExportTypes.STEP,
                    tolerance=0.001,
                    angularTolerance=0.1
                )
            
            # Also create a preview STL file for visualization
            stl_path = os.path.join(temp_dir, f"{name}.stl")
            exporters.export(workplane, stl_path)
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"STEP export failed: {str(e)}"
            }
    else:
        # Mock implementation
        output_path = output_path or os.path.join(temp_dir, f"{name}.step")
        with open(output_path, 'w') as f:
            f.write(f"Mock STEP file content for {name}")
        
        # Mock STL file
        stl_path = os.path.join(temp_dir, f"{name}.stl")
        with open(stl_path, 'w') as f:
            f.write(f"Mock STL file content for {name}")
    
    return {
        "status": "success",
        "message": f"Exported {name} as STEP file",
        "object_id": name,
        "files": {
            "step": output_path,
            "stl": stl_path
        }
    }

@mcp.tool()
def execute_cq_script(script: str, name: str = None) -> dict:
    """Execute a CadQuery script and store the resulting object
    
    Args:
        script: CadQuery Python script to execute
        name: Name for the resulting object (optional)
    """
    workspace = get_current_workspace()
    
    if name is None:
        name = f'script_{len(workspace["objects"])}'
    
    if CADQUERY_AVAILABLE:
        try:
            # Create a local scope with CadQuery module
            local_scope = {"cq": cq}
            
            # Execute the script
            exec(script, {}, local_scope)
            
            # Get the result (assume it's stored in a variable called 'result')
            if "result" not in local_scope:
                return {
                    "status": "error",
                    "message": "Script must define a 'result' variable containing the CadQuery object"
                }
            
            result = local_scope["result"]
            
            # Store in workspace
            workspace["objects"][name] = {
                'type': 'script',
                'script': script,
                'workplane': result
            }
            
            # Set as current object
            workspace["current_object"] = name
            
            # Export to STL
            stl_path = os.path.join(temp_dir, f"{name}.stl")
            exporters.export(result, stl_path)
            
            return {
                "status": "success",
                "message": f"Created object from script: {name}",
                "object_id": name,
                "files": {
                    "stl": stl_path
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error executing script: {str(e)}"
            }
    else:
        # Mock implementation
        workspace["objects"][name] = {
            'type': 'script',
            'script': script
        }
        
        workspace["current_object"] = name
        
        # Create a mock file path
        stl_path = os.path.join(temp_dir, f"{name}.stl")
        with open(stl_path, 'w') as f:
            f.write("Mock STL file content from script")
        
        return {
            "status": "success",
            "message": f"Created object from script (mock): {name}",
            "object_id": name,
            "files": {
                "stl": stl_path
            }
        }

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')