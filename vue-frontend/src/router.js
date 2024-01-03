import { createRouter, createWebHistory } from 'vue-router';
import Login from './components/Login.vue';
import Hero from './components/Hero.vue';

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
  // Add more routes as needed
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
