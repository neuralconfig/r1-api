"""
Switches module for the RUCKUS One API.

This module handles switch operations such as retrieving, configuring, and
monitoring switches.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class Switches:
    """
    Switches API module.
    
    Handles operations related to switches in the RUCKUS One API.
    """
    
    def __init__(self, client):
        """
        Initialize the Switches module.
        
        Args:
            client: RuckusOneClient instance
        """
        self.client = client
        # Register this module with the client for easier access
        self.client.switches = self
    
    def list(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List switches with optional filtering.
        
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
            Dict containing switches and pagination information
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
        
        logger.debug(f"Querying switches with data: {query_data}")
            
        try:
            result = self.client.post("/venues/switches/query", data=query_data)
            logger.debug(f"Switches query result keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying switches: {str(e)}")
            raise
    
    def get(self, venue_id: str, switch_id: str) -> Dict[str, Any]:
        """
        Retrieve a switch by ID.
        
        Args:
            venue_id: ID of the venue that contains the switch
            switch_id: ID of the switch to retrieve
            
        Returns:
            Dict containing switch details
            
        Raises:
            ResourceNotFoundError: If the switch does not exist
        """
        try:
            return self.client.get(f"/venues/{venue_id}/switches/{switch_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"Switch with ID {switch_id} not found in venue {venue_id}"
            )
    
    def update(self, venue_id: str, switch_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing switch.
        
        Args:
            venue_id: ID of the venue that contains the switch
            switch_id: ID of the switch to update
            **kwargs: Switch properties to update
            
        Returns:
            Dict containing the updated switch details
            
        Raises:
            ResourceNotFoundError: If the switch does not exist
        """
        try:
            return self.client.put(f"/venues/{venue_id}/switches/{switch_id}", data=kwargs)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"Switch with ID {switch_id} not found in venue {venue_id}"
            )
    
    def reboot(self, venue_id: str, switch_id: str) -> Dict[str, Any]:
        """
        Reboot a switch.
        
        Args:
            venue_id: ID of the venue that contains the switch
            switch_id: ID of the switch to reboot
            
        Returns:
            Dict containing the reboot operation status
            
        Raises:
            ResourceNotFoundError: If the switch does not exist
        """
        try:
            return self.client.post(f"/venues/{venue_id}/switches/{switch_id}/reboot")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"Switch with ID {switch_id} not found in venue {venue_id}"
            )
    
    def get_ports(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get ports for a switch or switches.
        
        Args:
            query_data: Query parameters including filters, pagination, etc.
                Example: {
                    "filters": [
                        {
                            "type": "SWITCH",
                            "value": "switch_id_here"
                        }
                    ],
                    "pageSize": 100,
                    "page": 0
                }
            
        Returns:
            Dict containing switch ports
        """
        # Prepare default query if none provided
        if query_data is None:
            query_data = {
                "pageSize": 100,
                "page": 0,
                "sortOrder": "ASC"  # API requires uppercase
            }
        
        # Make sure sortOrder is uppercase if present
        if "sortOrder" in query_data:
            query_data["sortOrder"] = query_data["sortOrder"].upper()
        
        logger.debug(f"Querying switch ports with data: {query_data}")
            
        try:
            result = self.client.post("/venues/switches/switchPorts/query", data=query_data)
            logger.debug(f"Switch ports query result keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying switch ports: {str(e)}")
            raise
    
    def configure_port(self, venue_id: str, switch_id: str, port_id: str, **kwargs) -> Dict[str, Any]:
        """
        Configure a switch port.
        
        Args:
            venue_id: ID of the venue
            switch_id: ID of the switch
            port_id: ID of the port to configure
            **kwargs: Port configuration parameters
            
        Returns:
            Dict containing the updated port configuration
            
        Raises:
            ResourceNotFoundError: If the switch or port does not exist
        """
        try:
            return self.client.put(
                f"/venues/{venue_id}/switches/{switch_id}/ports/{port_id}",
                data=kwargs
            )
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"Switch port with ID {port_id} not found in switch {switch_id}"
            )
    
    def get_vlans(self, venue_id: str, switch_id: str) -> Dict[str, Any]:
        """
        Get VLANs configured on a switch.
        
        Args:
            venue_id: ID of the venue
            switch_id: ID of the switch
            
        Returns:
            Dict containing VLANs configured on the switch
            
        Raises:
            ResourceNotFoundError: If the switch does not exist
        """
        logger.debug(f"Getting VLANs for switch {switch_id} in venue {venue_id}")
        try:
            result = self.client.get(f"/venues/{venue_id}/switches/{switch_id}/vlans")
            logger.debug(f"Retrieved {len(result) if isinstance(result, list) else '?'} VLANs")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch with ID {switch_id} not found in venue {venue_id}")
            raise ResourceNotFoundError(
                message=f"Switch with ID {switch_id} not found in venue {venue_id}"
            )
        except Exception as e:
            logger.exception(f"Error getting VLANs: {str(e)}")
            raise
    
    def configure_vlan(self, venue_id: str, switch_id: str, vlan_id: int, **kwargs) -> Dict[str, Any]:
        """
        Configure a VLAN on a switch.
        
        Args:
            venue_id: ID of the venue
            switch_id: ID of the switch
            vlan_id: ID of the VLAN to configure
            **kwargs: VLAN configuration parameters
                Example: {
                    "name": "Voice VLAN",
                    "igmpSnooping": True
                }
            
        Returns:
            Dict containing the updated VLAN configuration
            
        Raises:
            ResourceNotFoundError: If the switch or VLAN does not exist
        """
        logger.debug(f"Configuring VLAN {vlan_id} on switch {switch_id} with params: {kwargs}")
        try:
            result = self.client.put(
                f"/venues/{venue_id}/switches/{switch_id}/vlans/{vlan_id}",
                data=kwargs
            )
            logger.debug(f"VLAN configuration successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"VLAN with ID {vlan_id} not found in switch {switch_id}")
            raise ResourceNotFoundError(
                message=f"VLAN with ID {vlan_id} not found in switch {switch_id}"
            )
        except Exception as e:
            logger.exception(f"Error configuring VLAN: {str(e)}")
            raise
            
    def create_vlan(self, venue_id: str, switch_id: str, vlan_id: int, **kwargs) -> Dict[str, Any]:
        """
        Create a new VLAN on a switch.
        
        Args:
            venue_id: ID of the venue
            switch_id: ID of the switch
            vlan_id: ID of the VLAN to create (1-4094)
            **kwargs: VLAN configuration parameters
                Example: {
                    "name": "Data VLAN",
                    "igmpSnooping": False
                }
            
        Returns:
            Dict containing the created VLAN configuration
            
        Raises:
            ResourceNotFoundError: If the switch does not exist
            ValidationError: If the VLAN ID is invalid or already exists
        """
        logger.debug(f"Creating VLAN {vlan_id} on switch {switch_id} with params: {kwargs}")
        
        # Prepare the VLAN data
        data = {"id": vlan_id}
        data.update(kwargs)
        
        try:
            result = self.client.post(
                f"/venues/{venue_id}/switches/{switch_id}/vlans",
                data=data
            )
            logger.debug(f"VLAN creation successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch with ID {switch_id} not found in venue {venue_id}")
            raise ResourceNotFoundError(
                message=f"Switch with ID {switch_id} not found in venue {venue_id}"
            )
        except Exception as e:
            logger.exception(f"Error creating VLAN: {str(e)}")
            raise
    
    def delete_vlan(self, venue_id: str, switch_id: str, vlan_id: int) -> None:
        """
        Delete a VLAN from a switch.
        
        Args:
            venue_id: ID of the venue
            switch_id: ID of the switch
            vlan_id: ID of the VLAN to delete
            
        Raises:
            ResourceNotFoundError: If the switch or VLAN does not exist
        """
        logger.debug(f"Deleting VLAN {vlan_id} from switch {switch_id}")
        try:
            self.client.delete(
                f"/venues/{venue_id}/switches/{switch_id}/vlans/{vlan_id}"
            )
            logger.debug(f"VLAN deletion successful")
        except ResourceNotFoundError:
            logger.error(f"VLAN with ID {vlan_id} not found in switch {switch_id}")
            raise ResourceNotFoundError(
                message=f"VLAN with ID {vlan_id} not found in switch {switch_id}"
            )
        except Exception as e:
            logger.exception(f"Error deleting VLAN: {str(e)}")
            raise
    
    def get_statistics(self, venue_id: str, switch_id: str) -> Dict[str, Any]:
        """
        Get statistics for a switch.
        
        Args:
            venue_id: ID of the venue
            switch_id: ID of the switch
            
        Returns:
            Dict containing switch statistics
            
        Raises:
            ResourceNotFoundError: If the switch does not exist
        """
        try:
            return self.client.get(f"/venues/{venue_id}/switches/{switch_id}/statistics")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"Switch with ID {switch_id} not found in venue {venue_id}"
            )