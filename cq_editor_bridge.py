# cq_editor_bridge.py
import os
import sys
import tempfile
import json
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, Callable

class CQEditorBridge:
    """Bridge class to communicate with cq-editor"""
    
    def __init__(self, temp_dir: str = None, get_workspace_func: Callable = None):
        """Initialize the CQ-Editor bridge
        
        Args:
            temp_dir: Optional temporary directory for files
            get_workspace_func: Function to get the current workspace
        """
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="cadquery_mcp_")
        self.cq_editor_process = None
        self.script_file = os.path.join(self.temp_dir, "current_script.py")
        self.model_file = os.path.join(self.temp_dir, "current_model.step")
        self.screenshots_dir = os.path.join(self.temp_dir, "screenshots")
        self.get_workspace = get_workspace_func
        
        # Create directories
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Create empty script file
        with open(self.script_file, 'w') as f:
            f.write("import cadquery as cq\n\n# Initial empty script\nresult = cq.Workplane('XY')")
    
    def start_cq_editor(self) -> bool:
        """Start CQ-Editor as a subprocess
        
        Returns:
            bool: True if successfully started, False otherwise
        """
        if self.cq_editor_process and self.cq_editor_process.poll() is None:
            # Already running
            return True
        
        try:
            # Define potential paths for CQ-Editor
            potential_paths = [
                "cq-editor",  # Default in PATH
                os.path.join(sys.exec_prefix, 'Scripts', 'cq-editor.exe'),  # Windows conda/pip install
                os.path.join(sys.exec_prefix, 'python.exe'),  # Python executable for module approach
                r"C:\Users\Senthil\miniconda3\envs\cadquery\python.exe",  # Your specific environment
            ]
            
            # Try each path
            for path in potential_paths:
                try:
                    if path.endswith('python.exe'):
                        # Use module approach for Python executable
                        self.cq_editor_process = subprocess.Popen(
                            [path, "-m", "cq_editor"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                    else:
                        # Direct executable approach
                        self.cq_editor_process = subprocess.Popen(
                            [path, self.script_file],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                    
                    # Wait a bit to ensure it starts properly
                    time.sleep(2)
                    
                    if self.cq_editor_process.poll() is None:
                        # Process is running
                        print(f"Successfully launched CQ-Editor using: {path}")
                        return True
                    else:
                        # Process failed to start, try next path
                        print(f"Failed to launch with {path}, exit code: {self.cq_editor_process.returncode}")
                        stderr = self.cq_editor_process.stderr.read()
                        if stderr:
                            print(f"Error output: {stderr}")
                except Exception as e:
                    print(f"Error trying path {path}: {str(e)}")
                    continue
            
            # If we get here, all paths failed
            print("All attempts to launch CQ-Editor failed")
            return False
                
        except Exception as e:
            print(f"Unexpected error starting cq-editor: {str(e)}")
            return False
    
    def stop_cq_editor(self) -> bool:
        """Stop the CQ-Editor process
        
        Returns:
            bool: True if successfully stopped, False otherwise
        """
        if not self.cq_editor_process:
            return True
            
        try:
            self.cq_editor_process.terminate()
            self.cq_editor_process.wait(timeout=5)
            return True
        except Exception as e:
            print(f"Error stopping cq-editor: {str(e)}")
            try:
                self.cq_editor_process.kill()
            except:
                pass
            return False
    
    def update_script(self, script_content: str) -> bool:
        """Update the script file that CQ-Editor is using
        
        Args:
            script_content: CadQuery Python script content
            
        Returns:
            bool: True if successfully updated, False otherwise
        """
        try:
            with open(self.script_file, 'w') as f:
                f.write(script_content)
            return True
        except Exception as e:
            print(f"Error updating script: {str(e)}")
            return False
    
    def get_screenshot(self) -> str:
        """Take a screenshot of CQ-Editor (mock implementation)
        
        In a real implementation, you would use a library like PyAutoGUI to take
        a screenshot of the CQ-Editor window.
        
        Returns:
            str: Path to the screenshot image
        """
        # Mock implementation - in reality you'd use something like:
        # import pyautogui
        # screenshot = pyautogui.screenshot("window_title='CadQuery Editor'")
        
        # For now, we'll just create a simple text file as a placeholder
        timestamp = int(time.time())
        screenshot_path = os.path.join(self.screenshots_dir, f"screenshot_{timestamp}.png")
        
        # In a real implementation, you'd save an actual screenshot here
        with open(screenshot_path, 'w') as f:
            f.write("Mock screenshot file")
        
        return screenshot_path
    
    def save_model(self, object_data: Any, name: str) -> str:
        """Save a CadQuery model to a file
        
        Args:
            object_data: CadQuery object data
            name: Name for the model file
            
        Returns:
            str: Path to the saved model file, or empty string on failure
        """
        try:
            if not hasattr(object_data, "exportStep"):
                print("Object doesn't support STEP export")
                return ""
                
            # Save as STEP
            step_file = os.path.join(self.temp_dir, f"{name}.step")
            object_data.exportStep(step_file)
            
            # Also save as STL for compatibility
            stl_file = os.path.join(self.temp_dir, f"{name}.stl")
            object_data.exportStl(stl_file)
            
            return step_file
        except Exception as e:
            print(f"Error saving model: {str(e)}")
            return ""

# Example of using the bridge from your MCP server
def integrate_with_mcp_server(mcp, get_workspace_func):
    """
    Example of how to integrate the bridge with your MCP server
    
    Args:
        mcp: The FastMCP server instance
        get_workspace_func: Function to get the current workspace
    """
    # Create a new temp directory
    temp_dir = tempfile.mkdtemp(prefix="cadquery_mcp_")
    
    # Initialize the bridge
    bridge = CQEditorBridge(temp_dir=temp_dir, get_workspace_func=get_workspace_func)

    @mcp.tool()
    def diagnose_cq_editor() -> dict:
        """Diagnose CQ-Editor installation and find path"""
        results = {
            "python_executable": sys.executable,
            "conda_environment": os.environ.get("CONDA_DEFAULT_ENV", "None"),
            "searched_paths": []
        }
        
        # Search for cq-editor in common locations
        search_paths = [
            os.path.join(sys.exec_prefix, 'Scripts'),
            os.path.join(sys.exec_prefix, 'bin'),
            r"C:\Users\Senthil\miniconda3\envs\cadquery\Scripts",
        ]
        
        for dir_path in search_paths:
            results["searched_paths"].append({"path": dir_path, "exists": os.path.exists(dir_path)})
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    if "cq" in file.lower() and "editor" in file.lower():
                        results["searched_paths"].append(f"Found: {os.path.join(dir_path, file)}")
        
        # Try to find the module
        try:
            import importlib.util
            cq_editor_spec = importlib.util.find_spec("cq_editor")
            if cq_editor_spec:
                results["cq_editor_module"] = cq_editor_spec.origin
        except:
            results["cq_editor_module"] = "Error finding module"
        
        return results
    
    @mcp.tool()
    def launch_cq_editor() -> dict:
        """Launch the CadQuery Editor UI"""
        success = bridge.start_cq_editor()
        
        if success:
            return {
                "status": "success",
                "message": "CadQuery Editor launched successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to launch CadQuery Editor"
            }
    
    @mcp.tool()
    def close_cq_editor() -> dict:
        """Close the CadQuery Editor UI"""
        success = bridge.stop_cq_editor()
        
        if success:
            return {
                "status": "success",
                "message": "CadQuery Editor closed successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to close CadQuery Editor"
            }
    
    @mcp.tool()
    def update_cq_script(script: str) -> dict:
        """Update the script in CadQuery Editor
        
        Args:
            script: CadQuery Python script content
        """
        success = bridge.update_script(script)
        
        if success:
            return {
                "status": "success",
                "message": "Script updated in CadQuery Editor",
                "script_file": bridge.script_file
            }
        else:
            return {
                "status": "error",
                "message": "Failed to update script in CadQuery Editor"
            }
    
    @mcp.tool()
    def sync_object_from_editor(name: str = None) -> dict:
        """Sync the current object from CQ-Editor to the MCP server
        
        This retrieves the current model from CQ-Editor and stores it in the workspace.
        
        Args:
            name: Optional name for the synced object
        """
        if bridge.get_workspace is None:
            return {
                "status": "error",
                "message": "Workspace management function not provided to bridge"
            }
            
        workspace = bridge.get_workspace()
        
        if name is None:
            name = f'synced_{len(workspace["objects"])}'
        
        try:
            # In a real implementation, you would need a way to communicate with CQ-Editor
            # to retrieve the current model. This is a simplified mock implementation.
            
            # Read the current script
            with open(bridge.script_file, 'r') as f:
                script = f.read()
            
            # Here you would execute the script to get the result
            # This is a simplified example - in reality you'd need to handle
            # this in a way that fits your application architecture
            
            return {
                "status": "success",
                "message": f"Synced object from CQ-Editor: {name}",
                "object_id": name,
                "script": script
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error syncing from CQ-Editor: {str(e)}"
            }
            
    # Return the bridge for further use
    return bridge