import xmlrpc.client
import time
from datetime import datetime
import json

class OdooAPI:
    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=self._get_ssl_context())
        self.uid = self.common.authenticate(db, username, password, {})
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=self._get_ssl_context())

    def _get_ssl_context(self):
        import ssl
        context = ssl._create_unverified_context()
        return context

    def search(self, model, domain):
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'search', [domain])

    def read(self, model, ids, fields):
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'read', [ids], {'fields': fields})

    def search_read(self, model, domain, fields):
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'search_read', [domain], {'fields': fields})

    def create(self, model, data):
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'create', [data])

    def write(self, model, ids, data):
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'write', [ids, data])

    def unlink(self, model, ids):
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'unlink', [ids])

def extract_projects_and_tasks(odoo_api):
    print(f"Extracting data at {datetime.now()}")
    
    # Fetch all projects with additional fields
    projects = odoo_api.search_read('project.project', [['display_name', '!=', '']], 
                                    ['display_name', 'partner_id', 'user_id', 'date_start', 'x_studio_location_1'])
    
    all_data = []
    
    for project in projects:
        project_id = project['id']
        project_name = project['display_name']
        
        # Fetch tasks associated with the project
        tasks = odoo_api.search_read('project.task', [['project_id', '=', project_id]], 
                                     ['name', 'stage_id', 'date_deadline', 'priority', 'user_ids'])
        
        project_data = {
            'project_id': project_id,
            'project_name': project_name,
            'partner_id': project.get('partner_id'),
            'x_studio_location_1': project.get('x_studio_location_1'),
            'date_start': project.get('date_start'),
            'user_id': project.get('user_id'),
            'tasks': tasks
        }
        
        all_data.append(project_data)
    
    # Print the projects and their tasks
    for project in all_data:
        print(f"Project: {project['project_name']}")
        print(f"  Customer: {project.get('partner_id')}")
        print(f"  Location: {project.get('x_studio_location_1')}")
        print(f"  Date: {project.get('date_start')}")
        print(f"  Inspector: {project.get('user_id')}")
        for task in project['tasks']:
            print(f"  Task: {task['name']}, Stage: {task['stage_id']}, Deadline: {task.get('date_deadline')}, Priority: {task.get('priority')}, Assigned User: {task.get('user_ids')}")
    
    # Save data to a JSON file
    with open('projects_tasks_data.json', 'w') as f:
        json.dump(all_data, f, default=str)  # default=str to handle datetime serialization

if __name__ == "__main__":
    url = 'https://jfi-techniek-test-13644953.dev.odoo.com'
    db = 'jfi-techniek-test-13644953'
    username = 'info@novacheck.com'
    password = 'admin'  # Replace with your actual password

    odoo_api = OdooAPI(url, db, username, password)

    while True:
        extract_projects_and_tasks(odoo_api)
        # Sleep for an hour (3600 seconds)
        time.sleep(3600)
