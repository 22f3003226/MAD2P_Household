<template>
    <div>
        <nav class="navbar bg-dark border-bottom border-body" data-bs-theme="dark">
            <div class="container-fluid">
                <div class="d-flex align-items-center justify-content-between w-100">
                    <div class="d-flex align-items-center">
                        <a class="navbar-brand me-3" href="#">Summary Dashboard</a>
                        <router-link :to="getDashboardRoute" class="btn btn-sm btn-primary me-2">Back to Dashboard</router-link>
                        <a class="btn btn-sm btn-primary" @click="logout">Logout</a>
                    </div>
                </div>
            </div>
        </nav>

        <!-- Admin Summary Section -->
        <div v-if="userRole === 'admin'" class="container mt-4">
            <div class="row">
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">User Statistics</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-flex justify-content-between mb-3">
                                <span>Total Customers:</span>
                                <span class="badge bg-primary">{{ summaryData.customer_count || 0 }}</span>
                            </div>
                            <div class="d-flex justify-content-between">
                                <span>Total Service Professionals:</span>
                                <span class="badge bg-success">{{ summaryData.service_professional_count || 0 }}</span>
                            </div>
                            <div class="mt-4">
                                <img src="../assets/image_1.png" alt="Users by Role" class="img-fluid">
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Request Statistics</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Pending Requests:</span>
                                    <span class="badge bg-warning">{{ summaryData.request_counts?.pending || 0 }}</span>
                                </div>
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Accepted Requests:</span>
                                    <span class="badge bg-success">{{ summaryData.request_counts?.accepted || 0 }}</span>
                                </div>
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Rejected Requests:</span>
                                    <span class="badge bg-danger">{{ summaryData.request_counts?.rejected || 0 }}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Closed Requests:</span>
                                    <span class="badge bg-secondary">{{ summaryData.request_counts?.closed || 0 }}</span>
                                </div>
                            </div>
                            <div class="mt-4">
                                <img src="../assets/image_2.png" alt="Requests by Status" class="img-fluid">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Customer Summary Section -->
        <div v-if="userRole === 'customer'" class="container mt-4">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">My Service Request Statistics</h5>
                </div>
                <div class="card-body">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <img src="../assets/image_3.png" alt="My Requests by Status" class="img-fluid">
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Professional Summary Section -->
        <div v-if="userRole === 'service_proffessional'" class="container mt-4">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">My Service Request Statistics</h5>
                </div>
                <div class="card-body">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <img src="../assets/image_4.png" alt="My Requests by Status" class="img-fluid">
                        </div>
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
            userRole: '',
            summaryData: {},
            token: ''
        }
    },
    computed: {
        getDashboardRoute() {
            switch(this.userRole) {
                case 'admin':
                    return '/admin-dashboard';
                case 'customer':
                    return '/customer-dashboard';
                case 'service_proffessional':
                    return '/serviceproffessional-dashboard';
                default:
                    return '/';
            }
        }
    },
    methods: {
        async fetchSummary() {
            try {
                // Get token based on what's available
                this.token = localStorage.getItem('adminToken') || 
                           localStorage.getItem('customerToken') || 
                           localStorage.getItem('proffessionalToken');

                if (!this.token) {
                    this.$router.push('/');
                    return;
                }

                const response = await fetch('/api/summary', {
                    headers: {
                        'Authorization': `Bearer ${this.token}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                if (response.ok) {
                    this.summaryData = data.data;
                    // Role comes from the backend response
                    this.userRole = data.role;
                } else {
                    alert(data.message || 'Error fetching summary data');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error connecting to server');
            }
        },
        logout() {
            if (this.userRole === 'admin') localStorage.removeItem('adminToken');
            else if (this.userRole === 'customer') localStorage.removeItem('customerToken');
            else if (this.userRole === 'service_proffessional') localStorage.removeItem('proffessionalToken');
            this.$router.push('/');
        }
    },
    created() {
        this.fetchSummary();
    }
}
</script>

<style scoped>
.card {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
}
.card:hover {
    transform: translateY(-5px);
}
.badge {
    font-size: 1rem;
    padding: 0.5em 1em;
}
.img-fluid {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin-top: 1rem;
}
</style>