<template>
    <div>
        <!-- Navigation -->
        <nav class="navbar bg-dark border-bottom border-body" data-bs-theme="dark">
            <div class="container-fluid">
                <div class="d-flex align-items-center justify-content-between w-100">
                    <div class="d-flex align-items-center">
                        <a class="navbar-brand me-3" href="#">Admin Dashboard</a>
                        <router-link to="/create-service" class="btn btn-sm btn-primary me-2">Create Service</router-link>
                        <a class="btn btn-sm btn-primary me-2" @click="exportdata">Export Data</a>
                        <router-link to="/summary" class="btn btn-sm btn-primary me-2">Summary</router-link>
                        <a class="btn btn-sm btn-primary" @click="logout">Logout</a>
                    </div>
                    <div class="d-flex align-items-center">
                        <select class="form-select form-select-sm me-2" v-model="searchField">
                            <option value="">Filter by</option>
                            <option value="username">Username</option>
                            <option value="pincode">Pincode</option>
                            <option value="address">Address</option>
                            <option value="role">Role</option>
                            <option value="service">Service Name</option>
                            <option value="status">Request Status</option>
                        </select>
                        <input type="text" 
                               class="form-control form-control-sm" 
                               v-model="searchTerm"
                               placeholder="Search...">
                    </div>
                </div>
            </div>
        </nav>

        <!-- Dashboard Content -->
        <div class="container mt-4">
            <!-- Services Table -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Services</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Description</th>
                                    <th>Price</th>
                                    <th>Time Required</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="service in displayedServices" :key="service.id">
                                    <td>{{ service.id }}</td>
                                    <td>{{ service.service_name }}</td>
                                    <td>
                                        <div v-if="editingService === service.id">
                                            <input type="text" class="form-control" v-model="service.service_description">
                                        </div>
                                        <span v-else>{{ service.service_description }}</span>
                                    </td>
                                    <td>
                                        <div v-if="editingService === service.id">
                                            <input type="number" class="form-control" v-model="service.base_price">
                                        </div>
                                        <span v-else>₹{{ service.base_price }}</span>
                                    </td>
                                    <td>
                                        <div v-if="editingService === service.id">
                                            <input type="text" class="form-control" v-model="service.time_required">
                                        </div>
                                        <span v-else>{{ service.time_required }}</span>
                                    </td>
                                    <td>
                                        <div v-if="editingService === service.id">
                                            <button class="btn btn-sm btn-success me-2" @click="editService(service)">Save</button>
                                            <button class="btn btn-sm btn-secondary" @click="editingService = null">Cancel</button>
                                        </div>
                                        <div v-else>
                                            <button class="btn btn-sm btn-primary me-2" @click="editingService = service.id">Edit</button>
                                            <button class="btn btn-sm btn-danger" @click="deleteService(service.id)">Delete</button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Users Table -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Users</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Username</th>
                                    <th>Role</th>
                                    <th>Status</th>
                                    <th>Last Seen</th>
                                    <th>Rating</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="user in displayedUsers" :key="user.id">
                                    <td>{{ user.id }}</td>
                                    <td>{{ user.user_name }}</td>
                                    <td>{{ user.role }}</td>
                                    <td>
                                        <span :class="getStatusBadgeClass(user.status)">{{ user.status }}</span>
                                    </td>
                                    <td>{{ formatDate(user.last_seen) }}</td>
                                    <td>
                                        <span v-if="user.role === 'service_proffessional'">
                                            {{ formatRating(user) }}
                                        </span>
                                        <span v-else>N/A</span>
                                    </td>
                                    <td v-if="user.role === 'service_proffessional' || user.role === 'customer'">
                                        <div v-if="user.status === 'pending' && user.role === 'service_proffessional'">
                                            <button @click="updateUserStatus(user.id, 'approve', user.role)"
                                                    class="btn btn-sm btn-success me-2">
                                                Approve
                                            </button>
                                            <button @click="updateUserStatus(user.id, 'reject', user.role)"
                                                    class="btn btn-sm btn-danger">
                                                Reject
                                            </button>
                                        </div>
                                        <button v-if="user.status === 'approved'"
                                                @click="updateUserStatus(user.id, 'block', user.role)"
                                                class="btn btn-sm btn-danger">
                                            Block
                                        </button>
                                        <button v-if="user.status === 'blocked'"
                                                @click="updateUserStatus(user.id, 'unblock', user.role)"
                                                class="btn btn-sm btn-primary">
                                            Unblock
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Service Requests Table -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Service Requests</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Service</th>
                                    <th>Customer</th>
                                    <th>Professional</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                    <th>Rating</th>
                                    <th>Review</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="request in displayedRequests" :key="request.id">
                                    <td>{{ request.id }}</td>
                                    <td>{{ request.service_name }}</td>
                                    <td>{{ request.customer_name }}</td>
                                    <td>{{ request.professional_name }}</td>
                                    <td>{{ request.request_status }} </td>
                                    <td>{{ request.date_created }}</td>
                                    <td>{{ request.rating_by_customer || 'N/A' }}</td>
                                    <td>{{ request.review_by_customer || 'N/A' }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            services: [],
            users: [],
            requests: [],
            editingService: null,
            errorMessage: null,
            searchField: '',
            searchTerm: '',
            filteredUsers: [],
            filteredServices: [],
            filteredRequests: []
        }
    },
    computed: {
        displayedUsers() {
            if (!this.searchTerm || !this.searchField) return this.users;
            
            const term = this.searchTerm.toLowerCase();
            return this.users.filter(user => {
                switch(this.searchField) {
                    case 'username':
                        return user.user_name.toLowerCase().includes(term);
                    case 'pincode':
                        return user.pincode?.toString() === term;
                    case 'address':
                        return user.address?.toLowerCase().includes(term);
                    case 'role':
                        return user.role.toLowerCase().includes(term);
                    default:
                        return true;
                }
            });
        },
        displayedServices() {
            if (!this.searchTerm || !this.searchField) return this.services;
            
            const term = this.searchTerm.toLowerCase();
            return this.services.filter(service => {
                if (this.searchField === 'service') {
                    return service.service_name.toLowerCase().includes(term);
                }
                return true;
            });
        },
        displayedRequests() {
            if (!this.searchTerm || !this.searchField) return this.requests;
            
            const term = this.searchTerm.toLowerCase();
            return this.requests.filter(request => {
                switch(this.searchField) {
                    case 'username':
                        return request.customer_name.toLowerCase().includes(term) || 
                               request.professional_name?.toLowerCase().includes(term);
                    case 'service':
                        return request.service_name.toLowerCase().includes(term);
                    case 'status':
                        return request.request_status.toLowerCase().includes(term);
                    default:
                        return true;
                }
            });
        }
    },
    methods: {
        async fetchDashboardData() {
            try {
                const response = await fetch('/api/dashboard', {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    this.services = data.services;
                    this.users = data.users;
                    this.requests = data.service_requests;
                }
            } catch (error) {
                console.error('Error fetching dashboard data:', error);
            }
        },
        async exportdata() {
            try {
                const response = await fetch('/api/export', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                    }
                });
                if (response.ok) {
                    alert('Data exported successfully!');
                }
            } catch (error) {
                console.error('Error exporting data:', error);
            }
        },
        async logout() {
            localStorage.removeItem('adminToken');
            this.$router.push('/');
        },
        async editService(service) {
            try {
                const response = await fetch(`/api/service/${service.id}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                    },
                    body: JSON.stringify({
                        service_description: service.service_description,
                        base_price: service.base_price.toString(),
                        time_required: service.time_required
                    })
                });

                if (response.ok) {
                    this.editingService = null;
                    await this.fetchDashboardData();
                } else {
                    const data = await response.json();
                    alert(data.message || 'Error updating service');
                }
            } catch (error) {
                console.error('Error updating service:', error);
            }
        },

        async deleteService(serviceId) {
            if (confirm('Are you sure you want to delete this service?')) {
                try {
                    const response = await fetch(`/api/service/${serviceId}`, {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                        }
                    });

                    if (response.ok) {
                        await this.fetchDashboardData();
                    } else {
                        const data = await response.json();
                        alert(data.message || 'Error deleting service');
                    }
                } catch (error) {
                    console.error('Error deleting service:', error);
                }
            }
        },
        getStatusBadgeClass(status) {
            switch (status) {
                case 'approved':
                    return 'badge bg-success';
                case 'pending':
                    return 'badge bg-warning';
                case 'blocked':
                    return 'badge bg-danger';
                case 'rejected':
                    return 'badge bg-secondary';
                default:
                    return 'badge bg-secondary';
            }
        },
        formatDate(date) {
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            return new Date(date).toLocaleDateString(undefined, options);
        },
        async updateProfessionalStatus(userId, action) {
            try {
                const response = await fetch(`/api/dashboard/${userId}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                    },
                    body: JSON.stringify({ action }) // Send action in request body
                });

                const data = await response.json();
                if (response.ok) {
                    alert(data.message);
                    await this.fetchDashboardData(); // Refresh data after successful update
                } else {
                    alert(data.message || 'Error updating professional status');
                }
            } catch (error) {
                console.error('Error updating professional status:', error);
                alert('Error connecting to server');
            }
        },
        async updateUserStatus(userId, action, role) {
            try {
                const response = await fetch(`/api/dashboard/${userId}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                    },
                    body: JSON.stringify({ action, role })
                });

                const data = await response.json();
                if (response.ok) {
                    alert(data.message);
                    await this.fetchDashboardData();
                } else {
                    alert(data.message || 'Error updating user status');
                }
            } catch (error) {
                console.error('Error updating user status:', error);
                alert('Error connecting to server');
            }
        },
        formatRating(user) {
            if (!user.avg_rating) return 'No ratings';
            return `${parseFloat(user.avg_rating).toFixed(1)} (${user.rating_count} reviews)`;
        },
    },
    mounted() {
        this.fetchDashboardData();
    }
}
</script>

<style scoped>
.nav-link {
    cursor: pointer;
}
.table-responsive {
    overflow-x: auto;
}
.badge {
    font-size: 0.85em;
}
.form-select, .form-control {
    max-width: 200px;
}
.navbar .container-fluid {
    padding: 0.5rem 1rem;
}
</style>
