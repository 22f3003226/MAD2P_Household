*Things left:*

 Cache
 Search functionality for all.
 Frontend
 Avg Rating for proffessionals

Checking against actual usage:

/api/logout - This endpoint is defined but doesn't do anything meaningful. The logout is handled on the frontend by removing the token.

/api/get_request/<int:service_id> - This route exists but isn't being used in any frontend component. The ServiceRequestApi.get() method exists but no frontend component actually calls this endpoint.

/api/create_request/<int:service_id> - This route exists but no frontend component is using it to create requests.


