from datetime import datetime
import time
from flask import request, current_app as app
from flask_caching import Cache
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from applications.models import db, User, HouseholdServices, HouseholdServiceRequest
from applications.task import data_export
from matplotlib import use
import matplotlib.pyplot as plt
import seaborn as sns
import os

use('Agg')
#from main import cache
#from werkzeug.security import check_password_hash, generate_password_hash

cache = Cache()
# 200-OK, 201-Created a new record, 400-Bad Request, 401-Unauthorized, 404-Not Found, 403-Forbidden, 405-Method Not Allowed, 500-Internal Server Error

# Dashboard API with RBAC
class DashboardApi(Resource):
    @jwt_required()
    #@cache.cached(timeout=120) # Cache the response for 2 minutes
    def get(self):
        #time.sleep(10) #If we uncomment this, we will see results on dashboard after 10 secs. 
        # But, if we also uncomment line 18, first time it'll take 10 secs but for the next 2 mins, it'll be cached and will load instantaneously.
        current_user = get_jwt_identity()
        print(current_user)
        #user = User.query.filter_by(user_name=current_user['username']).first()
        if current_user['role'] == 'admin':
            all_users = User.query.all()
            all_services = HouseholdServices.query.all()
            all_service_requests = HouseholdServiceRequest.query.all()

            # Convert datetime objects to strings
            users_data = [{
                'id': user.id,
                'user_name': user.user_name,
                'role': user.role,
                'status': user.status,
                'last_seen': user.last_seen.strftime('%Y-%m-%d %H:%M:%S') if user.last_seen else None,
                'avg_rating': user.avg_rating if user.role == 'service_proffessional' else None,
                'rating_count': user.rating_count if user.role == 'service_proffessional' else None
            } for user in all_users]

            services_data = [{
                'id': service.id,
                'service_name': service.service_name,
                'service_description': service.service_description,
                'base_price': service.base_price,
                'time_required': service.time_required
            } for service in all_services]

            requests_data = [{
                'id': req.id,
                'service_name': req.service.service_name,
                'customer_name': req.customer.user_name,
                'professional_name': req.service_proffessional.user_name,
                'request_status': req.request_status,
                'date_created': req.date_created.strftime('%Y-%m-%d %H:%M:%S') if req.date_created else None,
                'rating_by_customer': req.rating_by_customer,
                'review_by_customer': req.review_by_customer
            } for req in all_service_requests]

            return {
                'users': users_data,
                'services': services_data,
                'service_requests': requests_data
            }, 200
        
        elif current_user['role'] == 'customer':
            user = User.query.filter_by(user_name=current_user['user']).first()
            
            # Get services that have at least one approved professional
            services = HouseholdServices.query.join(User).filter(
                User.role == 'service_proffessional',
                User.status == 'approved'
            ).distinct().all()
            
            requests = HouseholdServiceRequest.query.filter_by(customer_id=user.id).all()
            
            # Convert services to JSON
            services_data = [{
                'id': service.id,
                'service_name': service.service_name,
                'service_description': service.service_description,
                'base_price': service.base_price,
                'time_required': service.time_required
            } for service in services]
            
            # Convert requests to JSON with date formatting
            requests_data = [{
                'id': req.id,
                'service_name': req.service.service_name,
                'request_description': req.request_description,
                'request_status': req.request_status,
                'professional_name': req.service_proffessional.user_name if req.service_proffessional else None,
                'date_created': req.date_created.strftime('%Y-%m-%d') if req.date_created else None,
                'date_closed': req.date_closed.strftime('%Y-%m-%d') if req.date_closed else None,
                'rating_by_customer': req.rating_by_customer,
                'review_by_customer': req.review_by_customer
            } for req in requests]
            
            return {
                'services': services_data,
                'requests': requests_data
            }, 200
            
        elif current_user['role'] == 'service_proffessional':
            user = User.query.filter_by(user_name=current_user['user']).first()
            all_requests = HouseholdServiceRequest.query.filter_by(service_proffessional_id=user.id).all()
            pending_requests = HouseholdServiceRequest.query.filter_by(service_proffessional_id=user.id, request_status='pending').all()
            
            # Convert requests to JSON with proper date formatting
            all_requests_json = [{
                'id': req.id,
                'service_name': req.service.service_name,
                'customer_name': req.customer.user_name,
                'request_description': req.request_description,
                'request_status': req.request_status,
                'date_created': req.date_created.strftime('%Y-%m-%d') if req.date_created else None,
                'rating_by_customer': req.rating_by_customer,
                'review_by_customer': req.review_by_customer
            } for req in all_requests]

            pending_requests_json = [{
                'id': req.id,
                'service_name': req.service.service_name,
                'customer_name': req.customer.user_name,
                'request_description': req.request_description,
                'date_created': req.date_created.strftime('%Y-%m-%d') if req.date_created else None
            } for req in pending_requests]

            return {
                'all_requests': all_requests_json,
                'pending_requests': pending_requests_json
            }, 200
            
        return {'message': 'Unauthorized.'}, 401
    
    @jwt_required()
    def patch(self, userId):
        data = request.get_json()
        action = data.get('action')
        role = data.get('role')
    
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'message': 'Only Admin can manage users.'}, 403
    
        user = User.query.filter_by(id=userId).first()
        if not user:
            return {'message': 'User not found.'}, 404

        user_type = 'Professional' if role == 'service_proffessional' else 'Customer'

        if action == 'approve' and user.status == 'pending':
            user.status = 'approved'
            message = f'{user_type} approved successfully.'
        elif action == 'reject' and user.status == 'pending':
            user.status = 'rejected'
            message = f'{user_type} rejected successfully.'
        elif action == 'block' and user.status == 'approved':
            user.status = 'blocked'
            message = f'{user_type} blocked successfully.'
        elif action == 'unblock' and user.status == 'blocked':
            user.status = 'approved'
            message = f'{user_type} unblocked successfully.'
        else:
            return {'message': f'Invalid action "{action}" for current status "{user.status}".'}, 400

        db.session.commit()
        return {'message': message}, 200
    
    # @jwt_required()
    # # Admin approves service proffessional
    # def patch(self, service_proffessional_id): #Approvoing Service Proffessional
    #     data = request.get_json()
    #     action = data.get('action')  # 'approve', 'block', or 'unblock'
        
    #     current_user = get_jwt_identity()
    #     if current_user['role'] != 'admin':
    #         return {'message': 'Only Admin can manage professionals.'}, 403
        
    #     proff = User.query.filter_by(id=service_proffessional_id).first()
    #     if not proff:
    #         return {'message': 'Professional not found.'}, 404

    #     if action == 'approve' and proff.status == 'pending':
    #         proff.status = 'approved'
    #         message = 'Professional approved successfully.'
    #     elif action == 'block' and proff.status == 'approved':
    #         proff.status = 'blocked'
    #         message = 'Professional blocked successfully.'
    #     elif action == 'unblock' and proff.status == 'blocked':
    #         proff.status = 'approved'
    #         message = 'Professional unblocked successfully.'
    #     else:
    #         return {'message': 'Invalid action for current status.'}, 400

    #     db.session.commit()
    #     return {'message': message}, 200    

# Admin Service create and update API with CRUD operations
class ServiceApi(Resource):
    @jwt_required()
    #@cache.cached(timeout=30) # Cache the response for 5 minutes
    def get(self): # Get all services (/api/service)
        services = HouseholdServices.query.all() # this is a list of services-alchemy-obj
        services_json = []
        for service in services: #Converting to a list of dictionaries
            services_json.append(service.convert_to_json())
        return {'services': services_json}, 200
        
    
    @jwt_required()
    def post(self): # Create a new service (/api/service)
        data = request.get_json()
        service_name = data.get('service_name')  
        service_description = data.get('service_description')
        base_price = data.get('base_price')
        time_required = data.get('time_required')

        if not (data.get('service_name') and data.get('service_description') and data.get('base_price') and data.get('time_required')):
            return {'message': 'All fields are required.'}, 400
        if (len(service_name.strip()) < 4 or len(service_description.strip()) < 4) or (len(service_name.strip()) > 20):
            return {'message': 'Invalid data, check maximum and minimum length restrictions for all fields.'}, 400
        if not (base_price.strip().isdigit()):
            return {'message': 'Base Price should be numbers.'}, 400  

        current_user = get_jwt_identity()  
        #user = User.query.filter_by(user_name=current_user['username']).first()
        #if user.role == 'service_proffessional' or user.role == 'customer':
        if current_user['role'] != 'admin':
            return {'message': 'Only Admin can create services.'}, 403
        service = HouseholdServices.query.filter_by(service_name=service_name).first()
        if service:
            return {'message': 'Service already exists.'}, 400
        new_service = HouseholdServices(service_name=service_name.strip(), service_description=service_description.strip(), base_price=base_price, time_required=time_required)
        db.session.add(new_service)
        db.session.commit()
        return {'message': 'Service created successfully.'}, 201   
    
    @jwt_required()
    def patch(self, service_id): # Update a service (/api/service/<int:service_id>)
        data = request.get_json()
        service_description = data.get('service_description')
        base_price = data.get('base_price')
        time_required = data.get('time_required')

        if (len(service_description.strip()) < 4):
            return {'message': 'Invalid data, check maximum and minimum length restrictions for all fields.'}, 400
        if not (base_price.strip().isdigit()):
            return {'message': 'Base Price should be numbers.'}, 400

        current_user = get_jwt_identity()  
        #user = User.query.filter_by(user_name=current_user['username']).first()
        if current_user['role'] == 'admin':
            service = HouseholdServices.query.filter_by(id=service_id).first()
            if not service:
                return {'message': 'Service not found.'}, 404
            service.service_description = service_description.strip()
            service.base_price = base_price
            service.time_required = time_required
            db.session.commit()
            return {'message': 'Service updated successfully.'}, 200
        return {'message': 'Only Admin can update services.'}, 403  

    @jwt_required()
    def delete(self, service_id): # Delete a service (/api/service/<int:service_id>)
        current_user = get_jwt_identity()  
        #user = User.query.filter_by(user_name=current_user['username']).first()
        if current_user['role'] == 'admin':
            service = HouseholdServices.query.filter_by(id=service_id).first()
            if not service: 
                return {'message': 'Service not found.'}, 404
            db.session.delete(service)
            db.session.commit()
            return {'message': 'Service deleted successfully.'}, 200
        return {'message': 'Only Admin can delete services.'}, 403 
    
# Customer Create and Update Service Request API
class ServiceRequestApi(Resource):
    @jwt_required()
    #@cache.cached(timeout=300) # Cache the response for 5 minutes
    def get(self, service_id):
        service = HouseholdServices.query.get_or_404(service_id)
        service_proff = User.query.filter_by(
            role='service_proffessional', 
            service_id=service_id, 
            status='approved'
        ).all()
        
        # Format the response data
        service_data = {
            'id': service.id,
            'service_name': service.service_name,
            'service_description': service.service_description,
            'base_price': service.base_price,
            'time_required': service.time_required
        }
        
        professionals_data = [{
            'id': prof.id,
            'user_name': prof.user_name
        } for prof in service_proff]
        
        return {
            'service': service_data,
            'professionals': professionals_data
        }, 200

    @jwt_required()
    def post(self, service_id): # Create a new service request (/api/create_request/<int:service_id>)
        data = request.get_json()
        #service_id = data.get('service_id')
        request_description = data.get('request_description')
        service_proffessional_name = data.get('service_proffessional_name')

        if not (data.get('request_description') and data.get('service_proffessional_name')):
            return {'message': 'All fields are required.'}, 400
        if (len(request_description.strip()) < 4):
            return {'message': 'Invalid data, check maximum and minimum length restrictions for all fields.'}, 400

        current_user = get_jwt_identity()  
        user = User.query.filter_by(user_name=current_user['user']).first()
        if current_user['role'] == 'customer':
            service = HouseholdServices.query.filter_by(id=service_id).first()
            if not service:
                return {'message': 'Service not found.'}, 404
            service_proffessional = User.query.filter_by(user_name=service_proffessional_name, role='service_proffessional').first()
            new_service_request = HouseholdServiceRequest(service_id=service_id, customer_id=user.id, service_proffessional_id=service_proffessional.id, 
                                                          request_description=request_description, request_status='pending',
                                                          date_created=datetime.now().date())
            db.session.add(new_service_request)
            db.session.commit()
            return {'message': 'Service request created successfully.'}, 201
        return {'message': 'Only customer can create service request.'}, 403

class CloseServiceRequestApi(Resource): # /api/close_request/<int:request_id>
    @jwt_required()
    def patch(self, request_id):
        data = request.get_json()
        rating = data.get('rating')
        review = data.get('review')

        if not rating or not review:
            return {'message': 'Rating and review are required.'}, 400
        
        if not (1 <= int(rating) <= 5):
            return {'message': 'Rating must be between 1 and 5.'}, 400

        current_user = get_jwt_identity()
        if current_user['role'] == 'customer':
            service_request = HouseholdServiceRequest.query.filter_by(id=request_id).first()
            proff = User.query.filter_by(id=service_request.service_proffessional_id).first()
            if not service_request:
                return {'message': 'Service request not found.'}, 404
                
            service_request.request_status = 'closed'
            service_request.rating_by_customer = rating
            service_request.review_by_customer = review.strip()
            service_request.date_closed = datetime.now().date()
            # Increases rating_count first ; uses (rating_count - 1) in calculating new average cuz we need old count for proper avging
            proff.rating_count += 1
            proff.avg_rating = (proff.avg_rating * (proff.rating_count - 1) + int(rating)) / proff.rating_count
            db.session.commit()
            return {'message': 'Service request closed successfully.'}, 200
            
        return {'message': 'Only customer can close service request.'}, 403
    


class ExportAPI(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        if current_user['role'] == 'admin':
            data_export() 
            # alert of some type
            return {'message': 'Data exported successfully.'}, 200
        return {'message': 'Only admin can export data.'}, 403

class ServiceRequestUpdateApi(Resource):
    @jwt_required()
    def patch(self, request_id):
        data = request.get_json()
        action = data.get('action')

        current_user = get_jwt_identity()
        if current_user['role'] != 'service_proffessional':
            return {'message': 'Only service professionals can update request status.'}, 403

        service_request = HouseholdServiceRequest.query.filter_by(
            id=request_id, 
            service_proffessional_id = User.query.filter_by(user_name=current_user['user']).first().id,  # get service proffessional id from jwt token
        ).first()

        if not service_request:
            return {'message': 'Service request not found.'}, 404

        if service_request.request_status != 'pending':
            return {'message': 'Can only update pending requests.'}, 400

        if action == 'accept':
            service_request.request_status = 'accepted'
            message = 'Service request accepted successfully.'
        elif action == 'reject':
            service_request.request_status = 'rejected'
            message = 'Service request rejected successfully.'
        else:
            return {'message': 'Invalid action.'}, 400

        db.session.commit()
        return {'message': message}, 200

class CustomerRequestApi(Resource):
    @jwt_required()
    def patch(self, request_id):
        data = request.get_json()
        request_description = data.get('request_description')

        current_user = get_jwt_identity()
        if current_user['role'] != 'customer':
            return {'message': 'Only customers can update their requests.'}, 403

        service_request = HouseholdServiceRequest.query.filter_by(
            id=request_id,
            customer_id=User.query.filter_by(user_name=current_user['user']).first().id
        ).first()

        if not service_request:
            return {'message': 'Request not found.'}, 404

        if service_request.request_status != 'pending':
            return {'message': 'Can only update pending requests.'}, 400

        service_request.request_description = request_description
        db.session.commit()
        return {'message': 'Request updated successfully.'}, 200

    @jwt_required()
    def delete(self, request_id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'customer':
            return {'message': 'Only customers can delete their requests.'}, 403

        service_request = HouseholdServiceRequest.query.filter_by(
            id=request_id,
            customer_id=User.query.filter_by(user_name=current_user['user']).first().id
        ).first()

        if not service_request:
            return {'message': 'Request not found.'}, 404

        if service_request.request_status != 'pending':
            return {'message': 'Can only delete pending requests.'}, 400

        db.session.delete(service_request)
        db.session.commit()
        return {'message': 'Request deleted successfully.'}, 200

class ProfessionalsApi(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        if current_user['role'] == 'customer':
            professionals = User.query.filter_by(
                role='service_proffessional',
                status='approved'
            ).all()
            
            professionals_data = [{
                'id': prof.id,
                'professional_name': prof.user_name,
                'service_id': prof.service_id,
                'service_name': prof.service.service_name if prof.service else None,
                'address': prof.address,
                'pincode': prof.pincode,
                'avg_rating': prof.avg_rating,
                'rating_count': prof.rating_count
            } for prof in professionals]
            
            return {'professionals': professionals_data}, 200
        return {'message': 'Unauthorized'}, 403
    
class SummaryApi(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        if current_user['role'] == 'admin':    
            # Count approved professionals only
            service_professional_count = User.query.filter_by(
                role='service_proffessional',
                status='approved'
            ).count()
            
            # Count all customers
            customer_count = User.query.filter_by(role='customer').count()
            
            # Get request counts
            request_counts = {
                'pending': HouseholdServiceRequest.query.filter_by(request_status='pending').count(),
                'accepted': HouseholdServiceRequest.query.filter_by(request_status='accepted').count(),
                'rejected': HouseholdServiceRequest.query.filter_by(request_status='rejected').count(),
                'closed': HouseholdServiceRequest.query.filter_by(request_status='closed').count()
            }

            # Create plots
            plt.clf()  # Clear any existing plots
            
            # User roles plot
            plt.figure(figsize=(8, 6))
            roles = ['Customers', 'Service Professionals']
            counts = [customer_count, service_professional_count]
            sns.barplot(x=roles, y=counts)
            plt.title('Number of Users by Role')
            plt.savefig('/home/shiba/mad-2p/frontend/src/assets/image_1.png')
            plt.close()

            # Request status plot
            plt.figure(figsize=(8, 6))
            statuses = ['Pending', 'Accepted', 'Rejected', 'Closed']
            status_counts = [request_counts['pending'], request_counts['accepted'], 
                           request_counts['rejected'], request_counts['closed']]
            plt.pie(status_counts, labels=statuses, autopct='%1.1f%%', 
                   colors=['#2196f3', '#4caf50', '#f44336', '#ff9800'])
            plt.title('Service Requests by Status')
            plt.savefig('/home/shiba/mad-2p/frontend/src/assets/image_2.png')
            plt.close()

            return {
                'message': 'Summary generated successfully',
                'role': current_user['role'],
                'data': {
                    'customer_count': customer_count,
                    'service_professional_count': service_professional_count,
                    'request_counts': request_counts
                }
            }, 200
        
        elif current_user['role'] == 'customer':
            cust_id = User.query.filter_by(user_name=current_user['user']).first().id
            pending_request_count = HouseholdServiceRequest.query.filter_by(customer_id=cust_id, request_status='pending').count()
            accepted_request_count = HouseholdServiceRequest.query.filter_by(customer_id=cust_id, request_status='accepted').count()
            rejected_request_count = HouseholdServiceRequest.query.filter_by(customer_id=cust_id, request_status='rejected').count()
            closed_request_count = HouseholdServiceRequest.query.filter_by(customer_id=cust_id, request_status='closed').count()
            
            # Create the pie chart
            image_3 = os.path.join('/home/shiba/mad-2p/frontend/src/assets', 'image_3.png')
            status = ['Pending requests', 'Accepted requests', 'Rejected requests', 'Closed requests']
            count = [pending_request_count, accepted_request_count, rejected_request_count, closed_request_count]
            plt.clf()
            plt.figure(figsize=(8, 6))
            plt.pie(count, labels=status, autopct='%1.1f%%', colors=['#4caf50', '#f44336', '#ff9800', '#2196f3'], shadow=True, startangle=90)
            plt.title('Number of requests by status')
            plt.savefig(image_3, format='png')
            plt.close()

            request_counts = {
                'pending': pending_request_count,
                'accepted': accepted_request_count,
                'rejected': rejected_request_count,
                'closed': closed_request_count
            }

            return {
                'message': 'Summary generated successfully',
                'role': current_user['role'],
                'data': {
                    'request_counts': request_counts
                }
            }, 200

        elif current_user['role'] == 'service_proffessional':
            proff_id = User.query.filter_by(user_name=current_user['user']).first().id    
            pending_request_count = HouseholdServiceRequest.query.filter_by(service_proffessional_id=proff_id, request_status='pending').count()
            accepted_request_count = HouseholdServiceRequest.query.filter_by(service_proffessional_id=proff_id, request_status='accepted').count()
            rejected_request_count = HouseholdServiceRequest.query.filter_by(service_proffessional_id=proff_id, request_status='rejected').count()
            closed_request_count = HouseholdServiceRequest.query.filter_by(service_proffessional_id=proff_id, request_status='closed').count()
            
            # Create the pie chart
            image_4 = os.path.join('/home/shiba/mad-2p/frontend/src/assets', 'image_4.png')
            status = ['Pending requests', 'Accepted requests', 'Rejected requests', 'Closed requests']
            count = [pending_request_count, accepted_request_count, rejected_request_count, closed_request_count]
            plt.clf()
            plt.figure(figsize=(8, 6))
            plt.pie(count, labels=status, autopct='%1.1f%%', colors=['#4caf50', '#f44336', '#ff9800', '#2196f3'], shadow=True, startangle=90)
            plt.title('Number of requests by status')
            plt.savefig(image_4, format='png')
            plt.close()

            request_counts = {
                'pending': pending_request_count,
                'accepted': accepted_request_count,
                'rejected': rejected_request_count,
                'closed': closed_request_count
            }

            return {
                'message': 'Summary generated successfully',
                'role': current_user['role'],
                'data': {
                    'request_counts': request_counts
                }
            }, 200

        return {'message': 'Unauthorized'}, 403



