<template>
    <div>
        <nav class="navbar bg-dark border-bottom border-body" data-bs-theme="dark">
            <div class="container-fluid">
                <div class="d-flex align-items-center justify-content-between w-100">
                    <div class="d-flex align-items-center">
                        <a class="navbar-brand me-3" href="#">Customer Dashboard</a>
                        <router-link to="/summary" class="btn btn-sm btn-primary me-2">Summary</router-link>
                        <a class="btn btn-sm btn-primary" @click="logout">Logout</a>
                    </div>
                    <div class="d-flex align-items-center">
                        <select class="form-select form-select-sm me-2" v-model="searchField">
                            <option value="">Filter by</option>
                            <option value="service">Service Name</option>
                            <option value="pincode">Pincode</option>
                            <option value="address">Address</option>
                        </select>
                        <input type="text" 
                               class="form-control form-control-sm" 
                               v-model="searchTerm"
                               placeholder="Search...">
                    </div>
                </div>
            </div>
        </nav>

        <!-- Search Results -->
        <div v-if="searchTerm && searchField" class="container mt-4">
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Search Results</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Service Name</th>
                                    <th>Professional Name</th>
                                    <th>Address</th>
                                    <th>Pincode</th>
                                    <th>Rating</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="result in searchResults" :key="result.id">
                                    <td>{{ result.service_name }}</td>
                                    <td>{{ result.professional_name }}</td>
                                    <td>{{ result.address }}</td>
                                    <td>{{ result.pincode }}</td>
                                    <td>{{ formatRating(result) }}</td>
                                    <td>
                                        <button @click="goToCreateRequest(result.service_id)" 
                                                class="btn btn-sm btn-primary">
                                            Create Request
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <div class="container mt-4">
            <h4 class="mb-3">Available Services</h4>
            <div class="row">
                <div class="col-md-4 mb-4" v-for="service in services" :key="service.id">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">{{ service.service_name }}</h5>
                            <p class="card-text"><strong>Description:</strong> {{ service.service_description }}</p>
                            <div class="mb-3">
                                <strong>Base Price:</strong> ₹{{ service.base_price }}
                            </div>
                            <div class="mb-3">
                                <strong>Time Required:</strong> {{ service.time_required }}
                            </div>
                            <button @click="goToCreateRequest(service.id)" 
                                    class="btn btn-primary">
                                Create Request
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="container mt-4">
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">My Service Requests</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Service</th>
                                    <th>Professional</th>
                                    <th>Description</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                    <th>Rating</th>
                                    <th>Review</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="request in requests" :key="request.id">
                                    <td>{{ request.id }}</td>
                                    <td>{{ request.service_name }}</td>
                                    <td>{{ request.professional_name }}</td>
                                    <td>
                                        <div v-if="editingRequest === request.id">
                                            <input type="text" class="form-control" 
                                                   v-model="request.request_description">
                                        </div>
                                        <span v-else>{{ request.request_description }}</span>
                                    </td>
                                    <td>
                                        <span :class="getStatusBadgeClass(request.request_status)">
                                            {{ request.request_status }}
                                        </span>
                                    </td>
                                    <td>{{ formatDate(request.date_created) }}</td>
                                    <td>
                                        <div v-if="request.request_status === 'closed'">
                                            <div v-if="editingRating === request.id">
                                                <input type="number" class="form-control" min="1" max="5"
                                                       v-model="request.rating_by_customer">
                                            </div>
                                            <span v-else>{{ request.rating_by_customer || 'N/A' }}</span>
                                        </div>
                                    </td>
                                    <td>
                                        <div v-if="request.request_status === 'closed'">
                                            <div v-if="editingRating === request.id">
                                                <input type="text" class="form-control"
                                                       v-model="request.review_by_customer">
                                            </div>
                                            <span v-else>{{ request.review_by_customer || 'N/A' }}</span>
                                        </div>
                                    </td>
                                    <td>
                                        <!-- Actions for pending requests -->
                                        <div v-if="request.request_status === 'pending'">
                                            <button v-if="editingRequest === request.id"
                                                    @click="updateRequest(request)"
                                                    class="btn btn-sm btn-success me-2">
                                                Save
                                            </button>
                                            <button v-if="editingRequest === request.id"
                                                    @click="editingRequest = null"
                                                    class="btn btn-sm btn-secondary me-2">
                                                Cancel
                                            </button>
                                            <button v-else
                                                    @click="editingRequest = request.id"
                                                    class="btn btn-sm btn-primary me-2">
                                                Edit
                                            </button>
                                            <button @click="deleteRequest(request.id)"
                                                    class="btn btn-sm btn-danger">
                                                Delete
                                            </button>
                                        </div>
                                        <!-- Actions for accepted requests -->
                                        <div v-if="request.request_status === 'accepted'">
                                            <button @click="showRatingModal(request)"
                                                    class="btn btn-sm btn-primary">
                                                Close Request
                                            </button>
                                        </div>
                                        <!-- Actions for closed requests -->
                                        <div v-if="request.request_status === 'closed'">
                                            <button v-if="editingRating === request.id"
                                                    @click="updateRatingReview(request)"
                                                    class="btn btn-sm btn-success me-2">
                                                Save
                                            </button>
                                            <button v-if="editingRating === request.id"
                                                    @click="editingRating = null"
                                                    class="btn btn-sm btn-secondary">
                                                Cancel
                                            </button>
                                            <button v-else
                                                    @click="showRatingModal(request)"
                                                    class="btn btn-sm btn-primary">
                                                Rate & Review
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <div class="modal fade" id="ratingModal" tabindex="-1" ref="ratingModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Rate and Review Service</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Rating (1-5)</label>
                            <input type="number" class="form-control" v-model="tempRating" min="1" max="5">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Review</label>
                            <textarea class="form-control" v-model="tempReview" rows="3"></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" @click="submitRatingAndClose">Submit</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { Modal } from 'bootstrap'

export default {
    data() {
        return {
            requests: [],
            services: [], // Add this line
            editingRequest: null,
            editingRating: null,
            errorMessage: null,
            tempRating: null,
            tempReview: '',
            selectedRequest: null,
            ratingModal: null,
            searchField: '', // Add this line
            searchTerm: '', // Add this line
            searchResults: [], // Add this line
            professionals: [], // Will store all professionals data
        }
    },
    computed: {
        searchResults() {
            if (!this.searchTerm || !this.searchField) return [];
            
            const term = this.searchTerm.toLowerCase();
            const professionals = this.professionals;
            
            return professionals.filter(prof => {
                switch(this.searchField) {
                    case 'service':
                        return prof.service_name.toLowerCase().includes(term);
                    case 'pincode':
                        return prof.pincode?.toString() === term;
                    case 'address':
                        return prof.address?.toLowerCase().includes(term);
                    default:
                        return true;
                }
            });
        }
    },
    methods: {
        async fetchRequests() {
            try {
                const response = await fetch('/api/dashboard', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('customerToken')}`
                    }
                });
                const data = await response.json();
                console.log('Dashboard data:', data); // Add this line for debugging
                if (response.ok) {
                    this.requests = data.requests;
                    this.services = data.services;
                    console.log('Services:', this.services); // Add this line for debugging
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        },

        async updateRequest(request) {
            try {
                const response = await fetch(`/api/customer_request/${request.id}`, {  // Updated endpoint
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('customerToken')}`
                    },
                    body: JSON.stringify({
                        request_description: request.request_description
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    this.editingRequest = null;
                    await this.fetchRequests();
                    alert(data.message);
                } else {
                    alert(data.message || 'Error updating request');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        },

        async deleteRequest(requestId) {
            if (confirm('Are you sure you want to delete this request?')) {
                try {
                    const response = await fetch(`/api/customer_request/${requestId}`, {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('customerToken')}`
                        }
                    });

                    const data = await response.json();
                    if (response.ok) {
                        await this.fetchRequests();
                        alert(data.message);
                    } else {
                        alert(data.message || 'Error deleting request');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            }
        },

        async updateRatingReview(request) {
            if (!request.rating_by_customer || request.rating_by_customer < 1 || request.rating_by_customer > 5) {
                alert('Please provide a rating between 1 and 5');
                return;
            }

            try {
                const response = await fetch(`/api/close_request/${request.id}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('customerToken')}`
                    },
                    body: JSON.stringify({
                        rating: request.rating_by_customer,
                        review: request.review_by_customer || ''
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    this.editingRating = null;
                    await this.fetchRequests();
                    alert(data.message);
                } else {
                    alert(data.message || 'Error updating rating and review');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        },

        getStatusBadgeClass(status) {
            switch (status) {
                case 'pending': return 'badge bg-warning';
                case 'accepted': return 'badge bg-success';
                case 'rejected': return 'badge bg-danger';
                case 'closed': return 'badge bg-secondary';
                default: return 'badge bg-secondary';
            }
        },

        formatDate(date) {
            if (!date) return 'N/A';
            return new Date(date).toLocaleDateString();
        },

        async logout() {
            localStorage.removeItem('customerToken');
            this.$router.push('/');
        },

        showRatingModal(request) {
            this.selectedRequest = request;
            this.tempRating = null;
            this.tempReview = '';
            if (!this.ratingModal) {
                this.ratingModal = new Modal(this.$refs.ratingModal);
            }
            this.ratingModal.show();
        },

        async submitRatingAndClose() {
            if (!this.tempRating || this.tempRating < 1 || this.tempRating > 5) {
                alert('Please provide a rating between 1 and 5');
                return;
            }

            try {
                const response = await fetch(`/api/close_request/${this.selectedRequest.id}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('customerToken')}`
                    },
                    body: JSON.stringify({
                        rating: this.tempRating,
                        review: this.tempReview
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    this.ratingModal.hide();
                    await this.fetchRequests();
                    alert(data.message);
                } else {
                    alert(data.message || 'Error closing request');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        },

        goToCreateRequest(serviceId) {
            this.$router.push({
                name: 'create-service-request',
                params: { serviceId: serviceId }
            });
        },

        formatRating(professional) {
            if (!professional.avg_rating) return 'No ratings';
            return `${parseFloat(professional.avg_rating).toFixed(1)} (${professional.rating_count} reviews)`;
        },
    
        async fetchProfessionals() {
            try {
                const response = await fetch('/api/professionals', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('customerToken')}`
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    this.professionals = data.professionals;
                }
            } catch (error) {
                console.error('Error fetching professionals:', error);
            }
        }
    },
    mounted() {
        this.fetchRequests();
        this.fetchProfessionals();
    }
}
</script>

<style scoped>
.badge {
    padding: 0.5em 1em;
}
.table-responsive {
    overflow-x: auto;
}
.card {
    transition: transform 0.2s;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.card:hover {
    transform: translateY(-5px);
}
</style>
