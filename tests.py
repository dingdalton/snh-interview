import unittest
import os
from fastapi.testclient import TestClient
from main import app, db, nodes_table

# Use the TestClient for making requests to the FastAPI app in tests
client = TestClient(app)

class TreeApiTestCase(unittest.TestCase):
    """This class represents the test case for the Tree API."""

    def setUp(self):
        """Define test variables and initialize app."""
        nodes_table.truncate()

    def tearDown(self):
        """Executed after each test."""
        if os.path.exists('db.json'):
            db.truncate()

    def test_get_empty_tree(self):
        """Test GET request on an empty database returns an empty list."""
        res = client.get('/api/tree')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])

    def test_post_create_root_node(self):
        """Test API can create a root node (POST request)."""
        payload = {"label": "root"}
        res = client.post('/api/tree', json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data['label'], 'root')
        self.assertIsNone(data['parentId'])
        self.assertIn('id', data)

    def test_post_create_child_node(self):
        """Test API can create a child node attached to a parent."""
        # First, create a parent node to attach the child to
        parent_payload = {"label": "parent"}
        parent_res = client.post('/api/tree', json=parent_payload)
        self.assertEqual(parent_res.status_code, 201)
        parent_data = parent_res.json()
        parent_id = parent_data['id']

        # Now, create the child node
        child_payload = {"label": "child", "parentId": parent_id}
        child_res = client.post('/api/tree', json=child_payload)
        self.assertEqual(child_res.status_code, 201)
        child_data = child_res.json()
        self.assertEqual(child_data['label'], 'child')
        self.assertEqual(child_data['parentId'], parent_id)

    def test_post_create_child_with_nonexistent_parent(self):
        """Test API returns 404 for a non-existent parent ID."""
        payload = {"label": "orphan", "parentId": 9999}
        res = client.post('/api/tree', json=payload)
        self.assertEqual(res.status_code, 404)

    def test_get_full_tree_structure(self):
        """Test API can fetch the full nested tree structure (GET request)."""
        # 1. Create root node
        root_res = client.post('/api/tree', json={"label": "root"})
        root_id = root_res.json()['id']

        # 2. Create a child of root
        child_res = client.post('/api/tree', json={"label": "child1", "parentId": root_id})
        child_id = child_res.json()['id']

        # 3. Create a grandchild
        client.post('/api/tree', json={"label": "grandchild", "parentId": child_id})
        
        # 4. Create a second, separate root node
        client.post('/api/tree', json={"label": "root2"})

        # 5. Get the full tree structure
        res = client.get('/api/tree')
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Assertions to check the structure of the returned "forest"
        self.assertEqual(len(data), 2, "Should be two root nodes in the forest")
        
        # Check first tree
        root1 = data[0] if data[0]['label'] == 'root' else data[1]
        self.assertEqual(root1['label'], 'root')
        self.assertEqual(len(root1['children']), 1)
        self.assertEqual(root1['children'][0]['label'], 'child1')
        self.assertEqual(len(root1['children'][0]['children']), 1)
        self.assertEqual(root1['children'][0]['children'][0]['label'], 'grandchild')
        
        # Check second tree
        root2 = data[0] if data[0]['label'] == 'root2' else data[1]
        self.assertEqual(root2['label'], 'root2')
        self.assertEqual(len(root2['children']), 0)


# Make the tests executable
if __name__ == "__main__":
    unittest.main()

