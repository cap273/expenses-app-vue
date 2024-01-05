import { createRouter, createWebHistory } from 'vue-router';
import Login from './components/Login.vue';
import Hero from './components/Hero.vue';
import Signup from './components/Signup.vue';
import InputExpenses from './components/InputExpenses.vue';
import ViewExpenses from './components/ViewExpenses.vue';

const routes = [
  {
    path: '/',
    name: 'Hero',
    component: Hero,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Hero, //placeholder
  },
  {
    path: '/signup',
    name: 'Signup',
    component: Signup,
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
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
