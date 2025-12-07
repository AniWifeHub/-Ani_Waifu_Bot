import os
import json
from datetime import datetime

ownerc_file = "data/ownerc.json"

class OwnerC:
    @staticmethod
    def _initialize_file():
        """Initialize the data file with default structure"""
        default_data = {}
        os.makedirs(os.path.dirname(ownerc_file), exist_ok=True)
        with open(ownerc_file, 'w', encoding='utf-8') as file:
            json.dump(default_data, file, ensure_ascii=False, indent=4)
        return default_data

    @staticmethod
    def load():
        """Load data from JSON file"""
        try:
            with open(ownerc_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return OwnerC._initialize_file()

    @staticmethod
    def save(data):
        """Save data to JSON file"""
        os.makedirs(os.path.dirname(ownerc_file), exist_ok=True)
        with open(ownerc_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def add_admin(owner_id, admin_id, admin_name):
        """Add an admin to owner's admin list"""
        data = OwnerC.load()
        admin_id = str(admin_id)
        owner_id = str(owner_id)
        
        # Initialize owner entry if not exists
        if owner_id not in data:
            data[owner_id] = []
        
        # Check if admin already exists for this owner
        existing_admin = next((admin for admin in data[owner_id] if admin['id'] == admin_id), None)
        if existing_admin:
            # Update existing admin
            existing_admin.update({
                'name': admin_name,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            admin_data = existing_admin
        else:
            # Create new admin entry
            admin_data = {
                'owner_id': owner_id,
                'id': admin_id,
                'name': admin_name,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            data[owner_id].insert(0, admin_data)
        
        # Keep only the last 100 admins per owner
        data[owner_id] = data[owner_id][:100]
        OwnerC.save(data)
        return admin_data

    @staticmethod
    def remove_admin(owner_id, admin_id):
        """Remove an admin from owner's admin list"""
        data = OwnerC.load()
        admin_id = str(admin_id)
        owner_id = str(owner_id)
        
        if owner_id not in data:
            return False, "Owner not found"
        
        # Find and remove the admin
        initial_length = len(data[owner_id])
        data[owner_id] = [admin for admin in data[owner_id] if admin['id'] != admin_id]
        
        if len(data[owner_id]) < initial_length:
            OwnerC.save(data)
            return True, "Admin removed successfully"
        else:
            return False, "Admin not found for this owner"

    @staticmethod
    def list_admins(owner_id, limit=20):
        """Get list of admins for an owner"""
        data = OwnerC.load()
        owner_id = str(owner_id)
        
        if owner_id not in data or not data[owner_id]:
            return []
        
        # Return limited number of admins
        return data[owner_id][:limit]

    @staticmethod
    def get_admin(owner_id, admin_id):
        """Get specific admin information"""
        data = OwnerC.load()
        admin_id = str(admin_id)
        owner_id = str(owner_id)
        
        if owner_id not in data:
            return None
        
        return next((admin for admin in data[owner_id] if admin['id'] == admin_id), None)

    @staticmethod
    def is_admin(owner_id, admin_id):
        """Check if user is admin for given owner"""
        return OwnerC.get_admin(owner_id, admin_id) is not None

    @staticmethod
    def get_all_owners():
        """Get list of all owners in the system"""
        data = OwnerC.load()
        return list(data.keys())

    @staticmethod
    def get_owner_stats(owner_id):
        """Get statistics for an owner"""
        data = OwnerC.load()
        owner_id = str(owner_id)
        
        if owner_id not in data:
            return None
        
        admins = data[owner_id]
        return {
            'total_admins': len(admins),
            'latest_addition': admins[0]['date'] if admins else None,
            'owner_id': owner_id
        }

    @staticmethod
    def clear_owner_admins(owner_id):
        """Remove all admins for an owner"""
        data = OwnerC.load()
        owner_id = str(owner_id)
        
        if owner_id in data:
            removed_count = len(data[owner_id])
            data[owner_id] = []
            OwnerC.save(data)
            return True, f"Removed {removed_count} admins"
        return False, "Owner not found"

    @staticmethod
    def search_admins(owner_id, search_term):
        """Search admins by name for a specific owner"""
        data = OwnerC.load()
        owner_id = str(owner_id)
        
        if owner_id not in data:
            return []
        
        search_term = search_term.lower()
        return [admin for admin in data[owner_id] 
                if search_term in admin['name'].lower()]

    @staticmethod
    def format_admin_list(admins_list, title="Admins List"):
        """Format admin list for display"""
        if not admins_list:
            return f"📝 **{title}**\nNo admins found."
        
        formatted = f"📝 **{title}**\n\n"
        for i, admin in enumerate(admins_list, 1):
            formatted += f"{i}. **{admin['name']}** (ID: `{admin['id']}`)\n"
            formatted += f"   📅 Added: {admin['date']}\n\n"
        
        return formatted

# # Usage examples:
# if __name__ == "__main__":
#     # Add admin
#     admin = OwnerC.add_admin("123", "456", "John Doe")
#     print(f"Added admin: {admin}")
    
#     # List admins
#     admins = OwnerC.list_admins("123")
#     print(f"Admins: {admins}")
    
#     # Check if admin exists
#     is_admin = OwnerC.is_admin("123", "456")
#     print(f"Is admin: {is_admin}")
    
#     # Remove admin
#     success, message = OwnerC.remove_admin("123", "456")
#     print(f"Remove result: {success}, {message}")
    
#     # Get formatted list
#     OwnerC.add_admin("123", "789", "Jane Smith")
#     admins = OwnerC.list_admins("123")
#     print(OwnerC.format_admin_list(admins))