from flask import request, current_app as app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from applications.models import db, User, HouseholdServices
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# 200-OK, 201-Created a new record, 400-Bad Request, 401-Unauthorized, 404-Not Found, 403-Forbidden, 405-Method Not Allowed, 500-Internal Server Error

class LoginApi(Resource):
    def post(self): #we're getinng data from frotnend, so we use post.
        data = request.get_json() # == request.json
        username = data.get('username')
        password = data.get('password')
        
        if not (data.get('username') and data.get('password')):
            return {'message': 'All fields are required.'}, 400
        
        user = User.query.filter_by(user_name=username).first()
        if user:
            if user.role == 'service_proffessional':
                if user.status == 'pending' and check_password_hash(user.password, password):
                    return {'message': 'User is not approved yet.'}, 403
                elif user.status == 'blocked' and check_password_hash(user.password, password):
                    return {'message': 'User is blocked.'}, 403
                elif user.status == 'approved' and check_password_hash(user.password, password):
                    #session['id'] = user.id
                    #session['role'] = user.role
                    #session['user'] = user.user_name
                    #print(session)
                    user.last_seen = datetime.now() # Updating Last Seen time
                    db.session.commit()
                    token = create_access_token({'role': user.role, 'user': user.user_name})
                    return {'message': 'Service proff logged in successfully.', 'token': token, 'username': user.user_name, 'role': user.role}, 200
                return {'message': 'Invalid password.'}, 401
            elif user.role == 'customer':
                if user.status == 'approved' and check_password_hash(user.password, password):
                    #session['id'] = user.id
                    #session['role'] = user.role
                    #session['user'] = user.user_name
                    #print(session)
                    #user.last_seen = datetime.now() #Update the last seen time of the user
                    db.session.commit()
                    token = create_access_token({'role': user.role, 'user': user.user_name})
                    return {'message': 'Customer logged in successfully.', 'token': token, 'username': user.user_name, 'role': user.role}, 200
                elif user.status == 'blocked' and check_password_hash(user.password, password):
                    return {'message': 'User is blocked.'}, 403
                return {'message': 'Invalid password.'}, 401
            elif user.role == 'admin' and check_password_hash(user.password, password):
                #session['id'] = user.id
                #session['role'] = user.role
                #session['user'] = user.user_name
                #print(session)
                token = create_access_token({'role': user.role, 'user': user.user_name})
                user.last_seen = datetime.now()
                db.session.commit()
                return {'message': 'Admin logged in successfully.', 'token': token, 'username': user.user_name, 'role': user.role}, 200
        return {'message': 'User not found.'}, 404
    
    
class SignupApi(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        address = data.get('address')
        pincode = data.get('pincode')
        service_proffessional_experience = data.get('service_proffessional_experience')

        # Adding validation. In case, a machine requests data, only frontend validation will not work.
        if not (data.get('username') and data.get('password') and data.get('role') and data.get('address') and data.get('pincode')):
            return {'message': 'All fields are required.'}, 400
        if (len(username.strip()) < 4 or len(password.strip()) < 4) or (len(username.strip()) > 20 or len(password.strip()) > 20) or (len(address.strip()) < 4 or len(address.strip()) > 60):
            return {'message': 'Invalid data, check maximum and minimum length restrictions for all fields.'}, 400
        if role not in ['customer', 'service_proffessional']:
            return {'message': 'Invalid role.'}, 400
        
        user = User.query.filter_by(user_name=username).first() 
        if user:
            return {'message': 'User already exists.'}, 400
        if role == 'customer':
            new_user = User(user_name=username.strip(), password=generate_password_hash(password), role=role, status='approved', address=address.strip(), pincode=pincode)
        elif role == 'service_proffessional':
            service_id = data.get('service_id')
            s_id = HouseholdServices.query.filter_by(id=service_id).first().id
            if not (data.get('service_proffessional_experience') or data.get('service_id')):
                return {'message': 'All fields are required.'}, 400
            if (len(service_proffessional_experience.strip()) < 4 or len(service_proffessional_experience.strip()) > 20):
                return {'message': 'Invalid data, check maximum and minimum length restrictions for all fields.'}, 400
                
            new_user = User(user_name=username.strip(), password=generate_password_hash(password), role=role.strip(), status='pending', address=address.strip(), pincode=pincode, service_proffessional_experience=service_proffessional_experience.strip(), service_id=s_id)
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully.'}, 201 

# Add this new class after existing APIs
class GetServicesForSignupApi(Resource):
    def get(self):
        services = HouseholdServices.query.all()
        return {'services': [{'id': service.id, 'service_name': service.service_name} for service in services]}, 200

# In main.py, add this route:


# Logout API
# class LogoutApi(Resource):
#     @jwt_required()
#     def get(self):
#         #session.clear()
        
#         return {'message': 'User logged out successfully.'}, 200