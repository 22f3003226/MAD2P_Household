<template>
    <div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">Admin Login</div>
                <div class="card-body">
                    <form @submit.prevent="loginAdmin">
                        <div class="form-group">
                            <label for="email">Username:</label>
                            <input type="text" class="form-control" id="username" v-model="username" required>
                        </div>
                        <br>
                        <div class="form-group">
                            <label for="password">Password</label>
                            <input type="password" class="form-control" id="password" v-model="password" required>
                            <br>
                            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
                        </div>
                        <br>
                        <button type="submit" class="btn btn-primary">Login</button>
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
        async loginAdmin() {
            this.errorMessage = null;
            const payload = {
                username: this.username,
                password: this.password,
            };
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                });
                const data = await response.json();
                if (response.ok){
                    alert('Login successful!');
                    localStorage.setItem('adminToken', data.token);
                    this.$router.push('/admin-dashboard');
                } else {
                    this.errorMessage = data.message || 'An error occurred while logging in.';
                }
            } catch (error) {
                this.errorMessage = "Unable to connect to the server. Please try again later.";
            }
        },
    },
};
</script>