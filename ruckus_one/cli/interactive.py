"""
Interactive CLI for the RUCKUS One SDK.

This module provides an interactive command-line interface for the RUCKUS One SDK,
similar to a network switch CLI with tab completion and "?" help functionality.
"""

import os
import sys
import cmd2
import configparser
import json
import logging
from typing import Dict, Any, Optional, List, Tuple

from .. import __version__
from ..client import RuckusOneClient
from ..exceptions import APIError, AuthenticationError
from .main import load_config


class RuckusOneCLI(cmd2.Cmd):
    """Interactive CLI for the RUCKUS One SDK."""
    
    # Command categories
    CATEGORY_GENERAL = 'General Commands'
    CATEGORY_VENUE = 'Venue Commands'
    CATEGORY_AP = 'Access Point Commands'
    CATEGORY_SWITCH = 'Switch Commands'
    CATEGORY_WLAN = 'WLAN Commands'
    CATEGORY_VLAN = 'VLAN Commands'
    
    def __init__(self):
        """Initialize the interactive CLI."""
        # Set up cmd2 options
        super().__init__(
            allow_cli_args=True,
            allow_redirection=True,
            persistent_history_file='~/.ruckus_one_history',
            command_sets=[],
            shortcuts={
                '?': 'help',
                'exit': 'quit',
                'ls': 'list',
                'h': 'history'
            },
            include_ipy=False
        )
        
        # Configure cmd2 prompt and intro
        self.prompt = 'RUCKUS> '
        self.intro = f"""
RUCKUS One SDK Interactive CLI v{__version__}
Type ? for help, TAB for command completion, exit to quit.
        """
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Initialize client as None (will be set by authenticate command)
        self.client = None
        self.config_path = None
        self.auth_credentials = {
            'client_id': None,
            'client_secret': None,
            'tenant_id': None,
            'region': 'na'
        }
        
    # --------- Authentication commands ---------
    
    auth_parser = cmd2.Cmd2ArgumentParser(description='Authenticate with RUCKUS One API')
    auth_parser.add_argument('-c', '--config', help='Path to config.ini file')
    auth_parser.add_argument('--client_id', help='RUCKUS One OAuth2 client ID')
    auth_parser.add_argument('--client_secret', help='RUCKUS One OAuth2 client secret')
    auth_parser.add_argument('--tenant_id', help='RUCKUS One tenant ID')
    auth_parser.add_argument('--region', help='RUCKUS One API region (na, eu, asia)')
    
    @cmd2.with_category(CATEGORY_GENERAL)
    @cmd2.with_argparser(auth_parser)
    def do_authenticate(self, args):
        """Authenticate with the RUCKUS One API."""
        try:
            if args.config:
                self.config_path = args.config
                config = load_config(args.config)
                self.auth_credentials.update(config)
                self.poutput(f"Loaded credentials from {args.config}")
            
            # Override with args if provided
            if args.client_id:
                self.auth_credentials['client_id'] = args.client_id
            if args.client_secret:
                self.auth_credentials['client_secret'] = args.client_secret
            if args.tenant_id:
                self.auth_credentials['tenant_id'] = args.tenant_id
            if args.region:
                self.auth_credentials['region'] = args.region
            
            # Check if we need to prompt for missing credentials
            if not self.auth_credentials.get('client_id'):
                self.auth_credentials['client_id'] = self.read_token("Enter Client ID: ")
            if not self.auth_credentials.get('client_secret'):
                self.auth_credentials['client_secret'] = self.read_token("Enter Client Secret: ")
            if not self.auth_credentials.get('tenant_id'):
                self.auth_credentials['tenant_id'] = self.read_token("Enter Tenant ID: ")
            
            # Create client
            self.client = RuckusOneClient(
                client_id=self.auth_credentials['client_id'],
                client_secret=self.auth_credentials['client_secret'],
                tenant_id=self.auth_credentials['tenant_id'],
                region=self.auth_credentials['region']
            )
            
            self.poutput(f"Successfully authenticated with RUCKUS One API")
            self.poutput(f"Region: {self.auth_credentials['region']}")
            self.poutput(f"Tenant ID: {self.auth_credentials['tenant_id']}")
            
            # Update prompt to show authenticated status
            self.prompt = f"RUCKUS({self.auth_credentials['region']})> "
            
        except AuthenticationError as e:
            self.perror(f"Authentication failed: {e}")
        except Exception as e:
            self.perror(f"Error: {e}")
    
    def read_token(self, prompt_text):
        """Read a token with getpass to hide the input."""
        return self.read_secure(prompt_text)
    
    @cmd2.with_category(CATEGORY_GENERAL)
    def do_status(self, _):
        """Show current authentication status."""
        if not self.client:
            self.poutput("Not authenticated. Use 'authenticate' to connect to RUCKUS One API.")
            return
        
        self.poutput("RUCKUS One API Status:")
        self.poutput(f"  Region: {self.auth_credentials['region']}")
        self.poutput(f"  Tenant ID: {self.auth_credentials['tenant_id']}")
        self.poutput(f"  Config file: {self.config_path or 'Not using config file'}")
        self.poutput("  Authenticated: Yes")
    
    # --------- Venue commands ---------
    
    venue_list_parser = cmd2.Cmd2ArgumentParser(description='List venues')
    venue_list_parser.add_argument('--search', help='Search string')
    venue_list_parser.add_argument('--page-size', type=int, default=10, help='Page size')
    venue_list_parser.add_argument('--page', type=int, default=0, help='Page number')
    
    venue_get_parser = cmd2.Cmd2ArgumentParser(description='Get venue details')
    venue_get_parser.add_argument('id', help='Venue ID')
    
    @cmd2.with_category(CATEGORY_VENUE)
    @cmd2.with_argparser(venue_list_parser)
    def do_list_venues(self, args):
        """List venues."""
        if not self.client:
            self.perror("Not authenticated. Use 'authenticate' first.")
            return
        
        try:
            venues = self.client.venues.list(
                search_string=args.search,
                page_size=args.page_size,
                page=args.page
            )
            
            # Display venues in a table
            if 'data' in venues and venues['data']:
                self.poutput("\nVenues:")
                self.poutput(f"{'ID':<36} | {'Name':<30} | {'City':<20} | {'Country':<10}")
                self.poutput("-" * 100)
                
                for venue in venues['data']:
                    venue_id = venue.get('id', 'N/A')
                    name = venue.get('name', 'N/A')
                    city = venue.get('city', 'N/A')
                    country = venue.get('country', 'N/A')
                    self.poutput(f"{venue_id:<36} | {name:<30} | {city:<20} | {country:<10}")
                
                self.poutput(f"\nShowing {len(venues['data'])} of {venues.get('totalItems', 'unknown')} venues")
            else:
                self.poutput("No venues found.")
                
        except APIError as e:
            self.perror(f"API error: {e}")
        except Exception as e:
            self.perror(f"Error: {e}")
    
    @cmd2.with_category(CATEGORY_VENUE)
    @cmd2.with_argparser(venue_get_parser)
    def do_show_venue(self, args):
        """Show venue details."""
        if not self.client:
            self.perror("Not authenticated. Use 'authenticate' first.")
            return
        
        try:
            venue = self.client.venues.get(args.id)
            
            # Display venue details
            self.poutput("\nVenue Details:")
            self.poutput(f"ID: {venue.get('id', 'N/A')}")
            self.poutput(f"Name: {venue.get('name', 'N/A')}")
            self.poutput(f"Address: {venue.get('addressLine', 'N/A')}")
            self.poutput(f"City: {venue.get('city', 'N/A')}")
            self.poutput(f"State/Province: {venue.get('stateOrProvince', 'N/A')}")
            self.poutput(f"Country: {venue.get('country', 'N/A')}")
            self.poutput(f"Postal Code: {venue.get('postalCode', 'N/A')}")
            self.poutput(f"Timezone: {venue.get('timezone', 'N/A')}")
            self.poutput(f"Status: {venue.get('status', 'N/A')}")
            
        except APIError as e:
            self.perror(f"API error: {e}")
        except Exception as e:
            self.perror(f"Error: {e}")
    
    # --------- AP commands ---------
    
    ap_list_parser = cmd2.Cmd2ArgumentParser(description='List access points')
    ap_list_parser.add_argument('--venue-id', help='Venue ID')
    ap_list_parser.add_argument('--search', help='Search string')
    ap_list_parser.add_argument('--page-size', type=int, default=10, help='Page size')
    ap_list_parser.add_argument('--page', type=int, default=0, help='Page number')
    
    ap_get_parser = cmd2.Cmd2ArgumentParser(description='Get AP details')
    ap_get_parser.add_argument('venue_id', help='Venue ID')
    ap_get_parser.add_argument('serial', help='AP serial number')
    
    @cmd2.with_category(CATEGORY_AP)
    @cmd2.with_argparser(ap_list_parser)
    def do_list_aps(self, args):
        """List access points."""
        if not self.client:
            self.perror("Not authenticated. Use 'authenticate' first.")
            return
        
        try:
            filters = {}
            if args.venue_id:
                filters["venueId"] = args.venue_id
                
            aps = self.client.aps.list(
                search_string=args.search,
                page_size=args.page_size,
                page=args.page,
                **filters
            )
            
            # Display APs in a table
            if 'data' in aps and aps['data']:
                self.poutput("\nAccess Points:")
                self.poutput(f"{'Serial':<15} | {'Name':<25} | {'Model':<12} | {'Status':<8} | {'Venue ID':<36}")
                self.poutput("-" * 100)
                
                for ap in aps['data']:
                    serial = ap.get('serialNumber', 'N/A')
                    name = ap.get('name', 'N/A')
                    model = ap.get('model', 'N/A')
                    status = ap.get('status', 'N/A')
                    venue_id = ap.get('venueId', 'N/A')
                    self.poutput(f"{serial:<15} | {name:<25} | {model:<12} | {status:<8} | {venue_id:<36}")
                
                self.poutput(f"\nShowing {len(aps['data'])} of {aps.get('totalItems', 'unknown')} access points")
            else:
                self.poutput("No access points found.")
                
        except APIError as e:
            self.perror(f"API error: {e}")
        except Exception as e:
            self.perror(f"Error: {e}")
    
    @cmd2.with_category(CATEGORY_AP)
    @cmd2.with_argparser(ap_get_parser)
    def do_show_ap(self, args):
        """Show access point details."""
        if not self.client:
            self.perror("Not authenticated. Use 'authenticate' first.")
            return
        
        try:
            ap = self.client.aps.get(args.venue_id, args.serial)
            
            # Display AP details
            self.poutput("\nAccess Point Details:")
            self.poutput(f"Serial: {ap.get('serialNumber', 'N/A')}")
            self.poutput(f"Name: {ap.get('name', 'N/A')}")
            self.poutput(f"Model: {ap.get('model', 'N/A')}")
            self.poutput(f"Status: {ap.get('status', 'N/A')}")
            self.poutput(f"MAC: {ap.get('macAddress', 'N/A')}")
            self.poutput(f"IP: {ap.get('ipAddress', 'N/A')}")
            self.poutput(f"Firmware: {ap.get('firmwareVersion', 'N/A')}")
            self.poutput(f"Venue ID: {ap.get('venueId', 'N/A')}")
            
        except APIError as e:
            self.perror(f"API error: {e}")
        except Exception as e:
            self.perror(f"Error: {e}")
    
    # --------- WLAN commands ---------
    
    wlan_list_parser = cmd2.Cmd2ArgumentParser(description='List WLANs')
    wlan_list_parser.add_argument('--search', help='Search string')
    wlan_list_parser.add_argument('--page-size', type=int, default=10, help='Page size')
    wlan_list_parser.add_argument('--page', type=int, default=0, help='Page number')
    
    wlan_get_parser = cmd2.Cmd2ArgumentParser(description='Get WLAN details')
    wlan_get_parser.add_argument('id', help='WLAN ID')
    
    @cmd2.with_category(CATEGORY_WLAN)
    @cmd2.with_argparser(wlan_list_parser)
    def do_list_wlans(self, args):
        """List WLANs."""
        if not self.client:
            self.perror("Not authenticated. Use 'authenticate' first.")
            return
        
        try:
            wlans = self.client.wlans.list(
                search_string=args.search,
                page_size=args.page_size,
                page=args.page
            )
            
            # Display WLANs in a table
            if 'data' in wlans and wlans['data']:
                self.poutput("\nWLANs:")
                self.poutput(f"{'ID':<36} | {'Name':<25} | {'SSID':<20} | {'Security':<15} | {'VLAN':<5}")
                self.poutput("-" * 100)
                
                for wlan in wlans['data']:
                    wlan_id = wlan.get('id', 'N/A')
                    name = wlan.get('name', 'N/A')
                    ssid = wlan.get('ssid', 'N/A')
                    security = wlan.get('securityProtocol', 'N/A')
                    vlan = wlan.get('vlan', 'N/A')
                    self.poutput(f"{wlan_id:<36} | {name:<25} | {ssid:<20} | {security:<15} | {vlan:<5}")
                
                self.poutput(f"\nShowing {len(wlans['data'])} of {wlans.get('totalItems', 'unknown')} WLANs")
            else:
                self.poutput("No WLANs found.")
                
        except APIError as e:
            self.perror(f"API error: {e}")
        except Exception as e:
            self.perror(f"Error: {e}")
    
    @cmd2.with_category(CATEGORY_WLAN)
    @cmd2.with_argparser(wlan_get_parser)
    def do_show_wlan(self, args):
        """Show WLAN details."""
        if not self.client:
            self.perror("Not authenticated. Use 'authenticate' first.")
            return
        
        try:
            wlan = self.client.wlans.get(args.id)
            
            # Display WLAN details
            self.poutput("\nWLAN Details:")
            self.poutput(f"ID: {wlan.get('id', 'N/A')}")
            self.poutput(f"Name: {wlan.get('name', 'N/A')}")
            self.poutput(f"SSID: {wlan.get('ssid', 'N/A')}")
            self.poutput(f"Description: {wlan.get('description', 'N/A')}")
            self.poutput(f"Security: {wlan.get('securityProtocol', 'N/A')}")
            self.poutput(f"VLAN: {wlan.get('vlan', 'N/A')}")
            self.poutput(f"Hidden: {wlan.get('hiddenSsid', False)}")
            
        except APIError as e:
            self.perror(f"API error: {e}")
        except Exception as e:
            self.perror(f"Error: {e}")

    # --------- Switch commands ---------
    
    switch_list_parser = cmd2.Cmd2ArgumentParser(description='List switches')
    switch_list_parser.add_argument('--search', help='Search string')
    switch_list_parser.add_argument('--page-size', type=int, default=10, help='Page size')
    switch_list_parser.add_argument('--page', type=int, default=0, help='Page number')
    
    switch_get_parser = cmd2.Cmd2ArgumentParser(description='Get switch details')
    switch_get_parser.add_argument('id', help='Switch ID')
    
    @cmd2.with_category(CATEGORY_SWITCH)
    @cmd2.with_argparser(switch_list_parser)
    def do_list_switches(self, args):
        """List switches."""
        if not self.client:
            self.perror("Not authenticated. Use 'authenticate' first.")
            return
        
        try:
            switches = self.client.switches.list({
                "pageSize": args.page_size,
                "page": args.page,
                "sortOrder": "ASC"
            })
            
            # Display switches in a table
            if 'data' in switches and switches['data']:
                self.poutput("\nSwitches:")
                self.poutput(f"{'ID':<36} | {'Name':<25} | {'Model':<15} | {'Status':<8} | {'Venue ID':<36}")
                self.poutput("-" * 100)
                
                for switch in switches['data']:
                    switch_id = switch.get('id', 'N/A')
                    name = switch.get('name', 'N/A')
                    model = switch.get('model', 'N/A')
                    status = switch.get('status', 'N/A')
                    venue_id = switch.get('venueId', 'N/A')
                    self.poutput(f"{switch_id:<36} | {name:<25} | {model:<15} | {status:<8} | {venue_id:<36}")
                
                self.poutput(f"\nShowing {len(switches['data'])} of {switches.get('totalItems', 'unknown')} switches")
            else:
                self.poutput("No switches found.")
                
        except APIError as e:
            self.perror(f"API error: {e}")
        except Exception as e:
            self.perror(f"Error: {e}")
    
    @cmd2.with_category(CATEGORY_SWITCH)
    @cmd2.with_argparser(switch_get_parser)
    def do_show_switch(self, args):
        """Show switch details."""
        if not self.client:
            self.perror("Not authenticated. Use 'authenticate' first.")
            return
        
        try:
            # Get switch details
            switch = self.client.switches.get(args.id)
            
            # Display switch details
            self.poutput("\nSwitch Details:")
            self.poutput(f"ID: {switch.get('id', 'N/A')}")
            self.poutput(f"Name: {switch.get('name', 'N/A')}")
            self.poutput(f"Model: {switch.get('model', 'N/A')}")
            self.poutput(f"Serial: {switch.get('serialNumber', 'N/A')}")
            self.poutput(f"Status: {switch.get('status', 'N/A')}")
            self.poutput(f"IP: {switch.get('ip', 'N/A')}")
            self.poutput(f"Firmware: {switch.get('firmwareVersion', 'N/A')}")
            self.poutput(f"Venue ID: {switch.get('venueId', 'N/A')}")
            
        except APIError as e:
            self.perror(f"API error: {e}")
        except Exception as e:
            self.perror(f"Error: {e}")

    # Helper method to check authentication 
    def require_auth(self) -> bool:
        """Check if client is authenticated and print error if not."""
        if not self.client:
            self.perror("Not authenticated. Use 'authenticate' first.")
            return False
        return True


def main():
    """Launch the interactive CLI."""
    cli = RuckusOneCLI()
    cli.cmdloop()


if __name__ == '__main__':
    main()