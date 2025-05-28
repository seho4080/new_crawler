<template>
  <div class="login-container">
    <form @submit.prevent="handleLogin">
      <input
        type="username"
        v-model="username"
        placeholder="ID"
        required
      />
      <input
        type="password"
        v-model="password"
        placeholder="PASSWORD"
        required
      />
      <button type="submit">로그인</button>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>
    </form>
    <div class="register-container">
      <p>아직 회원이 아니신가요?  <button @click="register">회원 가입</button></p>
    </div>
    
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const router = useRouter();
const refresh = ref('')
const access = ref('')

const handleLogin = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/members/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      })
    })

    if (!response.ok) {
      errorMessage.value = "로그인 실패: " + response.status;
      return;
    }

    const data = await response.json()
    
    access.value = data.access
    refresh.value = data.refresh

    // 1. localStorage에 토큰 저장
    localStorage.setItem('access_token', access.value);
    localStorage.setItem('refresh_token', refresh.value);

    // 2. axios 기본 Authorization 설정
    axios.defaults.headers.common['Authorization'] = `Bearer ${access.value}`;
    
    alert("로그인 성공!");

    // 3. 페이지 이동
    router.replace('/');
    } catch (error) {
    errorMessage.value = '아이디 또는 비밀번호가 올바르지 않습니다.';
    alert(errorMessage.value)
  }
};

const register = () => {
  router.replace('/register')
}

</script>

<style scoped>
/* 페이지 배경과 기본 폰트는 전역에 이미 적용되어 있다고 가정합니다 */

/* 로그인 박스 */
.login-container {
  max-width: 360px;
  margin: 80px auto;
  padding: 2rem;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* form 내부 레이아웃 */
.login-container form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 입력창 스타일 */
.login-container input {
  padding: 0.75rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  color: #333333;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.login-container input:focus {
  outline: none;
  border-color: #001f3f;
  box-shadow: 0 0 0 2px rgba(0, 31, 63, 0.2);
}

/* 로그인 버튼 */
.login-container button[type="submit"] {
  background-color: #001f3f;
  color: #ffffff;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.login-container button[type="submit"]:hover {
  background-color: #003060;
}

/* 에러 메시지 */
.login-container .error {
  color: #e53935;
  font-size: 0.875rem;
  margin-top: -0.5rem;
}

/* 회원가입 영역 */
.register-container {
  margin-top: 1.5rem;
  text-align: center;
}

.register-container p {
  font-size: 0.9rem;
  color: #555555;
}

.register-container button {
  background: none;
  border: none;
  padding: 0;
  margin-left: 0.3rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: #001f3f;
  text-decoration: underline;
  cursor: pointer;
  transition: color 0.2s;
}

.register-container button:hover {
  color: #003060;
}
</style>
