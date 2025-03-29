<template>
    <div>
        <nav class="navbar bg-dark border-bottom border-body" data-bs-theme="dark">
            <div class="container-fluid">
                <div class="d-flex align-items-center">
                    <a class="navbar-brand me-3" href="#">Create Service Request</a>
                    <router-link to="/customer-dashboard" class="btn btn-sm btn-primary">Back to Dashboard</router-link>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title mb-4">New Service Request</h5>
                    <form @submit.prevent="createRequest">
                        <div class="mb-3">
                            <label class="form-label">Service Name</label>
                            <input type="text" class="form-control" :value="service.service_name" readonly>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Base Price</label>
                            <input type="text" class="form-control" :value="'₹' + service.base_price" readonly>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Time Required</label>
                            <input type="text" class="form-control" :value="service.time_required" readonly>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Select Professional</label>
                            <select class="form-select" v-model="selectedProfessional" required>
                                <option value="">Choose a professional...</option>
                                <option v-for="prof in professionals" 
                                        :key="prof.id" 
                                        :value="prof.user_name">
                                    {{ prof.user_name }}
                                </option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Request Description</label>
                            <textarea class="form-control" 
                                      v-model="requestDescription" 
                                      rows="3" 
                                      required
                                      placeholder="Describe your service request..."></textarea>
                        </div>

                        <button type="submit" class="btn btn-primary">Create Request</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            service: {
                service_name: '',
                base_price: '',
                time_required: '',
                service_description: ''
            },
            professionals: [],
            selectedProfessional: '',
            requestDescription: ''
        }
    },
    methods: {
        async fetchServiceDetails() {
            try {
                const response = await fetch(`/api/get_request/${this.$route.params.serviceId}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('customerToken')}`
                    }
                });
                const data = await response.json();
                console.log('Service data:', data); // Debug log
                if (response.ok) {
                    this.service = data.service;
                    this.professionals = data.professionals;
                } else {
                    alert(data.message || 'Error fetching service details');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error connecting to server');
            }
        },
        async createRequest() {
            if (!this.selectedProfessional) {
                alert('Please select a professional');
                return;
            }

            try {
                const response = await fetch(`/api/create_request/${this.$route.params.serviceId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('customerToken')}`
                    },
                    body: JSON.stringify({
                        service_proffessional_name: this.selectedProfessional,
                        request_description: this.requestDescription
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    alert('Service request created successfully!');
                    this.$router.push('/customer-dashboard');
                } else {
                    alert(data.message || 'Error creating request');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error creating request');
            }
        }
    },
    mounted() {
        this.fetchServiceDetails();
    }
}
</script>

