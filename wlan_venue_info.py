#!/usr/bin/env python3
"""
Script to analyze WLAN-venue relationships for the RUCKUS One API.
This will check all venues and try to determine which WLANs are associated with each venue.
"""

import os
import sys
import configparser
import json
from pprint import pprint

# Configure paths
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from ruckus_one.client import RuckusOneClient

def load_config():
    """Load configuration from config.ini file."""
    config = configparser.ConfigParser()
    config_path = os.path.join(script_dir, 'config.ini')
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

def main():
    # Load config
    config = load_config()
    
    # Initialize client
    client = RuckusOneClient(
        client_id=config.get('client_id'),
        client_secret=config.get('client_secret'),
        tenant_id=config.get('tenant_id'),
        region=config.get('region', 'na')
    )
    
    # Get all venues
    venues_result = client.venues.list(page_size=100, page=0, sort_order="ASC")
    venues = venues_result.get('data', [])
    print(f"Found {len(venues)} venues")
    
    # Get all WLANs
    wlans_result = client.wlans.list({"pageSize": 100, "page": 0, "sortOrder": "ASC"})
    wlans = wlans_result.get('data', [])
    print(f"Found {len(wlans)} WLANs")
    
    print("\nChecking for WLANs in all venues:")
    
    # For each venue, try different methods to find associated WLANs
    for venue in venues:
        venue_id = venue.get('id')
        venue_name = venue.get('name')
        print(f"\nVenue: {venue_name} (ID: {venue_id})")
        
        # Method 1: Check venueId field
        wlans_count = 0
        print("WLANs with venueId matching this venue:")
        for wlan in wlans:
            if wlan.get('venueId') == venue_id:
                wlans_count += 1
                print(f"  {wlan.get('name')} (SSID: {wlan.get('ssid')})")
        print(f"Count: {wlans_count}")
        
        # Method 2: Check venues array
        wlans_count = 0
        print("WLANs with venues array containing this venue:")
        for wlan in wlans:
            venues_list = wlan.get('venues', [])
            for v in venues_list:
                if v.get('id') == venue_id:
                    wlans_count += 1
                    print(f"  {wlan.get('name')} (SSID: {wlan.get('ssid')})")
                    break
        print(f"Count: {wlans_count}")
        
        # Method 3: Check deployments
        wlans_count = 0
        print("WLANs with deployments matching this venue:")
        for wlan in wlans:
            deployments = wlan.get('deployments', [])
            for deployment in deployments:
                # Check for both VENUE type and any other type with matching venue ID
                if deployment.get('id') == venue_id:
                    wlans_count += 1
                    print(f"  {wlan.get('name')} (SSID: {wlan.get('ssid')}) - Deployment type: {deployment.get('type')}")
                    break
        print(f"Count: {wlans_count}")
        
        # Method 4: Check venueApGroups field
        wlans_count = 0
        print("WLANs with venueApGroups matching this venue:")
        for wlan in wlans:
            venue_ap_groups = wlan.get('venueApGroups', [])
            if any(group.get('venueId') == venue_id for group in venue_ap_groups):
                wlans_count += 1
                print(f"  {wlan.get('name')} (SSID: {wlan.get('ssid')})")
        print(f"Count: {wlans_count}")
        
        # Method 5: Name-based matching for "Home" venue special case
        if venue_name == "Home":
            wlans_count = 0
            print("WLANs with name patterns matching Home network:")
            home_patterns = ['home', 'guest', 'iot', 'network', 'wifi', 'mesh']
            for wlan in wlans:
                wlan_name = wlan.get('name', '').lower()
                if any(pattern in wlan_name for pattern in home_patterns):
                    wlans_count += 1
                    print(f"  {wlan.get('name')} (SSID: {wlan.get('ssid')}) - Client count: {wlan.get('clientCount', 0)}")
            print(f"Count: {wlans_count}")
        
        # Method 6: Try direct API request for venue's WiFi networks
        try:
            venue_wifi_url = f"/venues/{venue_id}/wifiNetworks"
            print(f"Attempting direct API request to {venue_wifi_url}")
            try:
                # Try GET method
                wifi_results = client.get(venue_wifi_url)
                if isinstance(wifi_results, dict) and 'data' in wifi_results:
                    venue_wifis = wifi_results.get('data', [])
                    print(f"Found {len(venue_wifis)} WLANs via direct GET API")
                    for wifi in venue_wifis[:5]:  # Show first 5 only
                        print(f"  {wifi.get('name')} (SSID: {wifi.get('ssid', 'Unknown')})")
                else:
                    print("No direct API results found via GET")
            except Exception as e:
                print(f"Error on GET request: {e}")
                
            # Try query endpoint
            venue_query_url = f"/venues/{venue_id}/wifiNetworks/query"
            print(f"Attempting API query request to {venue_query_url}")
            try:
                # Try GET method with params
                query_data = {
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC"
                }
                wifi_results = client.get(venue_query_url, params=query_data)
                if isinstance(wifi_results, dict) and 'data' in wifi_results:
                    venue_wifis = wifi_results.get('data', [])
                    print(f"Found {len(venue_wifis)} WLANs via GET query API")
                    for wifi in venue_wifis[:5]:  # Show first 5 only
                        print(f"  {wifi.get('name')} (SSID: {wifi.get('ssid', 'Unknown')})")
                else:
                    print("No query API results found via GET")
            except Exception as e:
                print(f"Error on GET query: {e}")
        except Exception as e:
            print(f"Error with venue API requests: {e}")

if __name__ == "__main__":
    main()