<template>
    <div>
        <v-container class="pt-5">
            <v-row justify="center">
                <v-col cols="12" sm="8" md="6" class="text-center">
                    <h2 class="header-text">Welcome back!</h2>
                    <p class="subheader-text">Enter your credentials to log in</p>
                </v-col>
            </v-row>
        </v-container>
        <Login/>
        <v-container>
        <v-row justify="center">
            <v-col cols="12" sm="8" md="6" class="d-flex justify-center">
                <v-btn
                    text
                    class="signup-btn mt-5"
                    @click="$router.push('/signup')"
                >
                I don’t have an account
                </v-btn>
            </v-col>
        </v-row>
        </v-container>
    </div>
</template>
  
<script>
import Login from '@/components/Login.vue';

export default {
    components: { Login },
};
</script>

<style scoped>
.header-text {
  font-size: 1.5em; /* Adjust as needed */
  font-weight: normal;
}

.subheader-text {
  font-size: 1em;
  font-weight: normal;
}
</style>
  