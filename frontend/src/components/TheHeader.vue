<script setup>
import { RouterLink, useRouter } from "vue-router";
import { ref, onMounted } from "vue";


const isLogin = ref(false);

const router = useRouter();

onMounted(() => {
  const token = localStorage.getItem("access_token");
  isLogin.value = !!token;
})

const logout = () => {
  localStorage.removeItem("access_token");
  isLogin.value = false;
  delete axios.default.headers.common['Authorization']
  router.push("/");
}

const refreshPage = (event) => {
  event.preventDefault();
  router.push("/").then(() => {
    window.location.reload();
  });
};
</script>

<template>
  <div class="header__container">
    <header>
      <router-link to="/" @click="refreshPage">
        <span class="logo"> SSAFYNEWS </span>
      </router-link>

      <nav class="menus">
        <router-link to="/news">나만의 뉴스 큐레이팅</router-link>
        <router-link to="/dashboard">대시보드</router-link>
        <template v-if="isLogin">
          <button @click="logout">로그아웃</button>
        </template>
        <template v-else>
          <router-link to="/login">로그인</router-link>
        </template>
      </nav>
    </header>
  </div>
</template>

<style scoped lang="scss">
.header__container {
  background-color: white;
  border-bottom: 1px solid #d4d4d4;
  header {
    max-width: 1280px;
    margin: 0 auto;
    color: black;
    height: 80px;
    justify-content: space-between;
    align-items: center;
    display: flex;
    padding: 0 15px;
  }

  .logo {
    font-size: x-large;
    font-weight: 800;
  }

  .menus {
    display: flex;
    align-items: center;
    gap: 23px;
  }

  a.router-link-active {
    font-weight: bold;
  }
}
</style>
