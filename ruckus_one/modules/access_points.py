"""
Access Points module for the RUCKUS One API.

This module handles access point (AP) operations such as retrieving, configuring,
and monitoring APs.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class AccessPoints:
    """
    Access Points API module.
    
    Handles operations related to access points in the RUCKUS One API.
    """
    
    def __init__(self, client):
        """
        Initialize the AccessPoints module.
        
        Args:
            client: RuckusOneClient instance
        """
        self.client = client
        # Register this module with the client for easier access
        self.client.aps = self
    
    def list(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List access points with optional filtering.
        
        Args:
            query_data: Query parameters including filters, pagination, etc.
                Example: {
                    "filters": [
                        {
                            "type": "VENUE",
                            "value": "venue_id_here"
                        }
                    ],
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC"
                }
            
        Returns:
            Dict containing APs and pagination information
        """
        # Prepare default query if none provided
        if query_data is None:
            query_data = {
                "pageSize": 100,
                "page": 0,
                "sortOrder": "ASC"  # API requires uppercase
            }
        
        # Make sure sortOrder is uppercase
        if "sortOrder" in query_data:
            query_data["sortOrder"] = query_data["sortOrder"].upper()
        
        logger.debug(f"Querying APs with data: {query_data}")
            
        try:
            result = self.client.post("/venues/aps/query", data=query_data)
            logger.debug(f"AP query result keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying APs: {str(e)}")
            raise
    
    def get(self, ap_id: str) -> Dict[str, Any]:
        """
        Retrieve an access point by ID.
        
        Args:
            ap_id: ID of the AP to retrieve
            
        Returns:
            Dict containing AP details
            
        Raises:
            ResourceNotFoundError: If the AP does not exist
        """
        try:
            logger.debug(f"Getting AP details for AP ID: {ap_id}")
            # Search for the AP using the ID
            query_data = {
                "filters": [
                    {
                        "type": "ID",
                        "value": ap_id
                    }
                ]
            }
            result = self.client.post("/venues/aps/query", data=query_data)
            
            # If we have data, return the first item
            items = result.get('data', [])
            if items:
                return items[0]
            else:
                raise ResourceNotFoundError(message=f"AP with ID {ap_id} not found")
                
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"AP with ID {ap_id} not found")
        except Exception as e:
            logger.exception(f"Error getting AP details: {str(e)}")
            raise
    
    def update(self, venue_id: str, serial_number: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing access point.
        
        Args:
            venue_id: ID of the venue that contains the AP
            serial_number: Serial number of the AP to update
            **kwargs: AP properties to update
            
        Returns:
            Dict containing the updated AP details
            
        Raises:
            ResourceNotFoundError: If the AP does not exist
        """
        try:
            return self.client.put(f"/venues/{venue_id}/aps/{serial_number}", data=kwargs)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"AP with serial number {serial_number} not found in venue {venue_id}"
            )
    
    def reboot(self, venue_id: str, serial_number: str) -> Dict[str, Any]:
        """
        Reboot an access point.
        
        Args:
            venue_id: ID of the venue that contains the AP
            serial_number: Serial number of the AP to reboot
            
        Returns:
            Dict containing the reboot operation status
            
        Raises:
            ResourceNotFoundError: If the AP does not exist
        """
        try:
            return self.client.post(f"/venues/{venue_id}/aps/{serial_number}/reboot")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"AP with serial number {serial_number} not found in venue {venue_id}"
            )
    
    def get_clients(self, 
                   venue_id: str, 
                   serial_number: Optional[str] = None, 
                   **kwargs) -> Dict[str, Any]:
        """
        Get clients connected to an access point.
        
        Args:
            venue_id: ID of the venue
            serial_number: Optional serial number of a specific AP
            **kwargs: Additional filtering parameters
            
        Returns:
            Dict containing clients connected to the AP(s)
            
        Raises:
            ResourceNotFoundError: If the venue or AP does not exist
        """
        data = kwargs
        
        # Add AP filter if provided
        if serial_number:
            data["filters"] = data.get("filters", {})
            data["filters"]["serialNumber"] = serial_number
        
        try:
            return self.client.post(f"/venues/aps/clients/query", data=data)
        except ResourceNotFoundError:
            if serial_number:
                raise ResourceNotFoundError(
                    message=f"AP with serial number {serial_number} not found in venue {venue_id}"
                )
            else:
                raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
    
    def get_radio_settings(self, venue_id: str, serial_number: str) -> Dict[str, Any]:
        """
        Get radio settings for an access point.
        
        Args:
            venue_id: ID of the venue that contains the AP
            serial_number: Serial number of the AP
            
        Returns:
            Dict containing radio settings
            
        Raises:
            ResourceNotFoundError: If the AP does not exist
        """
        try:
            return self.client.get(f"/venues/{venue_id}/aps/{serial_number}/radioSettings")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"AP with serial number {serial_number} not found in venue {venue_id}"
            )
    
    def update_radio_settings(self, venue_id: str, serial_number: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update radio settings for an access point.
        
        Args:
            venue_id: ID of the venue that contains the AP
            serial_number: Serial number of the AP
            settings: Radio settings to update
            
        Returns:
            Dict containing updated radio settings
            
        Raises:
            ResourceNotFoundError: If the AP does not exist
        """
        try:
            return self.client.put(
                f"/venues/{venue_id}/aps/{serial_number}/radioSettings",
                data=settings
            )
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"AP with serial number {serial_number} not found in venue {venue_id}"
            )
    
    def get_statistics(self, venue_id: str, serial_number: str) -> Dict[str, Any]:
        """
        Get statistics for an access point.
        
        Args:
            venue_id: ID of the venue that contains the AP
            serial_number: Serial number of the AP
            
        Returns:
            Dict containing AP statistics
            
        Raises:
            ResourceNotFoundError: If the AP does not exist
        """
        try:
            return self.client.get(f"/venues/{venue_id}/aps/{serial_number}/statistics")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"AP with serial number {serial_number} not found in venue {venue_id}"
            )
            
    def add_to_group(self, venue_id: str, ap_group_id: str, serial_numbers: List[str]) -> Dict[str, Any]:
        """
        Add access points to an AP group.
        
        Args:
            venue_id: ID of the venue
            ap_group_id: ID of the AP group
            serial_numbers: List of AP serial numbers to add to the group
            
        Returns:
            Dict containing the operation result
            
        Raises:
            ResourceNotFoundError: If the venue, AP group, or any AP does not exist
        """
        data = {
            "serialNumbers": serial_numbers
        }
        
        try:
            return self.client.post(
                f"/venues/{venue_id}/apGroups/{ap_group_id}/members",
                data=data
            )
        except ResourceNotFoundError as e:
            # Check which resource is not found
            if "group" in str(e).lower():
                raise ResourceNotFoundError(message=f"AP group with ID {ap_group_id} not found")
            else:
                raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")