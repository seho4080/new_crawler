import "@/assets/scss/main.scss";
import { createApp } from "vue";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import App from "@/App.vue";
import router from "@/router";
import { createPinia } from "pinia";
import axios from "axios";

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

// 새로고침하더라도 로그인 세션 유지하도록 설정
const token = localStorage.getItem('access_token');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

app.use(pinia);
app.use(router);

app.mount("#app");
