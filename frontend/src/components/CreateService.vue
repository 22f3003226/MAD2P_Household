<template>
    <div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">Create Service</div>
                <div class="card-body">
                    <form @submit.prevent="createService">
                        <div class="form-group">
                            <label for="service_name">Service Name</label>
                            <input type="text" class="form-control" id="service_name" v-model="service_name" required>
                        </div>
                        <br>
                        <div class="form-group">
                            <label for="service_description">Service Description</label>
                            <input type="service_description" class="form-control" id="service_description" v-model="service_description" required>
                        </div><br>
                        <div class="form-group">
                            <label for="base_price">Base Price</label>
                            <input type="text" class="form-control" id="base_price" v-model="base_price">
                        </div>
                        <br><div class="form-group">
                            <label for="time_required">Time Required</label>
                            <input type="text" class="form-control" id="time_required" v-model="time_required" required>
                        </div>
                        <br>
                            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
                            <!-- <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div> -->
                        <br>
                        <button type="submit" class="btn btn-primary">Create Service</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
</template>

<script>export default {
    data() {
        return {
            service_name: '',
            service_description: '',
            base_price: '',
            time_required: '',
            errorMessage: null,
        };
    },
    methods: {
        async createService() {
            this.errorMessage = null;
            //this.successMessage = null;
            const payload = {
                service_name: this.service_name,
                service_description: this.service_description,
                base_price: this.base_price,
                time_required: this.time_required,
            };
            try {
                const response = await fetch('/api/service', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
                    },
                    body: JSON.stringify(payload),
                });
                const data = await response.json();
                if (response.ok){
                    //this.successMessage = data.message;
                    alert(data.message);
                    this.$router.push('/admin-dashboard');
                } else {
                    this.errorMessage = data.message || 'An error occurred while creating service.';
                }
            } catch (error) {
                this.errorMessage = "Unable to connect to the server. Please try again later.";
            }
        },
    },
};
</script>

