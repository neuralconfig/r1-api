#!/usr/bin/env python3
"""
RUCKUS One API Inventory Report Generator.

This script generates a comprehensive report of all resources accessible with
the provided credentials, including venues, switches, access points, and WLANs.
"""
import os
import sys
import json
import logging
import configparser
from datetime import datetime
from pprint import pformat
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the system path to import the ruckus_one package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ruckus_one.client import RuckusOneClient
from ruckus_one.modules.venues import Venues
from ruckus_one.modules.access_points import AccessPoints
from ruckus_one.modules.switches import Switches
from ruckus_one.modules.wlans import WLANs

def load_config():
    """Load configuration from config.ini file."""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
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

def get_venues(venues_module):
    """Get all venues accessible with the credentials."""
    logger.info("Getting venues...")
    query_data = {
        "pageSize": 100,
        "page": 0,
        "sortOrder": "ASC"
    }
    
    try:
        venues_result = venues_module.list(query_data)
        venues_list = venues_result.get('data', [])
        logger.info(f"Found {len(venues_list)} venues")
        return venues_list
    except Exception as e:
        logger.error(f"Error getting venues: {e}")
        return []

def get_access_points(ap_module, venue_id=None):
    """Get all access points, optionally filtered by venue."""
    logger.info("Getting access points...")
    query_data = {
        "pageSize": 100,
        "page": 0,
        "sortOrder": "ASC"
    }
    
    if venue_id:
        query_data["filters"] = [
            {
                "type": "VENUE",
                "value": venue_id
            }
        ]
    
    try:
        aps_result = ap_module.list(query_data)
        aps_list = aps_result.get('data', [])
        logger.info(f"Found {len(aps_list)} access points")
        return aps_list
    except Exception as e:
        logger.error(f"Error getting access points: {e}")
        return []

def get_switches(switches_module, venue_id=None):
    """Get all switches, optionally filtered by venue."""
    logger.info("Getting switches...")
    query_data = {
        "pageSize": 100,
        "page": 0,
        "sortOrder": "ASC"
    }
    
    try:
        switches_result = switches_module.list(query_data)
        switches_list = switches_result.get('data', [])
        logger.info(f"Found {len(switches_list)} switches")
        return switches_list
    except Exception as e:
        logger.error(f"Error getting switches: {e}")
        return []

def get_switch_ports(switches_module, switch_id=None):
    """Get all switch ports, optionally filtered by switch."""
    logger.info("Getting switch ports...")
    query_data = {
        "pageSize": 100,
        "page": 0,
        "sortOrder": "ASC"
    }
    
    try:
        ports_result = switches_module.get_ports(query_data)
        ports_list = ports_result.get('data', [])
        logger.info(f"Found {len(ports_list)} switch ports")
        return ports_list
    except Exception as e:
        logger.error(f"Error getting switch ports: {e}")
        return []

def get_wlans(wlans_module, venue_id=None):
    """Get all WLANs (WiFi networks)."""
    logger.info("Getting WLANs...")
    query_data = {
        "pageSize": 100,
        "page": 0,
        "sortOrder": "ASC"
    }
    
    try:
        wlans_result = wlans_module.list(query_data)
        wlans_list = wlans_result.get('data', [])
        logger.info(f"Found {len(wlans_list)} WLANs")
        return wlans_list
    except Exception as e:
        logger.error(f"Error getting WLANs: {e}")
        return []

def generate_report():
    """Generate and print a comprehensive inventory report."""
    # First try to load from config file
    config = load_config()
    
    # Then try environment variables or fall back to input
    client_id = os.environ.get("RUCKUS_CLIENT_ID") or config.get('client_id')
    client_secret = os.environ.get("RUCKUS_CLIENT_SECRET") or config.get('client_secret')
    tenant_id = os.environ.get("RUCKUS_TENANT_ID") or config.get('tenant_id')
    region = os.environ.get("RUCKUS_REGION") or config.get('region', 'na')
    
    if not all([client_id, client_secret, tenant_id]) or \
       any(x in [client_id, client_secret, tenant_id] for x in ['YOUR_CLIENT_ID', 'YOUR_CLIENT_SECRET', 'YOUR_TENANT_ID']):
        print("Please provide your RUCKUS One credentials:")
        if not client_id or client_id == 'YOUR_CLIENT_ID':
            client_id = input("Client ID: ")
        if not client_secret or client_secret == 'YOUR_CLIENT_SECRET':
            client_secret = input("Client Secret: ")
        if not tenant_id or tenant_id == 'YOUR_TENANT_ID':
            tenant_id = input("Tenant ID: ")
    
    # Initialize the client
    print(f"Initializing client with region: {region}")
    client = RuckusOneClient(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id, region=region)
    
    # Initialize modules
    venues_module = Venues(client)
    ap_module = AccessPoints(client)
    switches_module = Switches(client)
    wlan_module = WLANs(client)
    
    # Get all data
    venues = get_venues(venues_module)
    aps = get_access_points(ap_module)
    switches = get_switches(switches_module)
    switch_ports = get_switch_ports(switches_module)
    wlans = get_wlans(wlan_module)
    
    # Generate report
    report = []
    
    # Report header
    report.append("=" * 80)
    report.append(f"RUCKUS ONE INVENTORY REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")
    
    # Tenant Information
    report.append("TENANT INFORMATION")
    report.append("-" * 80)
    report.append(f"Tenant ID: {tenant_id}")
    report.append(f"Region: {region}")
    report.append("")
    
    # Venues summary
    report.append("VENUES SUMMARY")
    report.append("-" * 80)
    report.append(f"Total venues: {len(venues)}")
    report.append("")
    
    # Venues details
    report.append("VENUES DETAILS")
    report.append("-" * 80)
    for venue in venues:
        venue_id = venue.get('id')
        venue_name = venue.get('name', 'Unnamed')
        venue_aps = [ap for ap in aps if ap.get('venueId') == venue_id]
        venue_switches = [switch for switch in switches if switch.get('venueId') == venue_id]
        venue_wlans = []  # We can't easily filter WLANs by venue from the current data
        
        report.append(f"Venue: {venue_name} (ID: {venue_id})")
        report.append(f"  Address: {venue.get('addressLine', 'N/A')}")
        report.append(f"  City: {venue.get('city', 'N/A')}")
        report.append(f"  Country: {venue.get('country', 'N/A')}")
        report.append(f"  Status: {venue.get('status', 'N/A')}")
        report.append(f"  AP Count: {len(venue_aps)}")
        report.append(f"  Switch Count: {len(venue_switches)}")
        report.append("")
    
    # Access Points summary
    report.append("ACCESS POINTS SUMMARY")
    report.append("-" * 80)
    report.append(f"Total access points: {len(aps)}")
    
    # Group APs by model
    ap_models = {}
    for ap in aps:
        model = ap.get('model', 'Unknown')
        ap_models[model] = ap_models.get(model, 0) + 1
    
    report.append("AP Models:")
    for model, count in ap_models.items():
        report.append(f"  {model}: {count} units")
    report.append("")
    
    # Access Points details
    report.append("ACCESS POINTS DETAILS")
    report.append("-" * 80)
    for ap in aps:
        ap_name = ap.get('name', 'Unnamed')
        ap_serial = ap.get('serialNumber', 'Unknown')
        ap_mac = ap.get('macAddress', 'Unknown')
        ap_model = ap.get('model', 'Unknown')
        ap_status = ap.get('status', 'Unknown')
        ap_firmware = ap.get('firmwareVersion', 'Unknown')
        
        report.append(f"AP: {ap_name} (Serial: {ap_serial})")
        report.append(f"  Model: {ap_model}")
        report.append(f"  MAC: {ap_mac}")
        report.append(f"  Status: {ap_status}")
        report.append(f"  Firmware: {ap_firmware}")
        report.append("")
    
    # Switches summary
    report.append("SWITCHES SUMMARY")
    report.append("-" * 80)
    report.append(f"Total switches: {len(switches)}")
    
    # Group switches by model
    switch_models = {}
    for switch in switches:
        model = switch.get('model', 'Unknown')
        switch_models[model] = switch_models.get(model, 0) + 1
    
    report.append("Switch Models:")
    for model, count in switch_models.items():
        report.append(f"  {model}: {count} units")
    report.append("")
    
    # Switches details
    report.append("SWITCHES DETAILS")
    report.append("-" * 80)
    for switch in switches:
        switch_name = switch.get('name', 'Unnamed')
        switch_id = switch.get('id', 'Unknown')
        switch_serial = switch.get('serialNumber', 'Unknown')
        switch_model = switch.get('model', 'Unknown')
        switch_status = switch.get('status', 'Unknown')
        switch_firmware = switch.get('firmwareVersion', 'Unknown')
        
        # Get ports for this switch
        switch_ports_list = [port for port in switch_ports if port.get('switchMac') == switch_id]
        
        report.append(f"Switch: {switch_name} (ID: {switch_id})")
        report.append(f"  Model: {switch_model}")
        report.append(f"  Serial: {switch_serial}")
        report.append(f"  Status: {switch_status}")
        report.append(f"  Firmware: {switch_firmware}")
        report.append(f"  Port Count: {len(switch_ports_list)}")
        report.append("")
        
        # Add port details
        if switch_ports_list:
            report.append(f"  Ports for {switch_name}:")
            for port in switch_ports_list:
                port_id = port.get('portIdentifier', 'Unknown')
                port_name = port.get('name', 'Unnamed')
                port_status = port.get('status', 'Unknown')
                port_speed = port.get('portSpeed', 'Unknown')
                port_vlan = port.get('unTaggedVlan', 'N/A')
                port_vlan_ids = port.get('vlanIds', 'N/A')
                
                report.append(f"    Port {port_id}: {port_name}")
                report.append(f"      Status: {port_status}")
                report.append(f"      Speed: {port_speed}")
                report.append(f"      Untagged VLAN: {port_vlan}")
                report.append(f"      VLAN IDs: {port_vlan_ids}")
                report.append("")
    
    # WLANs summary
    report.append("WLANs SUMMARY")
    report.append("-" * 80)
    report.append(f"Total WLANs: {len(wlans)}")
    report.append("")
    
    # WLANs details
    report.append("WLANs DETAILS")
    report.append("-" * 80)
    for wlan in wlans:
        wlan_name = wlan.get('name', 'Unnamed')
        wlan_id = wlan.get('id', 'Unknown')
        wlan_ssid = wlan.get('ssid', 'Unknown')
        wlan_type = wlan.get('nwSubType', 'Unknown')
        wlan_security = wlan.get('securityProtocol', 'Unknown')
        wlan_vlan = wlan.get('vlan', 'N/A')
        
        report.append(f"WLAN: {wlan_name} (ID: {wlan_id})")
        report.append(f"  SSID: {wlan_ssid}")
        report.append(f"  Type: {wlan_type}")
        report.append(f"  Security: {wlan_security}")
        report.append(f"  VLAN: {wlan_vlan}")
        report.append("")
    
    # Join the report lines and return
    return "\n".join(report)

def main():
    """Main entry point for the script."""
    try:
        report = generate_report()
        
        # Save to file
        filename = f"ruckus_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(report)
        
        # Print to console
        print(report)
        print(f"\nReport saved to {filename}")
        
    except Exception as e:
        logger.exception("Error generating report")
        print(f"Error generating report: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())