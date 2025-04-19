# CadQuery MCP Server

A Model-Code-Parameter (MCP) server implementation for [CadQuery](https://github.com/CadQuery/cadquery), providing a bridge between CadQuery's parametric 3D modeling capabilities and a server architecture for programmatic control.


## Overview

CadQuery MCP is a server that enables interaction with [CadQuery](https://github.com/CadQuery/cadquery) through a standardized API, allowing remote control of 3D modeling operations. It leverages the Model-Code-Parameter (MCP) architecture to provide a consistent interface for CAD operations.

#### Demo

![demo](./assets/demo.mp4)

**Key Features:**
- Create and manage multiple workspaces for organizing models
- Create primitive shapes (boxes, cylinders, spheres)
- Perform boolean operations (union, subtract, intersect)
- Apply fillets and chamfers to edges
- Export models to various formats (STL, STEP)
- Execute arbitrary CadQuery scripts
- Integration with CQ-Editor for visual feedback

## Installation

### Prerequisites
- Python 3.7+
- CadQuery: `pip install cadquery`
- FastMCP: `pip install mcp`

### Installation steps

```bash
# Clone the repository
git clone https://github.com/yourusername/cadquery-mcp.git
cd cadquery-mcp


```

## Configuration
```json
{
    "mcpServers": {
        "freecad": {
            "command": "C:/Users/--/envs/cadquery/python.exe",
            "args": [
                ":/--/cadquery_fastmcp.py"
            ]
        }
    }
}
```




## Architecture

The CadQuery MCP server consists of two main components:

1. **CadQuery MCP Server** (`cadquery_fastmcp.py`): 
   - Main server implementation that exposes CadQuery functionality
   - Manages workspaces and objects
   - Handles import/export operations

2. **CQ-Editor Bridge** (`cq_editor_bridge.py`): 
   - Bridge to integrate with CQ-Editor for visual editing
   - Manages the CQ-Editor process
   - Synchronizes objects between the server and the editor


### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



## Acknowledgments

- Built with [CadQuery](https://github.com/CadQuery/cadquery) and FastMCP