# RUCKUS One (R1) Python SDK

A Python SDK for interacting with the RUCKUS One (R1) network management system.

## Features

- Comprehensive API coverage for RUCKUS One
- Intuitive, Pythonic interface
- Modular design for maintainability
- Error handling and logging
- OAuth2 authentication management

## Installation

Coming soon. For now, you can clone this repository:

```bash
git clone https://github.com/yourusername/ruckus-one-sdk.git
cd ruckus-one-sdk
pip install -e .
```

## Quick Start

```python
from ruckus_one import RuckusOneClient

# Initialize client with API credentials
client = RuckusOneClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tenant_id="your-tenant-id",
    region="na"  # "na", "eu", or "asia"
)

# Fetch all venues
venues = client.venues.list()
print(f"Found {len(venues['data'])} venues")

# Create a new venue
new_venue = client.venues.create(
    name="My New Venue",
    address={
        "street": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "zipCode": "94105",
        "country": "US"
    },
    description="A test venue",
    timezone="America/Los_Angeles"
)
print(f"Created venue: {new_venue['name']} with ID: {new_venue['id']}")

# Get APs in a venue
aps = client.aps.list(venue_id=new_venue['id'])
print(f"Found {len(aps['data'])} APs in venue {new_venue['name']}")
```

## Authentication

The SDK uses OAuth2 client credentials for authentication with the RUCKUS One API. You'll need:

1. Client ID
2. Client Secret
3. Tenant ID
4. Region (default is "na" for North America)

### Authentication Options

You have several options to provide these credentials:

#### 1. Direct in Code

```python
client = RuckusOneClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tenant_id="your-tenant-id",
    region="na"
)
```

#### 2. Environment Variables

```bash
export RUCKUS_API_REGION="na"
export RUCKUS_API_CLIENT_ID="your-client-id"
export RUCKUS_API_CLIENT_SECRET="your-client-secret"
export RUCKUS_API_TENANT_ID="your-tenant-id"
```

#### 3. Config File

You can create a `config.ini` file with your credentials:

```ini
[credentials]
client_id = your-client-id
client_secret = your-client-secret
tenant_id = your-tenant-id
region = na
```

Then load it in your code:

```python
import configparser
import os

def load_config(config_path="config.ini"):
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path)
        if 'credentials' in config:
            return {
                'client_id': config['credentials'].get('client_id'),
                'client_secret': config['credentials'].get('client_secret'),
                'tenant_id': config['credentials'].get('tenant_id'),
                'region': config['credentials'].get('region', 'na')
            }
    return {}

# Load config
config = load_config()

# Initialize client with config values
client = RuckusOneClient(
    client_id=config.get('client_id'),
    client_secret=config.get('client_secret'),
    tenant_id=config.get('tenant_id'),
    region=config.get('region', 'na')
)
```

## Modules

The SDK is organized into modules, each handling a specific aspect of the RUCKUS One API:

- **Venues**: Create and manage physical locations
- **AccessPoints**: Manage and monitor APs
- **Switches**: Manage and monitor switches
- **WLANs**: Create and configure wireless networks
- **VLANs**: Manage VLAN configurations
- **Clients**: Monitor client devices
- And more...

## CLI Tool

The SDK includes a command-line interface for common operations with two modes of operation:

### Command-Line Mode

In command-line mode, you execute individual commands directly:

```bash
# List venues
./bin/ruckus-cli venue list

# Get venue details
./bin/ruckus-cli venue get --id YOUR_VENUE_ID

# List APs in a venue
./bin/ruckus-cli ap list --venue-id YOUR_VENUE_ID

# Use a config file for authentication
./bin/ruckus-cli --config /path/to/config.ini venue list
```

### Interactive Mode (Network Switch-Like Interface)

Interactive mode provides a network switch-like experience with tab completion, command history, and "?" help:

```bash
# Start the interactive CLI
./bin/ruckus-cli --interactive
```

Once in interactive mode, you'll see a prompt where you can enter commands:

```
RUCKUS> authenticate --config /path/to/config.ini
RUCKUS> list_venues
RUCKUS> show_ap VENUE_ID SERIAL_NUMBER
```

Key features of interactive mode:
- Tab completion for commands and arguments
- Use "?" to get help on any command
- Built-in command history (use up/down arrows)
- Organized command categories
- Table-formatted output

Example interactive session:
```
RUCKUS> ?
Documented commands (use 'help -v' for verbose/'help <topic>' for details):

Access Point Commands
=====================
list_aps  show_ap

General Commands
===============
authenticate  help  history  quit  status

Switch Commands
=============
list_switches  show_switch

Venue Commands
=============
list_venues  show_venue

WLAN Commands
============
list_wlans  show_wlan

RUCKUS> authenticate --config config.ini
Successfully authenticated with RUCKUS One API
Region: na
Tenant ID: 95d4369d7134419ea680726ec84197b0

RUCKUS(na)> list_venues

Venues:
ID                                   | Name                           | City                 | Country   
----------------------------------------------------------------------------------------------------
8dae5704ae1043a19f620a5a44cded96    | US Test Venue                  | San Francisco        | US       
```

### CLI Authentication

You can provide authentication credentials to the CLI tool in three ways:

1. **Command-line arguments:**
   ```bash
   ./bin/ruckus-cli --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --tenant-id YOUR_TENANT_ID venue list
   ```

2. **Environment variables:**
   ```bash
   export RUCKUS_API_CLIENT_ID="your-client-id"
   export RUCKUS_API_CLIENT_SECRET="your-client-secret"
   export RUCKUS_API_TENANT_ID="your-tenant-id"
   ./bin/ruckus-cli venue list
   ```

3. **Config file:**
   ```bash
   ./bin/ruckus-cli --config /path/to/config.ini venue list
   ```

In interactive mode, you can authenticate with:
```
RUCKUS> authenticate --config /path/to/config.ini
```

The CLI tool will check for credentials in the following order:
1. Command-line arguments
2. Config file (if specified)
3. Environment variables

## Error Handling

The SDK provides custom exceptions for error handling:

```python
from ruckus_one.exceptions import ResourceNotFoundError, APIError

try:
    # Try to get a non-existent venue
    client.venues.get("non-existent-id")
except ResourceNotFoundError as e:
    print(f"Venue not found: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.