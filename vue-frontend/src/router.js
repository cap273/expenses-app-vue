import { createRouter, createWebHistory } from 'vue-router';
import LoginWithSignup from '@/views/LoginWithSignup.vue';
import Hero from './components/Hero.vue';
import SignUpWithLogin from '@/views/SignUpWithLogin.vue';
import InputExpenses from './components/InputExpenses.vue';
import ViewExpenses from './components/ViewExpenses.vue';
import Profile from '@/components/Profile.vue';
import HouseholdSettings from '@/components/HouseholdSettings.vue';
import PlaidDashboard from '@/views/PlaidDashboard.vue';
import Overview from '@/components/Overview.vue';
import Onboarding from './components/Onboarding.vue';

const routes = [
  {
    path: '/',
    name: 'Hero',
    component: Hero,
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginWithSignup,
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Hero, //placeholder
  },
  {
    path: '/signup',
    name: 'Signup',
    component: SignUpWithLogin,
  },
  {
    path: '/view_expenses',
    name: 'ViewExpenses',
    component: ViewExpenses,
  },
  {
    path: '/input_expenses',
    name: 'InputExpenses',
    component: InputExpenses,
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true },
  },
  {
    path: '/household',
    name: 'HouseholdSettings',
    component: HouseholdSettings,
    meta: { requiresAuth: true },
  },
  {
    path: '/plaid',
    name: 'PlaidDashboard',
    component: PlaidDashboard,
  },
  {
    path: '/overview',
    name: 'Overview',
    component: Overview,
    meta: { requiresAuth: true },
  },
  {
    path: '/onboarding',
    name: 'Onboarding',
    component: Onboarding,
    meta: { requiresAuth: true }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;