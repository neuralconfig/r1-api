"""
Main CLI entry point for the RUCKUS One SDK.
"""

import argparse
import json
import os
import sys
import logging
import configparser
from typing import Dict, Any, Optional

from .. import __version__
from ..client import RuckusOneClient
from ..exceptions import APIError, AuthenticationError


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def load_config(config_path: str) -> Dict[str, str]:
    """
    Load configuration from a config.ini file.
    
    Args:
        config_path: Path to the config.ini file
        
    Returns:
        Dictionary with configuration values
    """
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


def get_client(args: argparse.Namespace) -> RuckusOneClient:
    """
    Create a RUCKUS One client from command-line arguments, config file, or environment variables.
    
    Args:
        args: Command-line arguments
        
    Returns:
        RuckusOneClient instance
    
    Raises:
        AuthenticationError: If authentication fails
    """
    # Load config from file if specified
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Get credentials from arguments, config file, or environment variables (in that order)
    region = args.region or config.get('region') or os.environ.get('RUCKUS_API_REGION', 'na')
    client_id = args.client_id or config.get('client_id') or os.environ.get('RUCKUS_API_CLIENT_ID')
    client_secret = args.client_secret or config.get('client_secret') or os.environ.get('RUCKUS_API_CLIENT_SECRET')
    tenant_id = args.tenant_id or config.get('tenant_id') or os.environ.get('RUCKUS_API_TENANT_ID')
    
    if not client_id:
        raise AuthenticationError("Client ID is required (--client-id, config file, or RUCKUS_API_CLIENT_ID)")
    if not client_secret:
        raise AuthenticationError("Client Secret is required (--client-secret, config file, or RUCKUS_API_CLIENT_SECRET)")
    if not tenant_id:
        raise AuthenticationError("Tenant ID is required (--tenant-id, config file, or RUCKUS_API_TENANT_ID)")
    
    # Create and return client
    return RuckusOneClient(
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id,
        region=region
    )


def handle_venue_commands(args: argparse.Namespace, client: RuckusOneClient) -> Any:
    """
    Handle venue-related commands.
    
    Args:
        args: Command-line arguments
        client: RuckusOneClient instance
        
    Returns:
        Command result
    """
    if args.venue_command == 'list':
        # List venues
        return client.venues.list(
            search_string=args.search,
            page_size=args.page_size,
            page=args.page
        )
    elif args.venue_command == 'get':
        # Get venue details
        if not args.id:
            raise ValueError("Venue ID is required for 'get' command")
        return client.venues.get(args.id)
    elif args.venue_command == 'create':
        # Create venue
        if not args.name:
            raise ValueError("Venue name is required for 'create' command")
        if not args.address:
            raise ValueError("Venue address is required for 'create' command")
        
        # Parse address as JSON
        try:
            address = json.loads(args.address)
        except json.JSONDecodeError:
            raise ValueError("Address must be valid JSON")
        
        return client.venues.create(
            name=args.name,
            address=address,
            description=args.description,
            timezone=args.timezone
        )
    elif args.venue_command == 'update':
        # Update venue
        if not args.id:
            raise ValueError("Venue ID is required for 'update' command")
            
        # Parse properties as JSON
        props = {}
        if args.properties:
            try:
                props = json.loads(args.properties)
            except json.JSONDecodeError:
                raise ValueError("Properties must be valid JSON")
                
        return client.venues.update(args.id, **props)
    elif args.venue_command == 'delete':
        # Delete venue
        if not args.id:
            raise ValueError("Venue ID is required for 'delete' command")
        client.venues.delete(args.id)
        return {"message": f"Venue {args.id} deleted successfully"}


def handle_ap_commands(args: argparse.Namespace, client: RuckusOneClient) -> Any:
    """
    Handle AP-related commands.
    
    Args:
        args: Command-line arguments
        client: RuckusOneClient instance
        
    Returns:
        Command result
    """
    if args.ap_command == 'list':
        # List APs
        filters = {}
        if args.venue_id:
            filters["venueId"] = args.venue_id
            
        return client.aps.list(
            search_string=args.search,
            page_size=args.page_size,
            page=args.page,
            **filters
        )
    elif args.ap_command == 'get':
        # Get AP details
        if not args.venue_id:
            raise ValueError("Venue ID is required for 'get' command")
        if not args.serial:
            raise ValueError("AP serial number is required for 'get' command")
        return client.aps.get(args.venue_id, args.serial)
    elif args.ap_command == 'update':
        # Update AP
        if not args.venue_id:
            raise ValueError("Venue ID is required for 'update' command")
        if not args.serial:
            raise ValueError("AP serial number is required for 'update' command")
            
        # Parse properties as JSON
        props = {}
        if args.properties:
            try:
                props = json.loads(args.properties)
            except json.JSONDecodeError:
                raise ValueError("Properties must be valid JSON")
                
        return client.aps.update(args.venue_id, args.serial, **props)
    elif args.ap_command == 'reboot':
        # Reboot AP
        if not args.venue_id:
            raise ValueError("Venue ID is required for 'reboot' command")
        if not args.serial:
            raise ValueError("AP serial number is required for 'reboot' command")
        return client.aps.reboot(args.venue_id, args.serial)


def handle_wlan_commands(args: argparse.Namespace, client: RuckusOneClient) -> Any:
    """
    Handle WLAN-related commands.
    
    Args:
        args: Command-line arguments
        client: RuckusOneClient instance
        
    Returns:
        Command result
    """
    if args.wlan_command == 'list':
        # List WLANs
        return client.wlans.list(
            search_string=args.search,
            page_size=args.page_size,
            page=args.page
        )
    elif args.wlan_command == 'get':
        # Get WLAN details
        if not args.id:
            raise ValueError("WLAN ID is required for 'get' command")
        return client.wlans.get(args.id)
    elif args.wlan_command == 'create':
        # Create WLAN
        if not args.name:
            raise ValueError("WLAN name is required for 'create' command")
        if not args.ssid:
            raise ValueError("SSID is required for 'create' command")
        if not args.security_type:
            raise ValueError("Security type is required for 'create' command")
            
        return client.wlans.create(
            name=args.name,
            ssid=args.ssid,
            security_type=args.security_type,
            vlan_id=args.vlan_id,
            hidden=args.hidden,
            description=args.description
        )
    elif args.wlan_command == 'update':
        # Update WLAN
        if not args.id:
            raise ValueError("WLAN ID is required for 'update' command")
            
        # Parse properties as JSON
        props = {}
        if args.properties:
            try:
                props = json.loads(args.properties)
            except json.JSONDecodeError:
                raise ValueError("Properties must be valid JSON")
                
        return client.wlans.update(args.id, **props)
    elif args.wlan_command == 'delete':
        # Delete WLAN
        if not args.id:
            raise ValueError("WLAN ID is required for 'delete' command")
        client.wlans.delete(args.id)
        return {"message": f"WLAN {args.id} deleted successfully"}
    elif args.wlan_command == 'deploy':
        # Deploy WLAN to venue
        if not args.id:
            raise ValueError("WLAN ID is required for 'deploy' command")
        if not args.venue_id:
            raise ValueError("Venue ID is required for 'deploy' command")
            
        return client.wlans.deploy_to_venue(
            wlan_id=args.id,
            venue_id=args.venue_id,
            ap_group_id=args.ap_group_id
        )
    elif args.wlan_command == 'undeploy':
        # Undeploy WLAN from venue
        if not args.id:
            raise ValueError("WLAN ID is required for 'undeploy' command")
        if not args.venue_id:
            raise ValueError("Venue ID is required for 'undeploy' command")
            
        client.wlans.undeploy_from_venue(
            wlan_id=args.id,
            venue_id=args.venue_id,
            ap_group_id=args.ap_group_id
        )
        return {"message": f"WLAN {args.id} undeployed from venue {args.venue_id}"}


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='RUCKUS One CLI')
    
    # Global arguments
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--config', '-c', help='Path to config.ini file')
    parser.add_argument('--region', help='RUCKUS One API region (na, eu, asia)')
    parser.add_argument('--client-id', help='RUCKUS One OAuth2 client ID')
    parser.add_argument('--client-secret', help='RUCKUS One OAuth2 client secret')
    parser.add_argument('--tenant-id', help='RUCKUS One tenant ID')
    parser.add_argument('--output', '-o', choices=['json', 'table'], default='json',
                       help='Output format (default: json)')
    
    # Create subparsers for different command groups
    subparsers = parser.add_subparsers(dest='command', help='Command group')
    
    # Venue commands
    venue_parser = subparsers.add_parser('venue', help='Venue commands')
    venue_subparsers = venue_parser.add_subparsers(dest='venue_command', help='Venue command')
    
    # Venue list command
    venue_list_parser = venue_subparsers.add_parser('list', help='List venues')
    venue_list_parser.add_argument('--search', help='Search string')
    venue_list_parser.add_argument('--page-size', type=int, default=10, help='Page size')
    venue_list_parser.add_argument('--page', type=int, default=0, help='Page number')
    
    # Venue get command
    venue_get_parser = venue_subparsers.add_parser('get', help='Get venue details')
    venue_get_parser.add_argument('--id', required=True, help='Venue ID')
    
    # Venue create command
    venue_create_parser = venue_subparsers.add_parser('create', help='Create a new venue')
    venue_create_parser.add_argument('--name', required=True, help='Venue name')
    venue_create_parser.add_argument('--address', required=True, 
                                   help='Venue address as JSON')
    venue_create_parser.add_argument('--description', help='Venue description')
    venue_create_parser.add_argument('--timezone', help='Venue timezone')
    
    # Venue update command
    venue_update_parser = venue_subparsers.add_parser('update', help='Update a venue')
    venue_update_parser.add_argument('--id', required=True, help='Venue ID')
    venue_update_parser.add_argument('--properties', required=True, 
                                   help='Properties to update as JSON')
    
    # Venue delete command
    venue_delete_parser = venue_subparsers.add_parser('delete', help='Delete a venue')
    venue_delete_parser.add_argument('--id', required=True, help='Venue ID')
    
    # AP commands
    ap_parser = subparsers.add_parser('ap', help='AP commands')
    ap_subparsers = ap_parser.add_subparsers(dest='ap_command', help='AP command')
    
    # AP list command
    ap_list_parser = ap_subparsers.add_parser('list', help='List APs')
    ap_list_parser.add_argument('--venue-id', help='Venue ID')
    ap_list_parser.add_argument('--search', help='Search string')
    ap_list_parser.add_argument('--page-size', type=int, default=10, help='Page size')
    ap_list_parser.add_argument('--page', type=int, default=0, help='Page number')
    
    # AP get command
    ap_get_parser = ap_subparsers.add_parser('get', help='Get AP details')
    ap_get_parser.add_argument('--venue-id', required=True, help='Venue ID')
    ap_get_parser.add_argument('--serial', required=True, help='AP serial number')
    
    # AP update command
    ap_update_parser = ap_subparsers.add_parser('update', help='Update an AP')
    ap_update_parser.add_argument('--venue-id', required=True, help='Venue ID')
    ap_update_parser.add_argument('--serial', required=True, help='AP serial number')
    ap_update_parser.add_argument('--properties', required=True, 
                                help='Properties to update as JSON')
    
    # AP reboot command
    ap_reboot_parser = ap_subparsers.add_parser('reboot', help='Reboot an AP')
    ap_reboot_parser.add_argument('--venue-id', required=True, help='Venue ID')
    ap_reboot_parser.add_argument('--serial', required=True, help='AP serial number')
    
    # WLAN commands
    wlan_parser = subparsers.add_parser('wlan', help='WLAN commands')
    wlan_subparsers = wlan_parser.add_subparsers(dest='wlan_command', help='WLAN command')
    
    # WLAN list command
    wlan_list_parser = wlan_subparsers.add_parser('list', help='List WLANs')
    wlan_list_parser.add_argument('--search', help='Search string')
    wlan_list_parser.add_argument('--page-size', type=int, default=10, help='Page size')
    wlan_list_parser.add_argument('--page', type=int, default=0, help='Page number')
    
    # WLAN get command
    wlan_get_parser = wlan_subparsers.add_parser('get', help='Get WLAN details')
    wlan_get_parser.add_argument('--id', required=True, help='WLAN ID')
    
    # WLAN create command
    wlan_create_parser = wlan_subparsers.add_parser('create', help='Create a new WLAN')
    wlan_create_parser.add_argument('--name', required=True, help='WLAN name')
    wlan_create_parser.add_argument('--ssid', required=True, help='SSID')
    wlan_create_parser.add_argument('--security-type', required=True, 
                                  help='Security type')
    wlan_create_parser.add_argument('--vlan-id', type=int, help='VLAN ID')
    wlan_create_parser.add_argument('--hidden', action='store_true', 
                                  help='Hide SSID')
    wlan_create_parser.add_argument('--description', help='WLAN description')
    
    # WLAN update command
    wlan_update_parser = wlan_subparsers.add_parser('update', help='Update a WLAN')
    wlan_update_parser.add_argument('--id', required=True, help='WLAN ID')
    wlan_update_parser.add_argument('--properties', required=True, 
                                  help='Properties to update as JSON')
    
    # WLAN delete command
    wlan_delete_parser = wlan_subparsers.add_parser('delete', help='Delete a WLAN')
    wlan_delete_parser.add_argument('--id', required=True, help='WLAN ID')
    
    # WLAN deploy command
    wlan_deploy_parser = wlan_subparsers.add_parser('deploy', 
                                                 help='Deploy WLAN to venue')
    wlan_deploy_parser.add_argument('--id', required=True, help='WLAN ID')
    wlan_deploy_parser.add_argument('--venue-id', required=True, help='Venue ID')
    wlan_deploy_parser.add_argument('--ap-group-id', help='AP group ID')
    
    # WLAN undeploy command
    wlan_undeploy_parser = wlan_subparsers.add_parser('undeploy', 
                                                   help='Undeploy WLAN from venue')
    wlan_undeploy_parser.add_argument('--id', required=True, help='WLAN ID')
    wlan_undeploy_parser.add_argument('--venue-id', required=True, help='Venue ID')
    wlan_undeploy_parser.add_argument('--ap-group-id', help='AP group ID')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # If no command specified, print help and exit
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    try:
        # Create client
        client = get_client(args)
        
        # Handle commands
        result = None
        if args.command == 'venue' and args.venue_command:
            result = handle_venue_commands(args, client)
        elif args.command == 'ap' and args.ap_command:
            result = handle_ap_commands(args, client)
        elif args.command == 'wlan' and args.wlan_command:
            result = handle_wlan_commands(args, client)
        else:
            # Subcommand missing
            if args.command == 'venue':
                venue_parser.print_help()
            elif args.command == 'ap':
                ap_parser.print_help()
            elif args.command == 'wlan':
                wlan_parser.print_help()
            sys.exit(1)
            
        # Output result
        if result:
            if args.output == 'json':
                print(json.dumps(result, indent=2))
            elif args.output == 'table':
                # Simple table output (just for example)
                if isinstance(result, dict) and 'data' in result and isinstance(result['data'], list):
                    # Print data items as table
                    data = result['data']
                    if data:
                        # Get keys from first item
                        keys = data[0].keys()
                        # Print header
                        print(' | '.join(keys))
                        print('-' * 80)
                        # Print rows
                        for item in data:
                            print(' | '.join(str(item.get(k, '')) for k in keys))
                else:
                    # Just print as JSON for non-tabular data
                    print(json.dumps(result, indent=2))
                    
    except APIError as e:
        logging.error(f"API error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.exception(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()