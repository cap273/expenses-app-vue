<template>
    <div>
        <v-container class="pt-5">
            <v-row justify="center">
                <v-col cols="12" sm="8" md="6" class="text-center">
                    <h2 class="header-text">Create an account</h2>
                    <p class="subheader-text">Choose a username, enter your email, and enter a password</p>
                </v-col>
            </v-row>
        </v-container>
        <Signup/>
        <v-container>
        <v-row justify="center">
            <v-col cols="12" sm="8" md="6" class="d-flex justify-center">
                <v-btn
                    color="primary"
                    class="mt-5"
                    @click="$router.push('/login')"
                >
                I already have an account
                </v-btn>
            </v-col>
        </v-row>
        </v-container>
    </div>
</template>
  
<script>
import Signup from '@/components/Signup.vue';

export default {
    components: { Signup },
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
  