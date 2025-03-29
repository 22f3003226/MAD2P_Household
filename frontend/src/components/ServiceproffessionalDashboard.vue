<template>
    <div>
        <nav class="navbar bg-dark border-bottom border-body" data-bs-theme="dark">
            <div class="container-fluid">
                <div class="d-flex align-items-center">
                    <a class="navbar-brand me-3" href="#">Professional Dashboard</a>
                    <router-link to="/summary" class="btn btn-sm btn-primary me-2">Summary</router-link>
                    <a class="btn btn-sm btn-primary" @click="logout">Logout</a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <!-- Pending Requests Table -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Pending Requests</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Service</th>
                                    <th>Customer</th>
                                    <th>Description</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="request in pendingRequests" :key="request.id">
                                    <td>{{ request.id }}</td>
                                    <td>{{ request.service_name }}</td>
                                    <td>{{ request.customer_name }}</td>
                                    <td>{{ request.request_description }}</td>
                                    <td>{{ formatDate(request.date_created) }}</td>
                                    <td>
                                        <button @click="updateRequestStatus(request.id, 'accept')"
                                                class="btn btn-sm btn-success me-2">
                                            Accept
                                        </button>
                                        <button @click="updateRequestStatus(request.id, 'reject')"
                                                class="btn btn-sm btn-danger">
                                            Reject
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- All Requests Table -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">All Requests</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Service</th>
                                    <th>Customer</th>
                                    <th>Description</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                    <th>Rating</th>
                                    <th>Review</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="request in allRequests" :key="request.id">
                                    <td>{{ request.id }}</td>
                                    <td>{{ request.service_name }}</td>
                                    <td>{{ request.customer_name }}</td>
                                    <td>{{ request.request_description }}</td>
                                    <td>
                                        <span :class="getStatusBadgeClass(request.request_status)">
                                            {{ request.request_status }}
                                        </span>
                                    </td>
                                    <td>{{ formatDate(request.date_created) }}</td>
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
            allRequests: [],
            pendingRequests: [],
            errorMessage: null
        }
    },
    methods: {
        async fetchDashboardData() {
            try {
                const response = await fetch('/api/dashboard', {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('proffessionalToken')}`
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    this.allRequests = data.all_requests;
                    this.pendingRequests = data.pending_requests;
                }
            } catch (error) {
                console.error('Error fetching dashboard data:', error);
            }
        },

        async updateRequestStatus(requestId, action) {
            try {
                const response = await fetch(`/api/request_status/${requestId}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('proffessionalToken')}`
                    },
                    body: JSON.stringify({ action })
                });

                const data = await response.json();
                if (response.ok) {
                    alert(data.message);
                    await this.fetchDashboardData();
                } else {
                    alert(data.message || 'Error updating request status');
                }
            } catch (error) {
                console.error('Error updating request status:', error);
                alert('Error connecting to server');
            }
        },

        getStatusBadgeClass(status) {
            switch (status) {
                case 'accepted':
                    return 'badge bg-success';
                case 'pending':
                    return 'badge bg-warning';
                case 'rejected':
                    return 'badge bg-danger';
                case 'closed':
                    return 'badge bg-secondary';
                default:
                    return 'badge bg-secondary';
            }
        },

        formatDate(date) {
            if (!date) return 'N/A';
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            return new Date(date).toLocaleDateString(undefined, options);
        },

        async logout() {
            localStorage.removeItem('proffessionalToken');
            this.$router.push('/');
        }
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
    padding: 0.5em 1em;
}
</style>
