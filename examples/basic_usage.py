"""
Basic usage example for the RUCKUS One SDK.

This example demonstrates how to authenticate, list venues, and perform basic operations.
"""

import os
import sys
import logging
from pprint import pprint

# Add the parent directory to the path to import the SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ruckus_one import RuckusOneClient
from ruckus_one.exceptions import APIError, ResourceNotFoundError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API credentials (replace with your own or use environment variables)
API_REGION = os.environ.get("RUCKUS_API_REGION", "na")
API_CLIENT_ID = os.environ.get("RUCKUS_API_CLIENT_ID", "your-client-id")
API_CLIENT_SECRET = os.environ.get("RUCKUS_API_CLIENT_SECRET", "your-client-secret")
API_TENANT_ID = os.environ.get("RUCKUS_API_TENANT_ID", "your-tenant-id")

def main():
    """Main function to demonstrate SDK usage."""
    try:
        # Initialize the RUCKUS One client
        client = RuckusOneClient(
            client_id=API_CLIENT_ID,
            client_secret=API_CLIENT_SECRET,
            tenant_id=API_TENANT_ID,
            region=API_REGION
        )
        
        logger.info("Successfully authenticated with RUCKUS One API")
        
        # List venues
        logger.info("Listing venues...")
        venues = client.venues.list(page_size=10)
        
        if not venues.get('data'):
            logger.info("No venues found")
            return
            
        logger.info(f"Found {len(venues['data'])} venues")
        
        # Print the first venue
        first_venue = venues['data'][0]
        logger.info(f"First venue: {first_venue['name']} (ID: {first_venue['id']})")
        
        # Get more details about the first venue
        venue_id = first_venue['id']
        logger.info(f"Getting details for venue {venue_id}...")
        venue_details = client.venues.get(venue_id)
        
        logger.info("Venue details:")
        logger.info(f"  Name: {venue_details['name']}")
        logger.info(f"  Address: {venue_details.get('address', {}).get('street')}, "
                   f"{venue_details.get('address', {}).get('city')}, "
                   f"{venue_details.get('address', {}).get('state')}")
        logger.info(f"  Description: {venue_details.get('description', 'N/A')}")
        
        # List APs in the venue
        logger.info(f"Listing APs in venue {venue_id}...")
        aps = client.aps.list(venue_id=venue_id, page_size=10)
        
        if not aps.get('data'):
            logger.info("No APs found in this venue")
        else:
            logger.info(f"Found {len(aps['data'])} APs")
            
            # Print details of the first AP
            first_ap = aps['data'][0]
            logger.info(f"First AP: {first_ap.get('name', 'Unnamed')} "
                       f"(Serial: {first_ap.get('serialNumber')})")
            
            # Get more details about the first AP
            ap_serial = first_ap.get('serialNumber')
            if ap_serial:
                logger.info(f"Getting details for AP {ap_serial}...")
                try:
                    ap_details = client.aps.get(venue_id, ap_serial)
                    logger.info(f"AP details: {ap_details.get('name')} "
                               f"(Model: {ap_details.get('model')})")
                except ResourceNotFoundError:
                    logger.error(f"AP with serial {ap_serial} not found")
        
        # List WLANs
        logger.info("Listing WLANs...")
        wlans = client.wlans.list(page_size=10)
        
        if not wlans.get('data'):
            logger.info("No WLANs found")
        else:
            logger.info(f"Found {len(wlans['data'])} WLANs")
            
            # Print details of the first WLAN
            first_wlan = wlans['data'][0]
            logger.info(f"First WLAN: {first_wlan.get('name')} "
                       f"(SSID: {first_wlan.get('ssid')})")
            
        # List venue WLANs (WLANs deployed to the venue)
        logger.info(f"Listing WLANs deployed to venue {venue_id}...")
        venue_wlans = client.wlans.list_venue_wlans(venue_id, page_size=10)
        
        if not venue_wlans.get('data'):
            logger.info("No WLANs deployed to this venue")
        else:
            logger.info(f"Found {len(venue_wlans['data'])} WLANs deployed to this venue")
        
        logger.info("Example completed successfully")
        
    except APIError as e:
        logger.error(f"API Error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()