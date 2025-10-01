INTEGRATION_NAME = "Jamf"
INTEGRATION_DISPLAY_NAME = "Jamf"

# API ENDPOINTS
API_ENDPOINTS = {
    # Authentication
    "auth": "/api/v1/oauth/token",
    "invalidate_token": "/api/v1/auth/invalidate-token",
    # System information
    "jamf_pro_version": "/api/v1/jamf-pro-version",
    # Computer management
    "computer_groups": "/api/v1/computer-groups",
    "update_computer_group": "/JSSResource/computergroups/id/{id}",
    "computer_inventory_detail": "/api/v1/computers-inventory-detail/{id}",
    "device_group_membership": "/JSSResource/computergroups/id/{id}",
    "computers_inventory": "/api/v1/computers-inventory",
    "erase_computer": "/api/v1/computer-inventory/{id}/erase",
    "mdm_commands": "/api/v2/mdm/commands",
    "device_lock_pin": "/api/v1/computers-inventory/{id}/view-device-lock-pin",
    "computer_extension_attributes": "/JSSResource/computerextensionattributes",
}

# ACTION NAMES
PING_SCRIPT_NAME = f"{INTEGRATION_NAME} - Ping"
LIST_COMPUTER_GROUPS_SCRIPT_NAME = f"{INTEGRATION_NAME} - List Computer Groups"
GET_DEVICE_INFORMATION_SCRIPT_NAME = f"{INTEGRATION_NAME} - Get Device Information"
GET_DEVICE_GROUP_MEMBERSHIP_SCRIPT_NAME = f"{INTEGRATION_NAME} - Get Device Group Membership"
GET_COMPUTER_INVENTORY_SCRIPT_NAME = f"{INTEGRATION_NAME} - Get Computer Inventory"
WIPE_MANAGED_DEVICE_SCRIPT_NAME = f"{INTEGRATION_NAME} - Wipe Managed Device"
REMOTE_LOCK_MANAGED_DEVICE_SCRIPT_NAME = f"{INTEGRATION_NAME} - Remote Lock Managed Device"
ASSIGN_TO_GROUP_SCRIPT_NAME = f"{INTEGRATION_NAME} - Assign to Group"
UPDATE_EXTENSION_ATTRIBUTE_SCRIPT_NAME = f"{INTEGRATION_NAME} - Update Extension Attribute"

# CASE WALL TABLE NAMES
ENRICH_TABLE_NAME = "Jamf Report for: {}"

# HTTP HEADERS
VERSION = "1.0.0"
USER_AGENT = f"Jamf%20SOAR%20Integration/{VERSION} SecOps/Chronicle"

# ENRICHMENT PREFIX
ENRICH_PREFIX = "Jamf"
