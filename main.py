from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from tinydb import TinyDB, Query

# --- Pydantic Models ---

class Node(BaseModel):
    id: int
    label: str
    parentId: Optional[int] = None
    children: List['Node'] = []

Node.model_rebuild()

class NodeCreate(BaseModel):
    label: str
    parentId: Optional[int] = None

app = FastAPI(
    title="SNH Tree Data API",
    description="A simple API to manage tree data structures.",
    version="1.0.0",
)
db = TinyDB('db.json')
nodes_table = db.table('nodes')

# --- Helper function to build tree ---
def build_tree_from_nodes(nodes: List[dict]) -> List[Node]:
    """
    Turns a flat list of nodes from the database into a nested and validated tree structure.
    """
    # Create a dictionary of nodes for easy lookup
    node_map = {node['id']: Node(**node, children=[]) for node in nodes}

    # This list holds the final tree / forest
    forest = []
    for node in node_map.values():
        if node.parentId and node.parentId in node_map:
            # child node -> find its parent and append it
            parent_node = node_map[node.parentId]
            parent_node.children.append(node)
        else:
            # root node (no parent or parent not found) -> add to the forest
            forest.append(node)
    
    return forest


# --- API Endpoints ---

@app.get("/api/tree", response_model=List[Node], summary="Get All Trees")
def get_trees():
    """
    Gets all nodes from the database and returns as an array of trees
    the response is an array of root nodes that each contain their own nested children
    """
    all_nodes = nodes_table.all()
    if not all_nodes:
        return []
    
    # reconstruct the flat structure into a tree structure for the response
    tree_structure = build_tree_from_nodes(all_nodes)
    return tree_structure

@app.post("/api/tree", response_model=Node, status_code=status.HTTP_201_CREATED, summary="Create a New Node")
def create_node(node: NodeCreate):
    """
    Creates a new node
    - omit parentId to create a root node
    - include parentId of an existing node to create a child node
    """
    # If parent id provided then check it's a valid & existing node
    if node.parentId is not None:
        parent_node = nodes_table.get(doc_id=node.parentId)
        if not parent_node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent node with id {node.parentId} not found"
            )

    # Convert pydantic model to a dict to store in tinydb
    new_node_data = node.model_dump()
    # Insert the new node and get its generated ID
    node_id = nodes_table.insert(new_node_data)
    # Update the node in DB with its own ID for consistency
    nodes_table.update({'id': node_id}, doc_ids=[node_id])
    # Get the final created node from the database to return
    created_node_data = nodes_table.get(doc_id=node_id)

    return created_node_data

