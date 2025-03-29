import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/components/HomeView.vue';
import AdminLogin from '@/components/AdminLogin.vue';
import CustomerLogin from '@/components/CustomerLogin.vue';
import ProffessionalLogin from '@/components/ProffessionalLogin.vue';
import ProffessionalSignup from '@/components/ProffessionalSignup.vue';
import CustomerSignup from '@/components/CustomerSignup.vue';
import AdminDashboard from '@/components/AdminDashboard.vue';
import CreateService from '@/components/CreateService.vue';
import ServiceproffessionalDashboard from '@/components/ServiceproffessionalDashboard.vue';
import ServiceCustomerDashboard from '@/components/CustomerDashboard.vue';
import CreateServiceRequest from '../components/CreateServiceRequest.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/admin-login',
      name: 'admin-login',
      component: AdminLogin,
    },
    {
      path: '/customer-login',
      name: 'customer-login',
      component: CustomerLogin,
    },
    {
      path: '/proffessional-login',
      name: 'proffessional-login',
      component: ProffessionalLogin,
    },
    {
      path: '/proffessional-signup',
      name: 'proffessional-signup',
      component: ProffessionalSignup,
    },
    {
      path: '/customer-signup',
      name: 'customer-signup',
      component: CustomerSignup,
    },
    {
      path: '/admin-dashboard',
      name: 'admin-dashboard',
      component: AdminDashboard,
      //meta: {
        //requiresAuth: true,
      //},
    },
    {
      path: '/create-service',
      name: 'create-service',
      component: CreateService,
    },
    {
      path: '/serviceproffessional-dashboard',
      name: 'serviceproffessional-dashboard',
      component: ServiceproffessionalDashboard,
    },
    {
      path: '/customer-dashboard',
      name: 'customer-dashboard',
      component: ServiceCustomerDashboard,
    },
    {
      path: '/create-service-request/:serviceId',
      name: 'create-service-request',
      component: CreateServiceRequest,
    },
    {
      path: '/summary',
      name: 'summary',
      component: () => import('../components/Summary.vue')
  }
  ],
})

export default router
