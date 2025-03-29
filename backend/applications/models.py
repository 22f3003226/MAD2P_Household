from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(60), nullable=True)
    pincode = db.Column(db.Integer, nullable=True)
    role = db.Column(db.String(20), nullable=False) #customer, service_proff, admin
    status = db.Column(db.String(20), nullable=True, default='pending') #approved, rejected, blocked, pending
    last_seen = db.Column(db.Date, nullable=True, default=datetime.now())
    avg_rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    service_proffessional_file = db.Column(db.String(80), nullable=True)
    service_proffessional_experience = db.Column(db.String(20), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('householdServices.id', ondelete='SET NULL'), nullable=True) #bcoz our relationship with services table is 1 to many and 1 user can exist without a service
    service = db.relationship('HouseholdServices', back_populates='service_proffessionals') #2-way connection service_proffessionals(HouseholdServices Table) and service(User table)
    #One to Many relationship. 1 service will have many service_proffessionals but 1 service_proffessional can only have 1 service.
    
    #Relationship for requests customer made
    customer_requests = db.relationship('HouseholdServiceRequest', back_populates='customer', foreign_keys='HouseholdServiceRequest.customer_id')
    
    #Relationship for requests made to service proffessional
    service_proffessional_requests = db.relationship('HouseholdServiceRequest', back_populates='service_proffessional', foreign_keys='HouseholdServiceRequest.service_proffessional_id')

    def convert_to_json(self):
        return {'id': self.id, 'user_name': self.user_name, 'address': self.address, 'pincode': self.pincode, 'role': self.role, 'status': self.status, 'last_seen': self.last_seen, 'avg_rating': self.avg_rating, 'rating_count': self.rating_count, 'service_proffessional_file': self.service_proffessional_file, 'service_proffessional_experience': self.service_proffessional_experience, 'service_id': self.service_id}
    
class HouseholdServices(db.Model):
    __tablename__ = "householdServices"
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(20), unique=True, nullable=False)
    service_description = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Integer, nullable=True)
    time_required = db.Column(db.String(20), nullable=True)
    service_proffessionals = db.relationship('User', back_populates='service', cascade = 'all, delete') #2-way connection to user.service + if we delete-orphan, then all contractors related to deleted service will get deleted, 
    #but we want only the particular sevice_proff to get deleted
    request = db.relationship('HouseholdServiceRequest', back_populates='service', cascade = 'all, delete-orphan') #If any service is deleted, delete all the service requests associated with it.
    
    def convert_to_json(self):
        return {'id': self.id, 'service_name': self.service_name, 'service_description': self.service_description, 'base_price': self.base_price, 'time_required': self.time_required}

class HouseholdServiceRequest(db.Model):
    __tablename__ = 'householdServiceRequest'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('householdServices.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_proffessional_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    #req_type = db.Column(db.String(10), nullable=False) #private / public
    request_description = db.Column(db.Text, nullable=True) #request description, length of input can be long, so db.Text and not String
    request_status = db.Column(db.String(20), nullable=True) #pending / accepted / closed / rejected
    date_created = db.Column(db.Date, nullable=False, default=datetime.now().date())
    date_closed = db.Column(db.Date, nullable=True)
    rating_by_customer = db.Column(db.Float, default=0.0)
    review_by_customer = db.Column(db.String(20), nullable=True)
    service = db.relationship('HouseholdServices', back_populates='request')
    customer = db.relationship('User', back_populates='customer_requests', foreign_keys=[customer_id])
    service_proffessional = db.relationship('User', back_populates='service_proffessional_requests', foreign_keys=[service_proffessional_id])

    def convert_to_json(self):
        return {'id': self.id, 'service_id': self.service_id, 'customer_id': self.customer_id, 'service_proffessional_id': self.service_proffessional_id, 'request_description': self.request_description, 'request_status': self.request_status, 'date_created': self.date_created, 'date_closed': self.date_closed, 'rating_by_customer': self.rating_by_customer, 'review_by_customer': self.review_by_customer}

