import redis
from flask_caching import Cache
from flask import Flask, request
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager
from applications.models import db, User
from applications.interactions_api import ProfessionalsApi, SummaryApi, cache
from applications.interactions_api import CustomerRequestApi, DashboardApi, ServiceRequestApi, CloseServiceRequestApi, ExportAPI, ServiceRequestUpdateApi,ServiceApi
from applications.auth_api import GetServicesForSignupApi, LoginApi, SignupApi
from werkzeug.security import generate_password_hash,check_password_hash
from applications.worker import celery
from applications.task import daily_reminder, monthly_report
import os #,time

base_dir = os.path.abspath(os.path.dirname(__file__)) #Get the current directory of the file

app = Flask(__name__) #Create an instance of the Flask class

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, "A2Z.sqlite3") #ORM = Connects relational DB to objects in python (flask). This won't create an instance folder and create db within backend folder 
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///A2Z.sqlite3' #This will create an instance folder and store within that.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #To suppress the warning
app.config["SECRET_KEY"] = "super-secret-key" #To encrypt the session data
app.config['JWT_SECRET_KEY'] = 'super-duper-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 43200 #12 hours
app.config['PASSWORD_HASH'] = 'sha512' #To encrypt the password

# Redis Cache configuration
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300 #5 minutes

#cache = Cache(app) # Create an instance of the Cache class
cache.init_app(app) # Initialize the cache with the app

redis_client = redis.Redis(host='localhost', port=6379, db=0) # Create an instance of the Redis class

# Celery configuration

#app.config['CELERY_IMPORTS'] = ('applications.task') # List of modules to import when the worker starts

celery.conf.update(broker_url='redis://localhost:6379/0', 
                   result_backend='redis://localhost:6379/1',
                   timezone='Asia/Kolkata') # Update the celery configuration with the app configuration
#celery.init_app(app) # Initialize the celery with the app

db.init_app(app) # Initialize the db with the app
api = Api(app) # Create an instance of the Api class
jwt= JWTManager(app) # Create an instance of the JWTManager class
app.app_context().push() # Push the app context

def create_admin():
    admin = User.query.filter_by(role='admin').first() #We can use .one() also, but if there're no admins, it'll throw error.
    if admin is None:
        admin = User(user_name='admin', password=generate_password_hash('admin'), role='admin', status='approved')
        db.session.add(admin)
        db.session.commit()
        return "Admin created successfully."
    return "Admin already exists."

api.add_resource(LoginApi, '/api/login') #Add the LoginApi class to the api instance
api.add_resource(SignupApi, '/api/signup') #Add the RegisterApi class to the api instance
api.add_resource(GetServicesForSignupApi, '/api/signup/services')
#api.add_resource(LogoutApi, '/api/logout') #Add the LogoutApi class to the api instance
api.add_resource(DashboardApi, 
    '/api/dashboard', 
    '/api/dashboard/<int:userId>'
) #Add the DashboardApi class to the api instance
api.add_resource(ServiceApi, '/api/service', '/api/service/<int:service_id>') #Add the CreateServiceApi class to the api instance
api.add_resource(ServiceRequestApi, 
    '/api/get_request/<int:service_id>', 
    '/api/create_request/<int:service_id>'
) #Add the CreateServiceRequestApi class to the api instance
api.add_resource(CustomerRequestApi, '/api/customer_request/<int:request_id>')  # For customer operations
api.add_resource(ServiceRequestUpdateApi, '/api/request_status/<int:request_id>')  # For professional operations
api.add_resource(CloseServiceRequestApi, '/api/close_request/<int:request_id>')
api.add_resource(ExportAPI, '/api/export')
api.add_resource(ProfessionalsApi, '/api/professionals')
api.add_resource(SummaryApi, '/api/summary')

if __name__ == '__main__':
    #db.drop_all()
    db.create_all() #if my app is running in them main file only, then only run this. Other terminal se run nhi hoga. If it's imported to some other file and then ran, it won't run from there.
    create_admin()
    app.run(debug=True)