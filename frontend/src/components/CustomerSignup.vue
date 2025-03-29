<template>
    <div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">Customer Signup</div>
                <div class="card-body">
                    <form @submit.prevent="signupCustomer">
                        <div class="form-group">
                            <label for="username">Username:</label>
                            <input type="text" class="form-control" id="username" v-model="username" required>
                        </div>
                        <br>
                        <div class="form-group">
                            <label for="password">Password</label>
                            <input type="password" class="form-control" id="password" v-model="password" required>
                        </div><br>
                        <div class="form-group">
                            <label for="address">Address</label>
                            <input type="text" class="form-control" id="address" v-model="address" required>
                        </div>
                        <br><div class="form-group">
                            <label for="pincode">Pincode</label>
                            <input type="number" class="form-control" id="pincode" v-model="pincode" required>
                        </div>
                        <br>
                            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
                            <!-- <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div> -->
                        <br>
                        <button type="submit" class="btn btn-primary">Sign Up</button>
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
            username: '',
            password: '',
            errorMessage: null,
        };
    },
    methods: {
        async signupCustomer() {
            this.errorMessage = null;
            //this.successMessage = null;
            const payload = {
                username: this.username,
                password: this.password,
                address: this.address,
                pincode: this.pincode,
                role: 'customer',
            };
            try {
                const response = await fetch('/api/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                });
                const data = await response.json();
                if (response.ok){
                    //this.successMessage = data.message;
                    alert(data.message);
                    this.$router.push('/customer-login');
                } else {
                    this.errorMessage = data.message || 'An error occurred while signing up.';
                }
            } catch (error) {
                this.errorMessage = "Unable to connect to the server. Please try again later.";
            }
        },
    },
};
</script>

