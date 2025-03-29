<template>
  <div class="d-flex h-100 justify-content-center align-items-center">
    <div class="card m-5">
      <div class="card-header text-center">Welcome to the World of Services</div>
      <div class="card-body d-flex justify-content-center flex-column align-items-center">
        <h5 class="card-title mb-4">Choose your Role:</h5>
        
        <blockquote class="blockquote mb-0">
          <router-link to="/admin-login" class="btn btn-primary me-2 mb-2">Admin</router-link>
          <router-link to="/customer-login" class="btn btn-success me-2 mb-2">Customer</router-link>
          <router-link to="/proffessional-login" class="btn btn-info me-2 mb-2">Proffessional</router-link>
          
        </blockquote>
      </div>
    </div>
  </div>
</template>

<script>export default {
    name: 'HomeView',
};
</script>
